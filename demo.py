from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from pdfminer.high_level import extract_text
import base64
import io
import os
import concurrent.futures
from tqdm import tqdm
import re
import pandas as pd 
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np
from rich import print
from ast import literal_eval
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import ollama
import pdfplumber

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

file_path = "8VM3BlueGIS.pdf"
text, tables_as_text = extract_text_and_tables(file_path)

fragmentos = text.split("\n") + tables_as_text  # Se combinan los fragmentos normales con los de las tablas

# Filtrar fragmentos vacíos
fragmentos = [f.strip() for f in fragmentos if f.strip()]

VECTOR_DB = []

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Humanish-LLama3-8B-Instruct-GGUF'

VECTOR_DB = []

MAX_CHUNK_LENGTH = 1500  # Ajusta este valor según el modelo

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


for chunk in fragmentos:
    add_chunk_to_database(chunk, file_path)
print(f'Added chunks {len(fragmentos)} to the database')

def cosine_similarity(a, b):
  dot_product = sum([x * y for x, y in zip(a, b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)

def retrieve(query, top_n=20):
    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
    similarities = []
    
    for chunk, embedding, source in VECTOR_DB:
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, similarity, source))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_n]

#input_query = input('Ask me a question: ')
input_query = 'How long should I wait to perform the first inspection after installing the 8VM3 Blue GIS?'
#input_query = 'Can you explain me the technical details of 8VM3 Blue GIS?'
retrieved_knowledge = retrieve(input_query)

print('Retrieved knowledge:')
for chunk, similarity, source in retrieved_knowledge:
    print(f' - (similarity: {similarity:.2f}) [Source: {source}] {chunk}')

instruction_prompt = f'''You are a helpful chatbot.
Use only the following pieces of context to answer the question. Don't make up any new information:
{'\n'.join([f' - (Source: {source}) {chunk}' for chunk, similarity, source in retrieved_knowledge])}
'''

stream = ollama.chat(
  model=LANGUAGE_MODEL,
  messages=[
    {'role': 'system', 'content': instruction_prompt},
    {'role': 'user', 'content': input_query},
  ],
  stream=True,
)

# print the response from the chatbot in real-time
print('Chatbot response:')
for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)