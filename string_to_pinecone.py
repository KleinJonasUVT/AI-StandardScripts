from openai import OpenAI
from pinecone import Pinecone
import os
import uuid

# Initialiseer Pinecone met je API-sleutel
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Initialiseer OpenAI met je API-sleutel
client = OpenAI(api_key=os.environ.get("general_API"))

# Define the text and source
text = """Contents of the first week of the Online Data Collection and Management course.
The first week has the following content:
The document outlines information related to the "Online Data Collection and Management" course, specifically focusing on the first week's topic: "Getting started with Python and web data." 

**Learning Goals:** 
- Participants are expected to familiarize themselves with Python programming.
- They will learn how to launch Jupyter Notebook and run code in Visual Studio Code.
- The course addresses when it is beneficial to use Google Colab in comparison to Jupyter Notebook.
- Basic programming concepts in Python relevant to web data collection will be covered.

**Preparation Before the Lecture:** 
- Students must ensure they complete all required preparations, including installing necessary software using Datacamp licenses prior to attending the lecture.

**Lecture Requirements:**
- A laptop is required for participation.
- The lecture will include an introduction to the course and a tutorial titled "Python bootcamp for web data," available for download and through Google Colab.

**Downloading and Starting the Tutorial:**
- Instructions for downloading the tutorial involve right-clicking a link, selecting the appropriate download option, and saving the file in a convenient location.
- If the downloaded file is in a compressed format (.zip), it must be unzipped.
- Participants should then open Jupyter Notebook, navigate to their saved file, and begin the tutorial.

**After the Lecture:**
- Students are encouraged to work through the in-class tutorial at their own pace.
- They should continue to enhance their understanding of basic programming concepts by completing online tutorials on Datacamp, which is estimated to take around three hours, focusing on the first three chapters only.

**Premium Access to Datacamp:**
- The document notes that students can access premium content from Datacamp through their university email accounts, providing an opportunity to utilize resources typically reserved for paid subscriptions.

This comprehensive overview ensures that students have the necessary context and instructions to engage with the course effectively."""
source = "Week 1) Getting started _ Online Data Collections (oDCM).pdf"

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
def insert_to_pinecone(index, embedding, text, source):
    # Prepare the metadata
    metadata = {
        "text": text,
        "page": "",
        "author": "Hannes Datta",
        "source": source
    }
    
    # Upsert the vector to Pinecone, with generating a random ID
    index.upsert(vectors=[{"id": str(uuid.uuid4()), "values": embedding, "metadata": metadata}])

# Insert the embedding and metadata
insert_to_pinecone(index, embedding, text, source)
print("Text embedding inserted into Pinecone successfully!")