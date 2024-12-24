import json
from core.llm_interface.chat_groq import invoke_groq


async def extract_entities_and_relationships(prompt):
    """
    Extracts and cleans relevant entities, relationships, and constraints dynamically.
    Filters out meaningless entities such as generic terms or unqualified metrics.
    """
    system_prompt = """
        You are an intelligent entity extraction engine. Your job is to:
        1. Analyze the user’s input.
        2. Identify **only** the named, specific services or solutions (e.g., 'RDS', 'EC2', 'S3', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'EKS', 'ECS', etc.).
            - **Exclude** constraints or best practices (e.g., 'no downtime', 'enable autoscaling', 'slow queries', 'instance size').
            - **Exclude** generic terms like 'application', 'service', 'system', 'database', 'queries', etc., unless they are explicitly tied to a specifically named service.
        3. For each service identified, assign a **meaningful EntityType**:
            - 'RDS' → 'DatabaseService'
            - 'EC2' → 'ComputeService'
            - 'S3' → 'ObjectStorageService'
            - 'AWS', 'GCP', 'Azure' → 'CloudProvider'
            - 'Docker' → 'ContainerPlatform'
            - 'Kubernetes', 'EKS', 'ECS' → 'ContainerOrchestrationPlatform'
            - If no suitable predefined category exists, use 'OtherService'.
        4. Determine the **relationship** based on context:
            - 'positive' if the user wants to deploy, use, enable, or set up the service.
            - 'negative' if the user wants to avoid, remove, or disable the service.
        5. Return the result in **JSON** with the following format:

        \"\"\"
        {
        "Entities": {
            "serviceName": {
            "type": "<EntityType>",
            "relationship": "<positive | negative>"
            },
            "serviceName2": {
            "type": "<EntityType>",
            "relationship": "<positive | negative>"
            }
            ...
        }
        }
        \"\"\"

        Example usage:
        User Prompt: 'Use EC2 and RDS. Do not use Docker.'
        Expected Response:
        \"\"\"
        {
        "Entities": {
            "EC2": {
            "type": "ComputeService",
            "relationship": "positive"
            },
            "RDS": {
            "type": "DatabaseService",
            "relationship": "positive"
            },
            "Docker": {
            "type": "ContainerPlatform",
            "relationship": "negative"
            }
        }
        }
        \"\"\"
        
        Extract and format the relevant information as structured JSON. ONLY INCLUDE THE JSON. NO ADDITIONAL TEXT.
        """


    # Combine the system prompt with the user prompt
    response = invoke_groq(prompt=prompt, system_prompt=system_prompt)
    print(response)
    
    extracted_data = json.loads(response)
    return extracted_data
    


async def clean_extracted_entities(data, prompt_context):
    """
    Dynamically cleans extracted entities by leveraging an LLM to filter out meaningless or generic terms.

    Parameters:
        data (dict): The JSON-like data structure containing entities and relationships.
        prompt_context (str): The context or original user prompt to help the LLM understand the situation.

    Returns:
        dict: A cleaned data structure with only meaningful entities and relationships.
    """
    if not data or "Entities" not in data:
        return data  # Return as is if the structure is not as expected

    entities = data.get("Entities", {})
    if not entities:
        return data  # No entities to process

    # Construct a dynamic LLM prompt to evaluate the entities
    cleaning_prompt = f"""
    You are an expert entity evaluator for a natural language processing system. Your task is to clean up extracted entities and relationships.

    ### Context:
    The user provided this prompt: "{prompt_context}"

    ### Entities to Evaluate:
    {json.dumps(entities, indent=4)}

    ### Instructions:
    1. Identify entities that are too vague, generic, or irrelevant to the context of the user prompt.
    2. Mark each entity as either "meaningful" or "meaningless."
    3. If an entity is vague or irrelevant (e.g., "code," "data," "performance"), classify it as "meaningless."
    4. Provide your response as JSON with the following structure:
    {{
        "Entity1": "meaningful",
        "Entity2": "meaningless",
        ...
    }}
    ONLY INCLUDE THE JSON. NO ADDITIONAL TEXT.
    """

    # Invoke the LLM with the cleaning prompt
    response = invoke_groq(cleaning_prompt)

    try:
        evaluation_result = json.loads(response.content)

        # Filter out entities based on LLM's evaluation
        cleaned_entities = {
            key: value
            for key, value in entities.items()
            if evaluation_result.get(key, "meaningless") == "meaningful"
        }

        # Replace the original entities with the cleaned ones
        data["Entities"] = cleaned_entities
        return data
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response from LLM.")
        return data
