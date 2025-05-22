from sentence_transformers import SentenceTransformer
import json
import os

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def embed_chunks(chunks):
    """Generate embeddings for a list of chunks."""
    # Convert each chunk to a string representation
    chunk_texts = [json.dumps(chunk) for chunk in chunks]
    # Generate embeddings
    embeddings = model.encode(chunk_texts)
    return embeddings

def process_collection(file_path):
    """Load, chunk, and embed a collection from a JSON file."""
    data = load_json(file_path)
    # For simplicity, treat each item as a chunk
    chunks = data
    embeddings = embed_chunks(chunks)
    return chunks, embeddings

if __name__ == '__main__':
    data_dir = '../data'
    collections = ['wearable.json', 'chat_history.json', 'user_profile.json', 'location.json', 'custom.json']
    for collection in collections:
        file_path = os.path.join(data_dir, collection)
        chunks, embeddings = process_collection(file_path)
        print(f'Processed {collection}: {len(chunks)} chunks, {embeddings.shape} embeddings') 