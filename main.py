
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
    
    # filepath = "./entity_extraction_150-gr-70b.csv"
    # df = pd.read_csv(filepath)
    
    # for index, row in df.iterrows():
    #     username = row["User"]
    #     project = row["Project"]        
    #     prompt = row["Prompt"]
    #     organization = row["Organization"]
    #     print(prompt)
        
    #     try:
    #         a = await context_graph.update(username, project, organization, prompt)
        
    #     except Exception as e:
    #         print(e)
    #         print("Error in updating context graph")
        
    #     # if index == 10:
    #     #     break
    print("Searching")
    x = await context_graph.search("User 1", "Project 1", "Org1")
    print(x)
        
        
    
asyncio.run(main())
