import os
import json

from .graph.manage import setup
from .graph.users import add_user
from core.update.extract_entities import extract_entities_and_relationships, clean_extracted_entities

class ContextGraph:
    def __init__(self):
        """
        Initialize the class variables.
        """
        self.database = "neo4j"
        self.driver = None
        
    async def setup(self, uri):
        """
        Asynchronously setup the Neo4j driver.
        """
        self.driver = await setup(uri)
    
    async def add_user(self, name, organization):
        """
        Add a new user to the neo4j database.
        """
        return await add_user(self, name, organization)
        
            
            
            
    async def update(self, user, prompt):
        entities = await extract_entities_and_relationships(prompt)
        cleaned_entities = await clean_extracted_entities(entities, prompt)
        
        self.pprint(cleaned_entities)
        
        return cleaned_entities
    
    
    def pprint(self, js):
        print(json.dumps(js, indent=4))
