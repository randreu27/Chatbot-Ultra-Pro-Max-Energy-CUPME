import os

from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
import torch

# Check if GPU is available and set the device accordingly
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load environment variables from .env
load_dotenv()

# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": device} 
)
# Load the existing vector store with the embedding function
vector_store = PineconeVectorStore(
    embedding=embeddings,
    index_name="rag-siemens-embed384",
    namespace="default"  
)

# Create a retriever for querying the vector store
# `search_type` specifies the type of search (e.g., similarity)
# `search_kwargs` contains additional arguments for the search (e.g., number of results to return)
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},
)

# Create a ChatOpenAI model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Contextualize question prompt
# This system prompt helps the AI understand that it should reformulate the question
# based on the chat history to make it a standalone question
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, just "
    "reformulate it if needed and otherwise return it as is."
)

# Create a prompt template for contextualizing questions
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Create a history-aware retriever
# This uses the LLM to help reformulate the question based on chat history
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Answer question prompt
# This system prompt helps the AI understand that it should provide concise answers
# based on the retrieved context and indicates what to do if the answer is unknown
qa_system_prompt = (
    "You are an assistant for question-answering tasks of the products of Siemens-Energy. Use "
    "the following pieces of retrieved context to answer the question. "
    "\n\n"
    "{context}"
    "\n\n"
    "If you DO NOT KNOW the answer, just say that you "
    "don't know. NO ACKNOWLEDGEMENTS, NO EXPLANATIONS."
    "Use five sentences maximum and keep the answer concise."
    "At the end of your answer, cite your sources (if necessary) by writing SOURCES: followed by the source links. (separated by a line break). "
)

# Create a prompt template for answering questions
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Simply modify the continual_chat function to show sources
def continual_chat():
    print("Start chatting with the AI! Type 'exit' to end the conversation.")
    chat_history = []  # Collect chat history here (a sequence of messages)
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        
        # First get documents from retriever to access their metadata
        contextualized_question = history_aware_retriever.invoke({
            "input": query,
            "chat_history": chat_history
        })
        
        # Process the query manually using the prompt and LLM
        formatted_prompt = qa_prompt.format(
            context=contextualized_question,
            chat_history=chat_history,
            input=query
        )
        
        response = llm.invoke(formatted_prompt)
        answer = response.content
        
        # Display the AI's response
        print(f"AI: {answer}")
        
        # Update the chat history
        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=answer))


# Main function to start the continual chat
if __name__ == "__main__":
    continual_chat()
