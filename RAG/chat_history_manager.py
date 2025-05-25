from langchain_core.messages import HumanMessage, AIMessage


class ChatHistoryManager:
    """Manages chat history and handles language-specific history processing."""
    
    def __init__(self):
        """Initialize the chat history manager."""
        self.chat_history = []
    
    def get_english_chat_history(self, translator, current_language):
        """Create English chat history for context (translate user messages only).
        
        Args:
            translator (LLMTranslator): The translator instance
            current_language (str): Current language code
            
        Returns:
            list: Chat history with user messages translated to English
        """
        english_chat_history = []
        for message in self.chat_history:
            if isinstance(message, HumanMessage):
                # Translate user messages to English for better context
                if current_language != "en":
                    translated_content = translator.translate_to_english(message.content, current_language)
                    english_chat_history.append(HumanMessage(content=translated_content))
                else:
                    english_chat_history.append(message)
            else:  # AIMessage
                # AI messages are already in English from RAG processing
                english_chat_history.append(message)
        
        return english_chat_history
    
    def update_chat_history(self, query, answer, translator, current_language):
        """Update the chat history with a user query and AI response.
        
        Args:
            query (str): The user's question in their preferred language
            answer (str): The assistant's response in their preferred language
            translator (LLMTranslator): The translator instance
            current_language (str): Current language code
        """
        # Store user query in their original language
        self.chat_history.append(HumanMessage(content=query))
        
        # Store AI response in English for better context in future queries
        if current_language != "en":
            # Translate the response back to English for storage
            english_answer = translator.translate_to_english(answer, current_language)
            self.chat_history.append(AIMessage(content=english_answer))
        else:
            self.chat_history.append(AIMessage(content=answer))
    
    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []
    
    def get_history_length(self):
        """Get the current length of chat history.
        
        Returns:
            int: Number of messages in chat history
        """
        return len(self.chat_history)