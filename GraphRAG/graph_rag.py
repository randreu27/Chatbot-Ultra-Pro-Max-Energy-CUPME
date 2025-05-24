import os
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
# Connect to Neo4j graph
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URL"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# Create LLM instance
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)

# Create a QA chain that translates natural language into Cypher queries
qa_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=False,
    allow_dangerous_requests=True,
    return_intermediate_steps=True
)

def query_siemens_knowledge_graph(question):
    """
    Query the Siemens Energy knowledge graph with natural language.
    Returns both the Cypher query generated and the final answer.
    """
    # Execute the chain
    result = qa_chain.invoke(question)
    
    # Extract and print the generated Cypher query
    cypher_query = result["intermediate_steps"][0]["query"]
    # print(f"Generated Cypher Query:\n{cypher_query}\n")
    
    # Return the answer
    return result["result"]

# Example queries
# example_queries = [
#     "What products does Siemens Energy offer?",
#     "What is the utilitiy of Compressors?",
#     "What are the compatible components for the SGT-8000H gas turbine?",
#     "What services does Siemens provide for maintenance?",
#     "Which products are used in combined cycle power plants?"
# ]

# Execute example query
if __name__ == "__main__":
    print("Siemens Energy Knowledge Graph Query System")
    print("------------------------------------------")
    user_query = None
    while True:
        
        # Let user choose a query or write their own
        # print("Example queries:")
        # for i, query in enumerate(example_queries):
        #     print(f"{i+1}. {query}")
        
        user_query = input("Enter your query about Siemens Energy products: ")
        if user_query=="exit":
            break
        answer = query_siemens_knowledge_graph(user_query)
        print(f"Answer: {answer}")