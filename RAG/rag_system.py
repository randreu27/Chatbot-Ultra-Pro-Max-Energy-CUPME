import os
import torch
from langchain.chains import create_history_aware_retriever
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings


class RAGSystem:
    """Handles RAG (Retrieval-Augmented Generation) operations."""
    
    # Class-level constants to avoid repetition
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
    INDEX_NAME = "rag-siemens-embed384" 
    NAMESPACE = "complete_docs"
    SEARCH_CONFIG = {"k": 20, "score_threshold": 0.5}
    
    # Prompt templates as class constants
    CONTEXTUALIZE_PROMPT = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is. "
        "Keep the question in ENGLISH."
    )
    
    QA_PROMPT_BASE = (
    "You are an assistant for question-answering tasks of the products of Siemens-Energy. Use "
    "the following pieces of retrieved context to answer the question. "
    "\n\n{context}\n\n"
    "If you DO NOT KNOW the answer, just say that you "
    "don't know. NO ACKNOWLEDGEMENTS, NO EXPLANATIONS."
    "Use three sentences maximum and keep the answer concise."
    "At the end of your answer, cite your sources by writing \nSOURCES: followed by the source links."
    "(separated by a line break and no repetition). "
    "\nIMPORTANT: Always respond in ENGLISH."
    )

    def __init__(self, llm=None):
        """Initialize the RAG system with models and configuration.
        
        Args:
            llm: Optional existing LLM instance to reuse
        """
        # Set device
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Initialize components
        self._initialize_models(llm)
        self._create_prompt_templates()
        self._setup_history_aware_retriever()
    
    def _initialize_models(self, llm=None):
        """Initialize embedding model, vector store, retriever and LLM."""
        # Define the embedding model
        embeddings = HuggingFaceEmbeddings(
            model_name=self.EMBEDDING_MODEL,
            model_kwargs={"device": self.device}
        )
        
        # Load the vector store with the embedding function
        vector_store = PineconeVectorStore(
            embedding=embeddings,
            index_name=self.INDEX_NAME,
            namespace=self.NAMESPACE
        )
        
        # Create a retriever for querying the vector store
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs=self.SEARCH_CONFIG,
        )
        
        # Create or reuse LLM model
        self.llm = llm or ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    def _create_prompt_templates(self):
        """Create prompt templates for contextualizing questions and answering."""
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", self.CONTEXTUALIZE_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.QA_PROMPT_BASE),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
    
    def _setup_history_aware_retriever(self):
        """Set up the history-aware retriever using the LLM and prompt templates."""
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, 
            self.retriever, 
            self.contextualize_q_prompt
        )
    
    def process_query(self, english_query, english_chat_history):
        """Process a query using the RAG pipeline."""
        # Get contextualized question
        contextualized_question = self.history_aware_retriever.invoke({
            "input": english_query,
            "chat_history": english_chat_history
        })
        
        # Get response from LLM using the QA prompt
        response = self.llm.invoke(
            self.qa_prompt.format(
                context=contextualized_question,
                chat_history=english_chat_history,
                input=english_query
            )
        )
        
        return response.content