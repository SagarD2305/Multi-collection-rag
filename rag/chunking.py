import json
import os

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def chunk_data(data, chunk_size=2):
    """Split data into chunks of specified size."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def process_collection(file_path, chunk_size=2):
    """Load and chunk a collection from a JSON file."""
    data = load_json(file_path)
    return chunk_data(data, chunk_size)

if __name__ == '__main__':
    data_dir = '../data'
    collections = ['wearable.json', 'chat_history.json', 'user_profile.json', 'location.json', 'custom.json']
    for collection in collections:
        file_path = os.path.join(data_dir, collection)
        chunks = process_collection(file_path)
        print(f'Processed {collection}: {len(chunks)} chunks') 