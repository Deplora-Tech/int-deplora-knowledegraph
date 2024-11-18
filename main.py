
import asyncio
from core.contextGaph import ContextGraph


async def main():
    uri = "neo4j://localhost:7687"  # Replace with your Neo4j URI
    context_graph = ContextGraph()
    
    await context_graph.setup(uri)
    
    username = "Alice"
    organization = "Wonderland"
    uid = await context_graph.add_user(username, organization)

    a = await context_graph.update(uid, "Lambda function is returning a throttling error. Adjust the concurrency limit to handle increased requests, optimize code to improve performance, and monitor costs.")
    # print(a)
asyncio.run(main())
