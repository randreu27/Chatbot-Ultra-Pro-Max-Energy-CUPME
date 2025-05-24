import os
from dotenv import load_dotenv
from langchain.text_splitter import TokenTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.graph_transformers.llm import SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_experimental.graph_transformers.llm import JsonOutputParser, PromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
import json

load_dotenv()

# Instantiate the Neo4JGraph to persist the data
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URL"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# Define directories
current_dir = os.path.dirname(os.path.abspath(__file__))
products_dir = os.path.join(current_dir, "product-offerings")

print(f"Products directory: {products_dir}")

# Ensure the products directory exists
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

# Instantiate the token text splitter
splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)

# Load all .txt files
product_files = [f for f in os.listdir(products_dir) if f.endswith(".txt")]
documents = []

print("Loading product files...")
for product_file in product_files:
    file_path = os.path.join(products_dir, product_file)
    loader = TextLoader(file_path, encoding="utf-8")
    product_docs = loader.load()
    
    for doc in product_docs:
        # Add source metadata without overwriting existing data
        doc.metadata.update({"source": get_source(product_file)})
    
    # Split the documents
    split_docs = splitter.split_documents(product_docs)
    documents.extend(split_docs)


# Instantiate LLM to use with the LLMGraphTransformer
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)

# Create a system message to provide the LLM with the instructions
system_prompt = """
You are a data scientist working for Siemens Energy and you are building a knowledge graph database of their products, solutions, and services.
Your task is to extract information from technical documents and convert it into a knowledge graph database.
Provide a set of Nodes in the form [head, head_type, relation, tail, tail_type].
It is important that the head and tail exists as nodes that are related by the relation.
If you can't pair a relationship with a pair of nodes don't add it.
When you find a node or relationship you want to add try to create a generic TYPE for it that describes the entity you can also think of it as a label.
You must generate the output in a JSON format containing a list with JSON objects. Each object should have the keys: "head", "head_type", "relation", "tail", and "tail_type".
"""

system_message = SystemMessage(content=system_prompt)

# Create a Pydantic class for structured relation extraction
class SiemensEnergyRelation(BaseModel):
    head: str = Field(
        description=(
            "Extracted head entity like Product, Component, Service, Application, Industry, etc."
            "Must use human-readable unique identifier."
        )
    )
    head_type: str = Field(
        description="Type of the extracted head entity like Product, Component, Service, Application, Industry, etc."
    )
    relation: str = Field(description="Relation between the head and the tail entities")
    tail: str = Field(
        description=(
            "Extracted tail entity like Product, Component, Service, Application, Industry, etc."
            "Must use human-readable unique identifier."
        )
    )
    tail_type: str = Field(
        description="Type of the extracted tail entity like Product, Component, Service, Application, Industry, etc."
    )

# Instantiate the parser with our Pydantic class to provide the LLM with the format instructions
parser = JsonOutputParser(pydantic_object=SiemensEnergyRelation)

