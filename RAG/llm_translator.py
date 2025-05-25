from langchain_google_genai import ChatGoogleGenerativeAI


class LLMTranslator:
    """Handles translation tasks using Gemini LLM."""
    
    # Class-level language mapping to avoid repetition
    LANGUAGE_NAMES = {
        "es": "Spanish",
        "ca": "Catalan", 
        "en": "English",
        "zh": "Chinese"
    }
    
    def __init__(self, llm=None):
        """Initialize the translator with Gemini LLM.
        
        Args:
            llm: Optional existing LLM instance to reuse
        """
        self.llm = llm or ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    def _get_language_name(self, lang_code):
        """Get the full language name from language code."""
        return self.LANGUAGE_NAMES.get(lang_code, "English")
    
    def _create_translation_prompt(self, text, source_lang, target_lang):
        """Create a translation prompt template.
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language name
            target_lang (str): Target language name
            
        Returns:
            str: Formatted translation prompt
        """
        return f"""Translate the following text from {source_lang} to {target_lang}. 
                Only return the translation, nothing else. Do not add explanations or comments.
                Keep technical terms and product names in English when appropriate.
                Text to translate: {text}
                Translation:"""
    
    def translate_to_english(self, text, current_language):
        """Translate text to English for RAG processing using Gemini LLM."""
        if current_language == "en":
            return text
        
        try:
            source_language = self._get_language_name(current_language)
            prompt = self._create_translation_prompt(text, source_language, "English")
            
            response = self.llm.invoke(prompt)
            translated_text = response.content.strip()
            print(f"Translated query: '{text}' -> '{translated_text}'")
            return translated_text
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def translate_from_english(self, text, current_language):
        """Translate text from English to the user's language using Gemini LLM."""
        if current_language == "en":
            return text
        
        try:
            target_language = self._get_language_name(current_language)
            
            # Handle sources section separately
            if "SOURCES:" in text:
                main_text, sources_text = text.split("SOURCES:", 1)
                main_text = main_text.strip()
                sources_text = "SOURCES:" + sources_text
                
                # Translate only main text
                prompt = self._create_translation_prompt(main_text, "English", target_language)
                response = self.llm.invoke(prompt)
                translated_main = response.content.strip()
                
                final_text = f"{translated_main}\n\n{sources_text}" if sources_text else translated_main
            else:
                # Regular translation
                prompt = self._create_translation_prompt(text, "English", target_language)
                response = self.llm.invoke(prompt)
                final_text = response.content.strip()
            
            print(f"Translated response: EN -> {current_language.upper()}")
            return final_text
                
        except Exception as e:
            print(f"Translation error: {e}")
            return text