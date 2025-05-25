import os
from dotenv import load_dotenv
from llm_translator import LLMTranslator
from rag_system import RAGSystem
from chat_history_manager import ChatHistoryManager


class SiemensEnergyAssistant:
    """A RAG-based voice assistant for answering questions about Siemens Energy products."""
    
    def __init__(self):
        """Initialize the assistant with models, prompts, and configuration."""
        # Load environment variables
        load_dotenv()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Initialize components with shared LLM to avoid redundancy
        self.current_language = "en"  # Default language
        
        # Create shared LLM instance
        from langchain_google_genai import ChatGoogleGenerativeAI
        shared_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        # Initialize components with shared LLM
        self.translator = LLMTranslator(shared_llm)
        self.rag_system = RAGSystem(shared_llm)
        self.chat_manager = ChatHistoryManager()
    
    def set_language(self, language_code):
        """Set the preferred language for responses.
        
        Args:
            language_code (str): Language code (es, ca, en, zh)
        """
        self.current_language = language_code
        print(f"🌍 Language set to: {language_code}")
    
    def get_text_input(self):
        """Get user input through text entry.
        
        Returns:
            str: The user's query text
        """
        return input("You (text): ")
    
    def process_query(self, query):
        """Process a user query using the RAG pipeline with translation."""
        # Translate query to English for RAG processing
        english_query = self.translator.translate_to_english(query, self.current_language)
        
        # Create English chat history for context
        english_chat_history = self.chat_manager.get_english_chat_history(
            self.translator, self.current_language
        )
        
        # Process query using RAG system and translate response
        english_response = self.rag_system.process_query(english_query, english_chat_history)
        return self.translator.translate_from_english(english_response, self.current_language)
    
    def update_chat_history(self, query, answer):
        """Update the chat history with a user query and AI response.
        
        Args:
            query (str): The user's question in their preferred language
            answer (str): The assistant's response in their preferred language
        """
        self.chat_manager.update_chat_history(query, answer, self.translator, self.current_language)
    
    def run(self):
        """Run the main conversation loop for the assistant."""
        print("Welcome to Siemens Energy Assistant!")
        print("You can ask questions about Siemens Energy products.")
        print("Type 'exit' at any time to end the conversation.")
        
        # Begin conversation loop
        while True:
            # Get user input with choice between voice and text
            query = self.get_text_input()
            
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