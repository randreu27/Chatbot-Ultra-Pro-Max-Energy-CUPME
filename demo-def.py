from openai import OpenAI
import time
import ollama
from helper import extract_text_and_tables, add_chunk_to_database, retrieve


# # # Embedding Model Pull # # #
ollama.pull("hf.co/CompendiumLabs/bge-base-en-v1.5-gguf")

# # # Text Extraction (for PDFs) # # #
file_path = "8VM3BlueGIS.pdf"
file_path2 = "Bluegas-insulatedbusducts.pdf"
text, tables_as_text = extract_text_and_tables(file_path)
text2, tables_as_text2 = extract_text_and_tables(file_path2)

fragmentos = text.split("\n") + tables_as_text
fragmentos2 = text2.split("\n") + tables_as_text2

fragmentos = [f.strip() for f in fragmentos if f.strip()]
fragmentos2 = [f.strip() for f in fragmentos2 if f.strip()]

for chunk in fragmentos:
    add_chunk_to_database(chunk, file_path)
#print(f'Added chunks {len(fragmentos)} to the database')

for chunk in fragmentos2:
    add_chunk_to_database(chunk, file_path2)
#print(f'Added chunks {len(fragmentos2)} to the database')


# # # MAIN # # #
if __name__ == '__main__':
    end = False
    print('Hi! Im the Siemens Energy specialized ChatBot that searches information for you.')
    while not end:
        input_query = input('Do you have any questions? (To end the converstion just say "End") \n')
        if input_query == 'End' or input_query == 'end':
            break

        # # Question examples # #
        #input_query = 'How long should I wait to perform the first inspection after installing the 8VM3 Blue GIS?'
        #input_query = 'Can you tell me the technical details (voltage, frequency, ...) of 8VM3 Blue GIS?'
        #input_query = 'Can you tell me the technical details (voltage, frequency, ...) of Bluegas insulated busducts?'
        #input_query = 'Which is the recomended maintenance schedule of Bluegas insulated busducts?'
        retrieved_knowledge = retrieve(input_query)

        # # # Debbug code - Not definitive # # #
        #print('Retrieved knowledge:')
        #for chunk, similarity, source in retrieved_knowledge:
        #    print(f' - (similarity: {similarity:.2f}) [Source: {source}] {chunk}')

        # # # LLM # # #
        instruction_prompt = '''You are a helpful chatbot.
        Use only the following pieces of context to answer the question. In the same document could be explained multiple products, and if there are, don't mix up information. Don't make up any new information:
        {}
        '''.format('\n'.join([f' - (Source: {source}) {chunk}' for chunk, similarity, source in retrieved_knowledge]))

        print('Chatbot response:')
        client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
        )

        completion = client.chat.completions.create(
        extra_body={},
        #model="meta-llama/llama-3.3-70b-instruct:free",
        model="google/gemma-3-27b-it:free",
        messages=[
            {'role': 'system', 'content': instruction_prompt},
            {'role': 'user', 'content': input_query},
        ])
        print(completion.choices[0].message.content)
        time.sleep(3)