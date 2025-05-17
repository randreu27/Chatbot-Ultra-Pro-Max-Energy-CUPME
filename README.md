# Chatbot Ultra Pro Max Energy

A Retrieval-Augmented Generation (RAG) based chatbot application specifically designed for Siemens Energy. This intelligent assistant can answer queries about Siemens Energy products, services, and documentation by leveraging a knowledge base with accurate information retrieval.

## 🔍 Overview

This RAG-based chatbot provides Siemens Energy with an intelligent assistant that can retrieve relevant information from a knowledge base and generate accurate, contextually appropriate responses to user queries. The application is built using a modern tech stack and follows best practices for natural language processing and information retrieval.

## ✨ Features

- **Natural Language Understanding**: Processes and understands user queries in natural language
- **Knowledge-Grounded Responses**: Leverages RAG to provide accurate responses based on Siemens Energy documentation
- **Context-Aware Conversations**: Maintains context throughout the conversation
- **Real-time Interaction**: Offers fast response times for enhanced user experience
- **Customizable Knowledge Base**: Can be updated with new information and documentation
- **Chat History**: Maintains conversation history for reference
- **User-Friendly Interface**: Intuitive web interface for easy interaction

## 🏗️ Architecture
The application follows a RAG (Retrieval-Augmented Generation) architecture:

- Vector Database: Stores embeddings of the knowledge base documents
- Retriever: Finds relevant documents based on the user query
- LLM Integration: Uses a language model to generate responses based on retrieved context
- Web Interface: Provides a clean interface for users to interact with the chatbot

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
pip install -r requirements_now.txt.

# Configure API keys
cp .env.template .env
# Edit .env with your API keys
```


## 🖥️ Usage

```bash
# Enter the directory
cd RAG

# Running
python main.py
```

Access the chatbot interface at http://localhost:8000.

## 👥 Authors

- **Ramon Andreu**
- **Pengcheng Chen**
- **Zhihao Chen**
- **Zhiqian Zhou**
