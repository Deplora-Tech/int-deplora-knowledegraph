import os
import json
import asyncio
import math

from .embedings.embedingManager import EmbeddingManager
from .graph.manage import setup
from .graph.nodes import (
    add_user_node,
    add_entity_node,
    add_project_node,
    add_organization_node,
)
from .graph.edges import EdgeManager
from .update.extract_entities import (
    extract_entities_and_relationships,
    clean_extracted_entities,
)
from .graph.search import searchFromNode


class ContextGraph:
    def __init__(self):
        """
        Initialize the class variables.
        """
        self.database = "neo4j"
        self.driver = None
        self.embeding_manager = EmbeddingManager("all-MiniLM-L6-v2")
        self.edge_manager = None

    async def setup(self, uri):
        """
        Asynchronously setup the Neo4j driver.
        """
        driver = await setup(uri)
        if driver:
            self.driver = driver
            self.edge_manager = EdgeManager(
                self.driver, self.embeding_manager, self.database
            )
            print("Neo4j driver setup successfully.")
        else:
            print("Failed to setup Neo4j driver.")

            raise Exception("Failed to setup Neo4j driver.")

    async def update(self, user, project, organization, prompt):
        entities = await extract_entities_and_relationships(prompt)
        # cleaned_entities = await clean_extracted_entities(entities, prompt)
        cleaned_entities = entities
        
        await asyncio.gather(
            add_user_node(self, user),
            add_project_node(self, project),
            add_organization_node(self, organization),
        )

        await self.add_entities(user, project, organization, cleaned_entities)

    async def search(self, user, project, organization):
        userPrefereces = await searchFromNode(self, user, "User")
        projectPreferences = await searchFromNode(self, project, "Project")
        organizationPreferences = await searchFromNode(
            self, organization, "Organization"
        )
        weights = [3, 2, 1]  # Project, User, Organization
        preferenceDict = {}

        for pi, preferenceSet in enumerate(
            [projectPreferences, userPrefereces, organizationPreferences]
        ):
            for preference in preferenceSet:
                if preference[1] in preferenceDict:
                    if preference[0] in preferenceDict[preference[1]]:
                        preferenceDict[preference[1]][preference[0]][pi] = (
                            preference[2] * weights[pi]
                        )

                    else:
                        ps = [0, 0, 0]
                        ps[pi] = preference[2] * weights[pi]
                        preferenceDict[preference[1]][preference[0]] = ps

                else:
                    ps = [0, 0, 0]
                    ps[pi] = preference[2] * weights[pi]
                    preferenceDict[preference[1]] = {preference[0]: ps}

        positivePreferences = []
        negativePreferences = []

        user_preference_scale = ["Low", "Moderate", "High", "Very High", "Extreme"]

        for preference in preferenceDict:
            maxVal = 0
            maxEntity = list(preferenceDict[preference].keys())[0]
            for entity in preferenceDict[preference]:
                nonzero_weights = [
                    weights[w]
                    for w in range(len(preferenceDict[preference][entity]))
                    if preferenceDict[preference][entity][w] != 0
                ]
                val = sum(preferenceDict[preference][entity]) / sum(nonzero_weights)

                if val > maxVal:
                    maxVal = val
                    maxEntity = entity

            if maxVal >= 0.6:
                preference_level = user_preference_scale[math.floor(maxVal * 10) - 6]
                positivePreferences.append(
                    [preference, maxEntity, maxVal, preference_level]
                )
            elif maxVal <= 0.4:
                preference_level = user_preference_scale[4 - math.floor(maxVal * 10)]
                negativePreferences.append(
                    [preference, maxEntity, maxVal, preference_level]
                )

        # take the best 1/m of the positive and negative preferences
        m = 3
        sorted_positivePreferences = sorted(
            positivePreferences, key=lambda x: x[2], reverse=True
        )[: int(len(positivePreferences) / m)]
        sorted_negativePreferences = sorted(negativePreferences, key=lambda x: x[2])[
            : int(len(negativePreferences) / m)
        ]

        # Combine into a dictionary
        user_preferences = {
            "positive_preferences": [
                [pref[0], pref[1], pref[2], pref[3]]
                for pref in sorted_positivePreferences
            ],
            "negative_preferences": [
                [pref[0], pref[1], pref[2], pref[3]]
                for pref in sorted_negativePreferences
            ],
        }

        return user_preferences

    async def add_entities(self, user, project, organization, cleaned_entities):
        for entity in cleaned_entities.get("Entities", []):
            res = await add_entity_node(self, entity)
            isPositive = (
                cleaned_entities["Entities"][entity]["relationship"] == "positive"
            )

            entity_type = cleaned_entities["Entities"][entity]["type"]

            if res.get("status") == "similar_found":
                print(
                    f"Similar node found for {entity}: {res['similar_node']} with similarity score {res['similarity_score']}"
                )
                target_entity = res["similar_node"]
            else:
                target_entity = entity

            # Use asyncio.gather to handle all tasks concurrently
            await asyncio.gather(
                self.edge_manager.add_entity_user_edge(
                    user, target_entity, entity_type, isPositive
                ),
                self.edge_manager.add_organization_entity_edge(
                    organization, target_entity, entity_type, isPositive
                ),
                self.edge_manager.add_project_entity_edge(
                    project, target_entity, entity_type, isPositive
                ),
            )

    def pprint(self, js):
        print(json.dumps(js, indent=4))
