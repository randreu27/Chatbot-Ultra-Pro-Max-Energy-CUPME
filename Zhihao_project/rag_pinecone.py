import os
import torch
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from voice_recognition import VoiceRecognition


class SiemensEnergyAssistant:
    """A RAG-based voice assistant for answering questions about Siemens Energy products."""
    
    def __init__(self):
        """Initialize the assistant with models, prompts, and configuration."""
        # Load environment variables and set device
        load_dotenv()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Initialize components
        self.chat_history = []
        self.voice_recognition = VoiceRecognition()
        self._initialize_models()
        self._create_prompt_templates()
        self._setup_history_aware_retriever()
        
    def _initialize_models(self):
        """Initialize embedding model, vector store, retriever and LLM."""
        # Define the embedding model
        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": self.device}
        )
        
        # Load the vector store with the embedding function
        vector_store = PineconeVectorStore(
            embedding=embeddings,
            index_name="rag-siemens-embed384",
            namespace="default"
        )
        
        # Create a retriever for querying the vector store
        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )
        
        # Create LLM model
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    def _create_prompt_templates(self):
        """Create prompt templates for contextualizing questions and answering."""
        # Contextualize question prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is."
        )

        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        # Answer question prompt
        qa_system_prompt = (
            "You are an assistant for question-answering tasks of the products of Siemens-Energy. Use "
            "the following pieces of retrieved context to answer the question. "
            "\n\n"
            "{context}"
            "\n\n"
            "If you DO NOT KNOW the answer, just say that you "
            "don't know. NO ACKNOWLEDGEMENTS, NO EXPLANATIONS."
            "Use five sentences maximum and keep the answer concise."
            "At the end of your answer, cite your sources (if necessary) by writing \nSOURCES: followed by the source links. (separated by a line break). "
        )

        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
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
    
    def get_text_input(self):
        """Get user input through text entry.
        
        Returns:
            str: The user's query text
        """
        return input("You (text): ")
    
    def get_voice_input(self):
        """Get user input through voice recognition.
        
        Returns:
            str: The transcribed voice input or None if recognition failed
        """
        query = None
        while query is None:
            # Start recording
            print("Press Enter to start recording...")
            input()
            self.voice_recognition.start_recording()
            
            # Stop recording and get the recognized text
            print("Recording... Press Enter to stop recording")
            input()
            query = self.voice_recognition.stop_recording()
            
            if query is None:
                print("Sorry, I didn't catch that. Please try again or type 'text' to switch to text input.")
                choice = input("Try voice again? (y/n): ")
                if choice.lower() != 'y':
                    return self.get_text_input()
        
        print(f"You (voice): {query}")
        return query
    
    def get_user_input(self):
        """Get user input with choice between voice and text.
        
        Returns:
            str: The user's query text
        """
        print("\nHow would you like to input your question (1: Voice input / 2: Text input)?")
        choice = input("Your choice (1/2): ")
        
        if choice == '1':
            return self.get_voice_input()
        else:
            return self.get_text_input()
    
    def process_query(self, query):
        """Process a user query using the RAG pipeline.
        
        Args:
            query (str): The user's question
            
        Returns:
            str: The assistant's response
        """
        # Get contextualized question based on chat history
        contextualized_question = self.history_aware_retriever.invoke({
            "input": query,
            "chat_history": self.chat_history
        })
        
        # Process the query using the prompt and LLM
        formatted_prompt = self.qa_prompt.format(
            context=contextualized_question,
            chat_history=self.chat_history,
            input=query
        )
        
        # Get response from LLM
        response = self.llm.invoke(formatted_prompt)
        return response.content
    
    def update_chat_history(self, query, answer):
        """Update the chat history with a user query and AI response.
        
        Args:
            query (str): The user's question
            answer (str): The assistant's response
        """
        self.chat_history.append(HumanMessage(content=query))
        self.chat_history.append(AIMessage(content=answer))
    
    def run(self):
        """Run the main conversation loop for the assistant."""
        print("Welcome to Siemens Energy Assistant!")
        print("You can ask questions about Siemens Energy products.")
        print("Type 'exit' at any time to end the conversation.")
        
        # Begin conversation loop
        while True:
            # Get user input with choice between voice and text
            query = self.get_user_input()
            
            if query.lower() == "exit":
                print("Goodbye! Thanks for chatting.")
                break
            
            # Process query and get response
            answer = self.process_query(query)
            
            # Display the AI's response
            print(f"AI: {answer}")
            
            # Update the chat history
            self.update_chat_history(query, answer)


# --- Main Entry Point ---
if __name__ == "__main__":
    # Create and run the assistant
    assistant = SiemensEnergyAssistant()
    assistant.run()