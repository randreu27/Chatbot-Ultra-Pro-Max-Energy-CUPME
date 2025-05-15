import os

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

def process_source(link):
    """
    Process the source string to extract the relevant part.
    """
    # Replace the "___" with "/"
    link = link.replace("___", "/")
    # Replace the "---" with "?"
    link = link.replace("---", "?")
    # Replace the ".txt" with ".html"
    link = link.replace(".txt", ".html")
    # Add "https://..." to the beginning of the link
    link = "https://www.siemens-energy.com" + link

    return link

# Load environment variables from .env
load_dotenv()

# Define directories
current_dir = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(current_dir, "ALL_pages")

print(f"Books directory: {books_dir}")

# Ensure the books directory exists
if not os.path.exists(books_dir):
    raise FileNotFoundError(f"The directory {books_dir} does not exist. Please check the path.")

# Load all .txt files
book_files = [f for f in os.listdir(books_dir) if f.endswith(".txt")]
#book_files = ['documentos.txt'] # Replace with your actual file names
documents = []

for book_file in book_files:
    file_path = os.path.join(books_dir, book_file)
    loader = TextLoader(file_path, encoding="utf-8")
    book_docs = loader.load()
    for doc in book_docs:
        # Add source metadata without overwriting existing data
        doc.metadata.update({"source": process_source(book_file)})
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
    namespace="default"  
)
print("--- Finished creating and persisting vector store ---")
