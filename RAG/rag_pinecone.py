import os
import torch
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings

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
        self.current_language = "en"  # Default language
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
            namespace="complete_docs"
        )
        
        # Create a retriever for querying the vector store
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 20, "score_threshold": 0.5},
        )
        
        # Create LLM model
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    def set_language(self, language_code):
        """Set the preferred language for responses.
        
        Args:
            language_code (str): Language code (es, ca, en, zh)
        """
        self.current_language = language_code
        print(f"🌍 Language set to: {language_code}")
    
    def _get_language_name(self, lang_code):
        """Get the full language name from language code.
        
        Args:
            lang_code (str): Language code
            
        Returns:
            str: Full language name
        """
        language_names = {
            "es": "Spanish",
            "ca": "Catalan", 
            "en": "English",
            "zh": "Chinese"
        }
        return language_names.get(lang_code, "English")
    
    def _translate_to_english(self, text):
        """Translate text to English for RAG processing using Gemini LLM.
        
        Args:
            text (str): Text in the user's language
            
        Returns:
            str: Text translated to English
        """
        if self.current_language == "en":
            return text
        
        try:
            source_language = self._get_language_name(self.current_language)
            
            translation_prompt = f"""
            Translate the following text from {source_language} to English. 
            Only return the translation, nothing else. Do not add explanations or comments.

            Text to translate: {text}

            Translation:"""
            
            response = self.llm.invoke(translation_prompt)
            translated_text = response.content.strip()
            print(f"🔄 Translated query: '{text}' -> '{translated_text}'")
            return translated_text
            
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return text  # Return original text if translation fails
    
    def _translate_from_english(self, text):
        """Translate text from English to the user's language using Gemini LLM.
        
        Args:
            text (str): Text in English
            
        Returns:
            str: Text translated to user's language
        """
        if self.current_language == "en":
            return text
        
        try:
            target_language = self._get_language_name(self.current_language)
            
            # Special handling for sources section
            if "SOURCES:" in text:
                # Split text and sources
                parts = text.split("SOURCES:")
                main_text = parts[0].strip()
                sources_text = "SOURCES:" + parts[1] if len(parts) > 1 else ""
                
                # Translate only the main text, keep sources in original
                translation_prompt = f"""Translate the following text from English to {target_language}. 
Only return the translation, nothing else. Do not add explanations or comments.
Keep technical terms and product names in English when appropriate.

Text to translate: {main_text}

Translation:"""
                
                response = self.llm.invoke(translation_prompt)
                translated_main = response.content.strip()
                
                # Combine translated text with original sources
                final_text = translated_main + "\n\n" + sources_text if sources_text else translated_main
                print(f"🔄 Translated response: EN -> {self.current_language.upper()}")
                return final_text
            else:
                # Regular translation
                translation_prompt = f"""Translate the following text from English to {target_language}. 
Only return the translation, nothing else. Do not add explanations or comments.
Keep technical terms and product names in English when appropriate.

Text to translate: {text}

Translation:"""
                
                response = self.llm.invoke(translation_prompt)
                translated_text = response.content.strip()
                print(f"🔄 Translated response: EN -> {self.current_language.upper()}")
                return translated_text
                
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return text  # Return original text if translation fails
    
    def _get_language_instruction(self):
        """Get language-specific instruction for the system prompt.
        
        Returns:
            str: Language instruction for the system prompt (always in English for RAG)
        """
        # Keep instructions in English since RAG processing is in English
        # The final response will be translated to target language
        return "IMPORTANT: Always respond in English. The response will be translated to the user's preferred language automatically."
    
    def _create_prompt_templates(self):
        """Create prompt templates for contextualizing questions and answering."""
        # Contextualize question prompt (in English)
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is. "
            "Keep the question in English."
        )

        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        # Answer question prompt - always in English for RAG processing
        self.qa_prompt_template = (
            "You are an assistant for question-answering tasks of the products of Siemens-Energy. Use "
            "the following pieces of retrieved context to answer the question. "
            "\n\n"
            "{context}"
            "\n\n"
            "If you DO NOT KNOW the answer, just say that you "
            "don't know. NO ACKNOWLEDGEMENTS, NO EXPLANATIONS."
            "Use five sentences maximum and keep the answer concise."
            "At the end of your answer, cite your sources (if necessary) by writing \nSOURCES: followed by the source links."
            "(separated by a line break and no repetition). "
            "\n\n"
            "{language_instruction}"
        )
    
    def _get_current_qa_prompt(self):
        """Get the current QA prompt with language instruction.
        
        Returns:
            ChatPromptTemplate: The QA prompt template with current language instruction
        """
        qa_system_prompt = self.qa_prompt_template.format(
            context="{context}",
            language_instruction=self._get_language_instruction()
        )
        
        return ChatPromptTemplate.from_messages([
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
    
    def process_query(self, query):
        """Process a user query using the RAG pipeline with translation.
        
        Args:
            query (str): The user's question in their preferred language
            
        Returns:
            str: The assistant's response in the user's preferred language
        """
        # Step 1: Translate query to English for RAG processing
        english_query = self._translate_to_english(query)
        
        # Step 2: Create English chat history for context (translate user messages only)
        english_chat_history = []
        for message in self.chat_history:
            if isinstance(message, HumanMessage):
                # Translate user messages to English for better context
                if self.current_language != "en":
                    translated_content = self._translate_to_english(message.content)
                    english_chat_history.append(HumanMessage(content=translated_content))
                else:
                    english_chat_history.append(message)
            else:  # AIMessage
                # AI messages are already in English from RAG processing
                english_chat_history.append(message)
        
        # Step 3: Get contextualized question based on English chat history
        contextualized_question = self.history_aware_retriever.invoke({
            "input": english_query,
            "chat_history": english_chat_history
        })
        
        # Step 4: Get current QA prompt with language instruction
        current_qa_prompt = self._get_current_qa_prompt()
        
        # Step 5: Process the query using the prompt and LLM (in English)
        formatted_prompt = current_qa_prompt.format(
            context=contextualized_question,
            chat_history=english_chat_history,
            input=english_query
        )
        
        # Step 6: Get response from LLM (in English)
        response = self.llm.invoke(formatted_prompt)
        english_response = response.content
        
        # Step 7: Translate response to user's language
        translated_response = self._translate_from_english(english_response)
        
        return translated_response
    
    def update_chat_history(self, query, answer):
        """Update the chat history with a user query and AI response.
        
        Args:
            query (str): The user's question in their preferred language
            answer (str): The assistant's response in their preferred language
        """
        # Store user query in their original language
        self.chat_history.append(HumanMessage(content=query))
        
        # Store AI response in English for better context in future queries
        if self.current_language != "en":
            # Translate the response back to English for storage
            english_answer = self._translate_to_english(answer)
            self.chat_history.append(AIMessage(content=english_answer))
        else:
            self.chat_history.append(AIMessage(content=answer))
    
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