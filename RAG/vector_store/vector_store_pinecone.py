import os

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
import json


# Load environment variables from .env
load_dotenv()

# Define directories
current_dir = os.path.dirname(os.path.abspath(__file__))
products_dir = os.path.join(current_dir, "product-offerings")

print(f"Products directory: {products_dir}")

# Ensure the books directory exists
if not os.path.exists(products_dir):
    raise FileNotFoundError(f"The directory {products_dir} does not exist. Please check the path.")

# Load the JSON file containing file names and URLs
with open(os.path.join(current_dir,"file_url_pairs.json"), "r", encoding="utf-8") as f:
    file_url_pairs = json.load(f)

def get_source(name_txt):
    """
    Process the source name to extract the relevant link from the JSON file.
    Args:
        name_txt (str): The name of the text file.
    Returns:
        str: The corresponding link from the JSON file.
    """
    link = file_url_pairs.get(name_txt, None)

    return link

# Load all .txt files
product_files = [f for f in os.listdir(products_dir) if f.endswith(".txt")]
#book_files = ['documentos.txt'] # Replace with your actual file names
documents = []

for product_file in product_files:
    file_path = os.path.join(products_dir, product_file)
    loader = TextLoader(file_path, encoding="utf-8")
    book_docs = loader.load()
    for doc in book_docs:
        # Add source metadata without overwriting existing data
        doc.metadata.update({"source": get_source(product_file)})
        documents.append(doc)

# Split the documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

print("\n--- Document Chunks Information ---")
print(f"Number of document chunks: {len(docs)}")

# Create embeddings
print("\n--- Creating embeddings ---")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cuda"}  # Use GPU
)

print("--- Finished creating embeddings ---")

from langchain_pinecone import PineconeVectorStore

# Create and persist Pinecone vector store
print("\n--- Creating and persisting vector store ---")
vector_store = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=embeddings,
    index_name="rag-siemens-embed384",
    namespace="complete_docs",  
)
print("--- Finished creating and persisting vector store ---")
