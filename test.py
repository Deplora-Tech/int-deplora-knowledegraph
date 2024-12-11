from sentence_transformers import SentenceTransformer
import numpy as np

def calculate_similarity(entity1, entity2, model):
    """
    Calculate the similarity between two entities by generating embeddings and using cosine similarity.

    Args:
        entity1 (str): The first entity (e.g., "Database").
        entity2 (str): The second entity (e.g., "Web Server").
        model_name (str): Name of the pre-trained model to use for generating embeddings.
                          Default is "all-MiniLM-L6-v2".

    Returns:
        float: Cosine similarity score between the two entities.
    """
    # Load the pre-trained model
    

    # Generate embeddings for both entities
    embedding1 = model.encode(entity1)
    embedding2 = model.encode(entity2)

    # Compute cosine similarity
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    return similarity


model_name="all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)


for _ in range(10):
    entity1 = input("Enter first entity: ")
    entity2 = input("Enter second entity: ")
    similarity = calculate_similarity(entity1, entity2, model)
    print(f"Similarity between '{entity1}' and '{entity2}': {similarity:.4f}")


