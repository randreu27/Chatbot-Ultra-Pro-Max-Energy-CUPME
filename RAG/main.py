from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
import uvicorn
import os
from typing import List, Dict, Any

# Import our RAG assistant class
from rag_pinecone import SiemensEnergyAssistant

# Get the absolute path to the directory where main.py is located
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")

# Initialize the SiemensEnergyAssistant
assistant = SiemensEnergyAssistant()

# Initialize the FastAPI application
app = FastAPI(title="Siemens Energy ChatBot")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Define the input model for the chat
class ChatRequest(BaseModel):
    message: str
    language: str = "en"  # Default to English

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    print(request)
    print(f"📚 Historial ANTES del procesamiento: {len(assistant.chat_history)} elementos")
    print(f"🌍 Processing in language: {request.language}")
    try:
        # Set language preference in assistant
        assistant.set_language(request.language)
        
        # Process the query using the assistant (with translation if needed)
        answer = assistant.process_query(request.message)
        # Update the chat history in backend
        assistant.update_chat_history(request.message, answer)
        print(f"📚 Historial DESPUÉS del procesamiento: {len(assistant.chat_history)} elementos")
        # Return the response
        return {"response": answer}

    except Exception as e:
        # Handle errors
        print(f"Error: {str(e)}")
        # Return error message in user's language
        error_messages = {
            "es": "Lo siento, ocurrió un error al procesar tu pregunta. Por favor, inténtalo de nuevo.",
            "ca": "Ho sento, s'ha produït un error en processar la teva pregunta. Si us plau, torna-ho a intentar.",
            "en": "Sorry, an error occurred while processing your question. Please try again.",
            "zh": "抱歉，处理您的问题时出现了错误。请重试。"
        }
        error_msg = error_messages.get(request.language, error_messages["en"])
        raise HTTPException(status_code=500, detail=error_msg)

# Clear chat history endpoint
@app.post("/clear-history")
async def clear_history():
    try:
        # Clear the chat history in the assistant
        print(f"🗑️ Limpiando historial. Elementos antes: {len(assistant.chat_history)}")
        assistant.chat_history = []
        print(f"🗑️ Historial limpiado. Elementos después: {len(assistant.chat_history)}")
        return {"status": "success", "message": "Chat history cleared"}
    
    except Exception as e:
        print(f"Error clearing history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error clearing chat history")

# Serve the index.html file at the root path
@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Health endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Siemens Energy ChatBot API is running"}

if __name__ == "__main__":
    # Ensure the static directory exists
    os.makedirs("static", exist_ok=True)
    
    # Run on all interfaces (0.0.0.0) to be accessible from other devices
    uvicorn.run(app, host="localhost", port=8000)
