# Multi-Collection RAG System with Memory Layer

A sophisticated Retrieval-Augmented Generation (RAG) system that integrates multiple data collections and maintains context through a memory layer. The system is built with Python and provides a web interface using Streamlit.

## Features

- **Multiple Data Collections**:
  - Wearable Data (steps, heart rate)
  - Chat History
  - User Profile
  - Location Data
  - Custom Collection (movies, books, restaurants)

- **RAG Pipeline**:
  - Efficient data chunking and embedding
  - Vector-based similarity search
  - Context-aware response generation

- **Memory Layer**:
  - Maintains conversation context
  - Tracks user preferences and history
  - Enables personalized responses

- **Web Interface**:
  - User-friendly Streamlit dashboard
  - Real-time interaction
  - Visual data representation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multi-collection-rag.git
cd multi-collection-rag
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key'  # On Windows: set OPENAI_API_KEY=your-api-key
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Interact with the chatbot through the web interface

## Project Structure

```
multi-collection-rag/
├── app.py                 # Streamlit web application
├── chatbot.py            # Main chatbot logic
├── requirements.txt      # Project dependencies
├── data/                 # Data collections
│   ├── wearable.json    # Wearable device data
│   ├── chat_history.json # Chat history
│   ├── user_profile.json # User profiles
│   ├── location.json    # Location data
│   └── custom.json      # Custom collection data
└── rag/                 # RAG system components
    ├── chunking.py      # Text chunking utilities
    ├── embedding.py     # Embedding generation
    ├── vector_store.py  # Vector storage and retrieval
    ├── retrieval.py     # Data retrieval logic
    └── memory.py        # Memory layer implementation
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT models
- Streamlit for the web framework
- FAISS for efficient similarity search 