import faiss
import numpy as np
import json
import os

class VectorStore:
    def __init__(self, dimension=384):  # dimension for 'all-MiniLM-L6-v2'
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []

    def add_chunks(self, chunks, embeddings):
        """Add chunks and their embeddings to the index."""
        self.chunks.extend(chunks)
        self.index.add(embeddings.astype(np.float32))

    def search(self, query_embedding, k=5):
        """Search for the k nearest neighbors of the query embedding."""
        distances, indices = self.index.search(query_embedding.astype(np.float32).reshape(1, -1), k)
        return [self.chunks[i] for i in indices[0]]

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def process_collection(file_path, vector_store):
    """Load, chunk, embed, and add a collection to the vector store."""
    data = load_json(file_path)
    # For simplicity, treat each item as a chunk
    chunks = data
    # Generate embeddings (using a dummy embedding for demo)
    embeddings = np.random.rand(len(chunks), 384)  # Replace with actual embeddings
    vector_store.add_chunks(chunks, embeddings)

if __name__ == '__main__':
    data_dir = '../data'
    collections = ['wearable.json', 'chat_history.json', 'user_profile.json', 'location.json', 'custom.json']
    vector_store = VectorStore()
    for collection in collections:
        file_path = os.path.join(data_dir, collection)
        process_collection(file_path, vector_store)
    print(f'Indexed {len(vector_store.chunks)} chunks') 