# Define examples to guide the model
examples = [
    {
        "text": (
            "The SGT-800 gas turbine offers excellent performance for power generation, "
            "with an electrical efficiency of 39% and power output of 54 MW."
        ),
        "head": "SGT-800",
        "head_type": "Product",
        "relation": "HAS_SPECIFICATION",
        "tail": "54 MW",
        "tail_type": "PowerOutput",
    },
    {
        "text": (
            "The SGT-800 gas turbine offers excellent performance for power generation, "
            "with an electrical efficiency of 39% and power output of 54 MW."
        ),
        "head": "SGT-800",
        "head_type": "Product",
        "relation": "HAS_SPECIFICATION",
        "tail": "39%",
        "tail_type": "Efficiency",
    },
    {
        "text": (
            "The SGT-800 gas turbine offers excellent performance for power generation, "
            "with an electrical efficiency of 39% and power output of 54 MW."
        ),
        "head": "SGT-800",
        "head_type": "Product",
        "relation": "USED_IN",
        "tail": "Power Generation",
        "tail_type": "Application",
    },
    {
        "text": (
            "Siemens Energy's SIESTART solution combines battery energy storage with the SGT-A45 "
            "mobile gas turbine to provide black start capability for power plants."
        ),
        "head": "SIESTART",
        "head_type": "Solution",
        "relation": "INCLUDES",
        "tail": "Battery Energy Storage",
        "tail_type": "Component",
    },
    {
        "text": (
            "Siemens Energy's SIESTART solution combines battery energy storage with the SGT-A45 "
            "mobile gas turbine to provide black start capability for power plants."
        ),
        "head": "SIESTART",
        "head_type": "Solution",
        "relation": "INCLUDES",
        "tail": "SGT-A45",
        "tail_type": "Product",
    },
    {
        "text": (
            "Siemens Energy's SIESTART solution combines battery energy storage with the SGT-A45 "
            "mobile gas turbine to provide black start capability for power plants."
        ),
        "head": "SIESTART",
        "head_type": "Solution",
        "relation": "PROVIDES",
        "tail": "Black Start Capability",
        "tail_type": "Feature",
    },
    {
        "text": (
            "The SST-6000 steam turbine is compatible with the SGT-8000H gas turbine in combined cycle power plants, "
            "increasing overall plant efficiency to over 63%."
        ),
        "head": "SST-6000",
        "head_type": "Product",
        "relation": "COMPATIBLE_WITH",
        "tail": "SGT-8000H",
        "tail_type": "Product",
    },
    {
        "text": (
            "The SST-6000 steam turbine is compatible with the SGT-8000H gas turbine in combined cycle power plants, "
            "increasing overall plant efficiency to over 63%."
        ),
        "head": "SST-6000",
        "head_type": "Product",
        "relation": "USED_IN",
        "tail": "Combined Cycle Power Plants",
        "tail_type": "Application",
    },
    {
        "text": (
            "The OMNIVISE Digital Services Suite provides predictive maintenance for Siemens gas turbines, "
            "helping customers reduce maintenance costs by up to 20%."
        ),
        "head": "OMNIVISE",
        "head_type": "Service",
        "relation": "APPLIES_TO",
        "tail": "Siemens Gas Turbines",
        "tail_type": "ProductCategory",
    },
    {
        "text": (
            "The OMNIVISE Digital Services Suite provides predictive maintenance for Siemens gas turbines, "
            "helping customers reduce maintenance costs by up to 20%."
        ),
        "head": "OMNIVISE",
        "head_type": "Service",
        "relation": "PROVIDES",
        "tail": "Predictive Maintenance",
        "tail_type": "Feature",
    },
    {
        "text": (
            "Siemens Energy's SPPA-T3000 control system is installed in over 1,800 power plants worldwide, "
            "providing comprehensive automation for all types of power generation."
        ),
        "head": "SPPA-T3000",
        "head_type": "Product",
        "relation": "PROVIDES",
        "tail": "Automation",
        "tail_type": "Feature",
    },
    {
        "text": (
            "Siemens Energy's SPPA-T3000 control system is installed in over 1,800 power plants worldwide, "
            "providing comprehensive automation for all types of power generation."
        ),
        "head": "SPPA-T3000",
        "head_type": "Product",
        "relation": "USED_IN",
        "tail": "Power Plants",
        "tail_type": "Application",
    }
]

# Instantiate the human prompt template using the examples and Pydantic class with format instructions
human_prompt = PromptTemplate(
    template="""
Examples:
{examples}

For the following text, extract entities and relations relevant to Siemens Energy products, components, services, and applications.
Focus on identifying:
1. Products (turbines, generators, transformers, control systems, etc.)
2. Product specifications (power output, efficiency, emissions, dimensions)
3. Components that make up products
4. Applications and industries where products are used
5. Services related to products
6. Features and benefits of products
7. Compatibility between products
8. Manufacturing or service locations

{format_instructions}\nText: {input}""",
    input_variables=["input"],
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
        "node_labels": None,
        "rel_types": None,
        "examples": examples,
    },
)

# Instantiate the human message prompt to provide the LLM with the instructions and examples
human_message_prompt = HumanMessagePromptTemplate(prompt=human_prompt)

# Create a chat_prompt combining the system and human messages to use with the LLMGraphTransformer
chat_prompt = ChatPromptTemplate.from_messages(
    [system_message, human_message_prompt]
)

# Instantiate the LLMGraphTransformer that will extract the entities and relationships from the Documents
llm_transformer = LLMGraphTransformer(llm=llm, prompt=chat_prompt)

# Convert the Documents into Graph Documents
print("Converting documents to graph documents...")
graph_documents = llm_transformer.convert_to_graph_documents(documents)

# Persist the Graph Documents into the Neo4JGraph
print("Storing graph documents in Neo4j...")
graph.add_graph_documents(
  graph_documents,
  baseEntityLabel=True,
  include_source=True
)
