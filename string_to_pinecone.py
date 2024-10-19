from openai import OpenAI
from pinecone import Pinecone
import os
import uuid

# Initialiseer Pinecone met je API-sleutel
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Initialiseer OpenAI met je API-sleutel
client = OpenAI(api_key=os.environ.get("general_API"))

# Define the text and source
text = """
This image presents a **methodological framework for collecting web data**. It is structured as an inverted funnel that represents a balance between two key aspects: **technical feasibility** and **legal and ethical risks**. The ultimate goal is to ensure the **validity** of the data collection process.

The framework is divided into three main stages:

1. **Source Selection** (Table 2):
   - This stage involves choosing which data sources to use.
   - Key questions to consider:
     - **Has the universe of potential data sources been sufficiently explored?** (#1.1)
     - **Have alternatives to web scraping been considered?** (#1.2)
     - **Have the complexities of the data context been sufficiently mapped?** (#1.3)

2. **Collection Design** (Table 3):
   - This stage focuses on designing how data will be collected from the selected sources.
   - Key questions to consider:
     - **Which information to extract?** (#2.1)
     - **How to sample?** (#2.2)
     - **At what frequency to extract information?** (#2.3)
     - **How to process the information during extraction?** (#2.4)

3. **Data Extraction** (Table 4):
   - This stage deals with the actual process of extracting data and ensuring its quality.
   - Key questions to consider:
     - **How to improve the performance of the extraction?** (#3.1)
     - **How to monitor data quality during extraction?** (#3.2)
     - **How to document the data during and after extraction?** (#3.3)

The framework's objective is to ensure that the process of collecting web data is methodologically sound, legally and ethically compliant, and technically feasible, leading to valid results.
"""
source = "FieldsOfGold.pdf"
page = "6"

# Make embeddings for the text
def get_text_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    embedding = response.data[0].embedding
    return embedding

embedding = get_text_embedding(text)
print(embedding)

# Define the index name
index_name = "odcm"

index = pc.Index(index_name)

# Insert the embedding into Pinecone
def insert_to_pinecone(index, embedding, text, source, page):
    # Prepare the metadata
    metadata = {
        "text": text,
        "page": page,
        "author": "Hannes Datta",
        "source": source
    }
    
    # Upsert the vector to Pinecone, with generating a random ID
    index.upsert(vectors=[{"id": str(uuid.uuid4()), "values": embedding, "metadata": metadata}])

# Insert the embedding and metadata
insert_to_pinecone(index, embedding, text, source, page)
print("Text embedding inserted into Pinecone successfully!")