
import asyncio
from core.contextGaph import ContextGraph
import pandas as pd

async def main():
    uri = "neo4j://localhost:7687"  # Replace with your Neo4j URI
    context_graph = ContextGraph()
    
    await context_graph.setup(uri)
    
    # username = "Alice2"
    # organization = "Wonderland2"
    # uid = await context_graph.add_user(username, organization)

    # a = await context_graph.update(username, "Lambda function is returning a throttling error. Adjust the concurrency limit to handle increased requests, optimize code to improve performance, and monitor costs.")
    # print(a)
    
    filepath = "./entity_extraction_150-gr-70b.csv"
    df = pd.read_csv(filepath)
    
    for index, row in df.iterrows():
        username = row["User"]
        
        if username != "User 3":
            continue
        
        prompt = row["Prompt"]
        print(prompt)
        
        await context_graph.add_user(username, "Organization")
        a = await context_graph.update(username, prompt)
        
        
    
asyncio.run(main())
