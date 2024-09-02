from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from pinecone import Pinecone
import os
import uuid

# Load your PDF
loader = PyPDFLoader("FieldsOfGold.pdf")

# Set up your text embedding model
model = OpenAIEmbeddings(openai_api_key=os.environ.get("general_API"), model="text-embedding-3-large")

# Set up your text splitter
text_splitter = SemanticChunker(model, breakpoint_threshold_type="percentile", breakpoint_threshold_amount=85)

# Initialize Pinecone with your API key
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Define the Pinecone index name
index_name = "bpi"
index = pc.Index(index_name)

# Function to get text embedding using OpenAI
def get_text_embedding(text):
    response = model.embed(text)
    embedding = response[0]['embedding']
    return embedding

# Function to insert the embedding and metadata into Pinecone
def insert_to_pinecone(embedding, text, page, source):
    metadata = {
        "text": text,
        "page": page,
        "author": "Johannes Boegershausen, Hannes Datta, Abhishek Borah and Andrew T. Stephen",
        "source": source
    }
    index.upsert(vectors=[{"id": str(uuid.uuid4()), "values": embedding, "metadata": metadata}])

# Load the PDF pages
pages = loader.load()

# Iterate over each page, split it into semantic chunks, and store them in Pinecone
for i, page in enumerate(pages):
    text = page.page_content
    print(f"Processing Page {i + 1}...")

    # Split the text into semantic chunks
    docs = text_splitter.split_text(text)

    # Process each chunk
    for doc in docs:
        # Get the embedding for the chunk
        embedding = get_text_embedding(doc)

        # Insert the embedding into Pinecone
        insert_to_pinecone(embedding, doc, i + 1, "FieldsOfGold.pdf")
        print(f"Chunk from Page {i + 1} added to Pinecone.")

print("All pages processed and inserted into Pinecone.")
