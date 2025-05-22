from sentence_transformers import SentenceTransformer
import numpy as np
from .vector_store import VectorStore

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_query(query):
    """Generate embedding for a query."""
    return model.encode(query)

def retrieve_data(query, vector_store, k=5):
    """Retrieve relevant data from the vector store based on the query."""
    query_embedding = embed_query(query)
    return vector_store.search(query_embedding, k)

if __name__ == '__main__':
    # Example usage
    vector_store = VectorStore()
    # Assume vector_store is already populated
    query = "What's the weather like?"
    results = retrieve_data(query, vector_store)
    print(f'Retrieved {len(results)} results for query: {query}') 