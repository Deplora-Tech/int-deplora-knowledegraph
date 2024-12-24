
async def searchFromNode(self, value, type):
    """
    Search for a node in the Neo4j database by value and type.
    """
    records, summary, keys = await self.driver.execute_query(
    f"""
    MATCH (n:{type} {{name: $value}})-[r]->(connected)
    RETURN elementId(connected) AS connectedId, 
           connected.name AS connectedName, 
           type(r) AS relationshipType, 
           r.weight AS weight
    """,
    value=value,
    database_=self.database,
    )


    if records:
        print(f"Found {len(records)} nodes with value: {value} and type: {type}")
        formatted_records = [[record["connectedName"], record["relationshipType"], record["weight"]] for record in records]
        return formatted_records
    else:
        print(f"No node found with value: {value} and type: {type}")
        return None
    