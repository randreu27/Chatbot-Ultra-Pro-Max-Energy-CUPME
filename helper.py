import ollama
import pdfplumber
import pandas as pd


# # # Auxiliary Variables - Constants # # #
VECTOR_DB = []
EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
MAX_CHUNK_LENGTH = 1500


# # # Text Extraction Functions (for PDFs) # # #
def extract_text_and_tables(path):
    text = ""
    tables_as_text = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            # Extraer texto de la página
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

            # Extraer tablas y convertirlas a texto estructurado
            page_tables = page.extract_tables()
            for table in page_tables:
                df = pd.DataFrame(table)  # Convertir tabla a DataFrame
                table_text = df.to_string(index=False, header=False)  # Convertir a texto sin índices ni cabecera
                tables_as_text.append(table_text)

    return text, tables_as_text


# # # RAG Text Processing Functions # # #
def truncate_chunk(chunk, max_length=MAX_CHUNK_LENGTH):
    return chunk[:max_length]  # Recortar al máximo permitido

def add_chunk_to_database(chunk, source):
    chunk = truncate_chunk(chunk)  # Truncar si es demasiado largo
    if chunk.strip():  
        try:
            response = ollama.embed(model=EMBEDDING_MODEL, input=chunk)
            if 'embeddings' in response and response['embeddings']:
                embedding = response['embeddings'][0]
                VECTOR_DB.append((chunk, embedding, source))
        except Exception as e:
            print(f"Error al procesar chunk: {e}")


# # # Retrieval Functions # # #
def cosine_similarity(a, b):
  dot_product = sum([x * y for x, y in zip(a, b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)

def retrieve(query, top_n=30):
    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
    similarities = []
    
    for chunk, embedding, source in VECTOR_DB:
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, similarity, source))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_n]