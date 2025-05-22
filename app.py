import streamlit as st
from chatbot import Chatbot
from rag.vector_store import VectorStore
import json
import os
import numpy as np

# Initialize vector store
vector_store = VectorStore()

# Load and process all collections
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def process_collection(file_path, vector_store):
    """Load and add a collection to the vector store."""
    data = load_json(file_path)
    # For simplicity, treat each item as a chunk
    chunks = data
    # Generate dummy embeddings (replace with actual embeddings in production)
    embeddings = np.random.rand(len(chunks), 384)  # 384 is the dimension for 'all-MiniLM-L6-v2'
    vector_store.add_chunks(chunks, embeddings)

# Process all collections
data_dir = 'data'
collections = ['wearable.json', 'chat_history.json', 'user_profile.json', 'location.json', 'custom.json']
for collection in collections:
    file_path = os.path.join(data_dir, collection)
    process_collection(file_path, vector_store)

# Initialize chatbot with populated vector store
chatbot = Chatbot(vector_store)

st.title('Multi-Collection RAG Chatbot')

# Input for user query
query = st.text_input('Ask a question:')

if query:
    # Generate response
    response = chatbot.generate_response(query)
    
    # Split response and suggestions
    if "Proactive Suggestions:" in response:
        main_response, suggestions = response.split("Proactive Suggestions:")
        st.write(f'Response: {main_response.strip()}')
        
        st.subheader('Proactive Suggestions')
        for suggestion in suggestions.strip().split('\n'):
            if suggestion.strip():
                st.write(f"💡 {suggestion.strip()}")
    else:
        st.write(f'Response: {response}')

    # Display memory history
    st.subheader('Recent Interactions')
    for interaction in chatbot.memory.get_history():
        st.write(f"Q: {interaction['query']}\nA: {interaction['response']}") 