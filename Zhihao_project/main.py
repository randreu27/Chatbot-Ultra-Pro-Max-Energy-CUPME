from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pinecone import rag_chain  # Importa tu RAG
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI()

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir a ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define el modelo de entrada
class ChatRequest(BaseModel):
    message: str
    history: list  # Lista de dicts con {"user": ..., "ai": ...}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Convierte el historial a mensajes para LangChain
    chat_history = []
    for pair in request.history:
        chat_history.append(HumanMessage(content=pair["user"]))
        chat_history.append(AIMessage(content=pair["ai"]))

    # Ejecuta el RAG
    result = rag_chain.invoke({
        "input": request.message,
        "chat_history": chat_history
    })

    return {"response": result["answer"]}
