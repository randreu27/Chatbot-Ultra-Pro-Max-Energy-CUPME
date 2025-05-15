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

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define the input model for the chat
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]  # List of dicts with {"user": ..., "ai": ...}

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    print(request)
    try:
        # Convert history to LangChain message format
        chat_history = []
        for pair in request.history:
            chat_history.append(HumanMessage(content=pair["user"]))
            chat_history.append(AIMessage(content=pair["ai"]))
        
        # Set the assistant's chat history
        assistant.chat_history = chat_history
        
        # Process the query using the assistant
        answer = assistant.process_query(request.message)
        
        # Return the response
        return {"response": answer}

    except Exception as e:
        # Handle errors
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing the request")

# Serve the index.html file at the root path
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Health endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Siemens Energy ChatBot API is running"}

if __name__ == "__main__":
    # Ensure the static directory exists
    os.makedirs("static", exist_ok=True)
    
    # Run on all interfaces (0.0.0.0) to be accessible from other devices
    uvicorn.run(app, host="0.0.0.0", port=8000)