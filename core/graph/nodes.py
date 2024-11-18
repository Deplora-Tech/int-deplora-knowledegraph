async def add_user_node(self, id, organization):
    """
    Add a new user to the Neo4j database if they don't already exist and return the node ID.
    """

    records, summery, keys = await self.driver.execute_query(
        """
        MERGE (u:User {userid: $id})
        ON CREATE SET u.organization = $organization
        RETURN elementId(u) AS uid
        """,
        id=id,
        organization=organization,
        database_=self.database,
    )

    id = records[0]["uid"]

    return id
