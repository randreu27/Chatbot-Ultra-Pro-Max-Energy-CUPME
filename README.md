# Chatbot Ultra Pro Max Energy

A Retrieval-Augmented Generation (RAG) based chatbot application specifically designed for Siemens Energy. This intelligent assistant can answer queries about Siemens Energy products, services, and documentation by leveraging a knowledge base with accurate information retrieval.

## 🔍 Overview

This RAG-based chatbot provides Siemens Energy with an intelligent assistant that can retrieve relevant information from a knowledge base and generate accurate, contextually appropriate responses to user queries. The application is built using a modern tech stack and follows best practices for natural language processing and information retrieval.

## ✨ Features

- **Voice Recognition**: Supports voice input for hands-free interaction with the chatbot
- **Knowledge-Grounded Responses**: Leverages RAG to provide accurate responses based on Siemens Energy documentation
- **Context-Aware Conversations**: Maintains context throughout the conversation
- **Real-time Interaction**: Offers fast response times for enhanced user experience
- **Chat History**: Maintains conversation history for reference
- **User-Friendly Interface**: Intuitive web interface for easy interaction

## 🏗️ Architecture
The application follows a RAG (Retrieval-Augmented Generation) architecture:

- Vector Database: Stores embeddings of the knowledge base documents
- Retriever: Finds relevant documents based on the user query
- LLM Integration: Uses a language model to generate responses based on retrieved context
- Web Interface: Provides a clean interface for users to interact with the chatbot


## ⚙️ Technology Stack

This project leverages the following technologies:

### Backend

- **FastAPI**: High-performance web framework for building APIs
- **LangChain**: Framework for developing applications powered by language models
- **Pinecone**: Vector database for efficient similarity search
- **Google Gemini**: Language model for generating human-like responses
- **Uvicorn**: ASGI server for running the FastAPI application

### Frontend

- **HTML/CSS/JavaScript**: Core web technologies
- **TailwindCSS**: Utility-first CSS framework for styling
- **Web Speech API**: Browser API for voice recognition and text-to-speech


## 🛠️ Installation

### Prerequisites

- Python 3.11+
- API keys for:
  - [Google API](https://console.cloud.google.com/apis/credentials) (for LLM)
  - [Pinecone API](https://app.pinecone.io/) (for vector database)

### Quick Setup

```bash
# Clone and enter repository
git clone https://github.com/randreu27/PIA-Siemens

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -r requirements.txt.

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```


## 🖥️ Usage

### Web Scraping

### Vector Store
1. Place your text files in the RAG/vector_store/product-offerings directory.
2. Create a file_url_pairs.json file in RAG/vector_store to associate each file with its source URL or any other relevant metadata. 
3. Edit RAG/vector_store/vector_store_pinecone.py to set up your embedding model and Pinecone connection.
```bash
# Enter to the vector store directory
cd RAG/vector_store

# Create the data directory
mkdir -p product-offerings

# Create or edit the file-URL mapping
vi file_url_pairs.json

# Run the script to populate the vector store
python vector_store_pinecone.py
```

### RAG System

1. Start the backend server:
```bash
# Enter the directory
cd RAG

# Running
python main.py
```
2. The API will be available at http://localhost:8000. Access the application at http://localhost:8000 after starting the backend.

## 🤖 Using the Chatbot

1. Access the web interface through your browser at http://localhost:8000
2. Type your query related to Siemens Energy in the input field or click the microphone button to use voice input
3. For voice input:

- Ensure your microphone is connected and working
- Click the microphone icon in the chat interface
- In the voice modal that appears, click "Start" to begin speaking
- Speak your question clearly
- Click "Stop" when finished or let it automatically detect when you've stopped speaking
- The voice recognition system will convert your speech to text
- The chatbot will process your query and respond

4. Receive knowledgeable responses based on the Siemens Energy documentation
5. Continue the conversation with follow-up questions as needed, using either text or voice input



## 👥 Authors

- **Ramon Andreu**
- **Pengcheng Chen**
- **Zhihao Chen**
- **Zhiqian Zhou**
