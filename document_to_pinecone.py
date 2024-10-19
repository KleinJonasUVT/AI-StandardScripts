from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from openai import OpenAI
from pinecone import Pinecone
import os
import uuid

# Load your PDF
loader = PyPDFLoader("/Users/jonasklein/Library/CloudStorage/OneDrive-Personal/TilburgAI/lerarenopleiding/static/files/lerarenopleiding/KirschnerHendrick_HowLearningHappens.pdf")

# Set up your text embedding model
client = OpenAI(api_key=os.environ.get("general_API"))


# Set up your text splitter
text_splitter = CharacterTextSplitter(
    separator="\n\n"
)

# Initialize Pinecone with your API key
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Define the Pinecone index name
index_name = "lerarenopleiding"
index = pc.Index(index_name)

# Function to get text embedding using OpenAI
def get_text_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    embedding = response.data[0].embedding
    return embedding

# Function to insert the embedding and metadata into Pinecone
def insert_to_pinecone(embedding, text, page, source):
    metadata = {
        "text": text,
        "page": page,
        "author": "Paul Kirschner & Carl Hendrick",
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
    for j, doc in enumerate(docs):
        # Get the embedding for the chunk
        embedding = get_text_embedding(doc)

        # Insert the embedding into Pinecone
        insert_to_pinecone(embedding, doc, i + 1, "KirschnerHendrick_HowLearningHappens.pdf")
        print(f"Chunk {j + 1} from Page {i + 1} added to Pinecone.")

print("All pages processed and inserted into Pinecone.")
