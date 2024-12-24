from fastapi import FastAPI, Query
from pydantic import BaseModel
import asyncio
from core.contextGaph import ContextGraph

# Initialize FastAPI app
app = FastAPI()

# Instantiate the ContextGraph class
context_graph = ContextGraph()


# Define the setup route for initialization
@app.on_event("startup")
async def setup_context_graph():
    uri = "neo4j://localhost:7687"  # Replace with your Neo4j URI
    await context_graph.setup(uri)


# Define the route to search the context graph
@app.get("/search")
async def search_context(
    username: str = Query(..., description="Username to search for"),
    project: str = Query(..., description="Project to search for"),
    organization: str = Query(..., description="Organization to search for"),
):
    try:
        result = await context_graph.search(username, project, organization)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/update")
async def update_context(
    username: str = Query(..., description="Username to search for"),
    project: str = Query(..., description="Project to search for"),
    organization: str = Query(..., description="Organization to search for"),
    prompt: str = Query(..., description="Prompt to update the context graph"),
):
    try:
        result = await context_graph.update(
            username, project, organization, prompt
        )
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Define a shutdown event to close resources
# @app.on_event("shutdown")
# async def shutdown_context_graph():
#     await context_graph.close()
