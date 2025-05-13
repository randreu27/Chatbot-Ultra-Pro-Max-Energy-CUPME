from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
import uvicorn
import os
from typing import List, Dict, Any

# Importar nuestro RAG
from rag_pinecone import (
    llm,
    qa_prompt, 
    history_aware_retriever,
    retriever
)

# Inicializar la aplicación FastAPI
app = FastAPI(title="Siemens Energy ChatBot")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Definir el modelo de entrada para el chat
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]  # Lista de dicts con {"user": ..., "ai": ...}

# Endpoint para el chat
@app.post("/chat")
async def chat(request: ChatRequest):
    print(request)
    try:
        # Convertir el historial a mensajes para LangChain
        chat_history = []
        for message in request.history:
            chat_history.append(HumanMessage(content=pair["user"]))
            chat_history.append(AIMessage(content=pair["ai"]))

        # Obtener documentos del retriever con su metadata
        if chat_history:
            contextualized_question = history_aware_retriever.invoke({
                "input": request.message,
                "chat_history": chat_history
            })
            docs = contextualized_question
        else:
            docs = retriever.invoke(request.message)
        
        # Extraer fuentes
        sources = [doc.metadata.get('source', 'Unknown source') for doc in docs]
        
        # Crear contexto con información de fuentes
        context_with_sources = []
        for i, doc in enumerate(docs):
            source = sources[i]
            context_with_sources.append(f"{doc.page_content}\nSOURCE: {source}")
        
        # Unir todas las piezas de contexto
        combined_context = "\n\n".join(context_with_sources)
        
        # Procesar la consulta usando el prompt y LLM
        formatted_prompt = qa_prompt.format(
            context=combined_context,
            chat_history=chat_history,
            input=request.message
        )
        
        response = llm.invoke(formatted_prompt)
        answer = response.content
        
        # Devolver la respuesta
        return {"response": answer}

    except Exception as e:
        # Manejar errores
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar la consulta")

# Servir el archivo index.html en la ruta raíz
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Endpoint de salud
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API ChatBot Siemens Energy está funcionando"}

if __name__ == "__main__":
    # Asegurarse de que existe el directorio static
    os.makedirs("static", exist_ok=True)
    
    # Ejecutar en todas las interfaces (0.0.0.0) para que sea accesible desde otros dispositivos
    uvicorn.run(app, host="0.0.0.0", port=8000)