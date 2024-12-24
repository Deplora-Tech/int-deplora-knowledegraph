from utils.utils import replace_special_characters

class EdgeManager:
    def __init__(self, driver, embedding_manager, database):
        self.driver = driver
        self.embedding_manager = embedding_manager
        self.database = database

    async def add_relationship(self, source, target, relationship, source_type, target_type, is_positive=True, weighted=True):
        multiplier = 0.1 if weighted else 0

        relationship = replace_special_characters(relationship)

        relationship_embedding = (
            self.embedding_manager.calculate_embedding(relationship) if weighted else None
        )

        similarity_query = f"""
        MATCH (s:{source_type} {{name: $sourceName}})-[r]->(t:{target_type} {{name: $targetName}})
        WHERE type(r) = $relationship
        """ + (
            """
            AND r.embedding IS NOT NULL
            WITH r, gds.similarity.cosine(r.embedding, $relationship_embedding) AS similarity
            WHERE similarity > 0.8
            """ if weighted else "") + """
        RETURN r.weight AS currentWeight, elementId(r) AS edgeId, type(r) AS relationship
        LIMIT 1
        """

        similar_records, _, _ = await self.driver.execute_query(
            similarity_query,
            sourceName=source,
            targetName=target,
            relationship=relationship,
            relationship_embedding=relationship_embedding,
            database_=self.database,
        )

        if similar_records:
            edge_id = similar_records[0]["edgeId"]

            if weighted:
                current_weight = similar_records[0]["currentWeight"]
                new_weight = (
                    current_weight + (1 - current_weight) * multiplier
                    if is_positive
                    else current_weight - current_weight * multiplier
                )
                update_query = """
                MATCH ()-[r]->()
                WHERE elementId(r) = $edgeId
                SET r.weight = $new_weight
                RETURN r
                """
                await self.driver.execute_query(
                    update_query,
                    edgeId=edge_id,
                    new_weight=new_weight,
                    database_=self.database,
                )
                return {"status": "edge_updated", "edge_id": edge_id, "new_weight": new_weight}
            return {"status": "edge_exists", "edge_id": edge_id}

        initial_weight = 0.5 + (multiplier if is_positive else -multiplier) if weighted else None

        add_edge_query = f"""
        MATCH (s:{source_type} {{name: $source}})
        MATCH (t:{target_type} {{name: $target}})
        MERGE (s)-[r:{relationship}]->(t)
        """ + (
            """
            SET r.weight = $initial_weight,
                r.embedding = $relationship_embedding
            """ if weighted else "") + """
        RETURN elementId(r) AS edgeId
        """

        params = {
            "source": source,
            "target": target,
            "relationship_embedding": relationship_embedding,
            "initial_weight": initial_weight,
        }

        new_edge_records, _, _ = await self.driver.execute_query(
            add_edge_query, **{k: v for k, v in params.items() if v is not None}, database_=self.database
        )

        new_edge_id = new_edge_records[0]["edgeId"]
        return {"status": "new_edge_added", "edge_id": new_edge_id, "initial_weight": initial_weight}

    async def add_entity_user_edge(self, user, entity, relationship, is_positive=True):
        return await self.add_relationship(
            source=user,
            target=entity,
            relationship=relationship,
            source_type="User",
            target_type="Entity",
            is_positive=is_positive,
            weighted=True,
        )

    async def add_organization_entity_edge(self, organization, entity, relationship, is_positive=True):
        return await self.add_relationship(
            source=organization,
            target=entity,
            relationship=relationship,
            source_type="Organization",
            target_type="Entity",
            weighted=True,
            is_positive=is_positive,
        )

    async def add_project_entity_edge(self, project, entity, relationship, is_positive=True):
        return await self.add_relationship(
            source=project,
            target=entity,
            relationship=relationship,
            source_type="Project",
            target_type="Entity",
            weighted=True,
            is_positive=is_positive,
        )

    # async def add_user_organization_edge(self, user, organization, relationship):
    #     return await self.add_relationship(
    #         source=user,
    #         target=organization,
    #         relationship=relationship,
    #         source_type="User",
    #         target_type="Organization",
    #         weighted=False,
    #     )

    # async def add_user_project_edge(self, user, project, relationship):
    #     return await self.add_relationship(
    #         source=user,
    #         target=project,
    #         relationship=relationship,
    #         source_type="User",
    #         target_type="Project",
    #         weighted=False,
    #     )

    # async def add_organization_project_edge(self, organization, project, relationship):
    #     return await self.add_relationship(
    #         source=organization,
    #         target=project,
    #         relationship=relationship,
    #         source_type="Organization",
    #         target_type="Project",
    #         weighted=False,
    #     )