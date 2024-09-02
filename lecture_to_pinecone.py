from pdf2image import convert_from_path
import base64
import requests
from pinecone import Pinecone
from openai import OpenAI
import os
import uuid

# Initialize OpenAI API
openai_api_key = os.environ.get("general_API")
client = OpenAI(api_key=openai_api_key)

# Initialize Pinecone with your API key
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Define the Pinecone index name
index_name = "dprep"
index = pc.Index(index_name)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to upload the image to OpenAI API and get the description
def get_image_description(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",  # Ensure this model is available for image inputs
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Describe this image very accurately. It is a single slide from a PDF document.
                                The description will be used as context in a chatbot, so the description should cover the entire scope of the document.
                                Type all relevant text that appears in the image in your description/explanation.
                                The goal is for someone who cannot see the image to get a good understanding of the concept explained in the image, and that the description contains enough information to answer questions from students.
                                First, analyze the image and then explain the concept explained in the image.
                                Do thus not describe the layout of the image, but purely explain the concept in the image. Do not start with 'in the image...', but immediately start explaining the concept in the image."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Ensure that the response is successful and contains the required data
    if response.status_code == 200:
        result = response.json()
        if result.get("choices") and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
    return "Description not available"

# Function to get text embedding using OpenAI
def get_text_embedding(description):
    response = client.embeddings.create(
        input=description,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# Function to insert the embedding and metadata into Pinecone
def insert_to_pinecone(embedding, description, page, source):
    metadata = {
        "text": description,
        "page": page,
        "author": "Hannes Datta",
        "source": source
    }
    index.upsert(vectors=[{"id": str(uuid.uuid4()), "values": embedding, "metadata": metadata}])

# Convert PDF to images
pdf_path = "/Users/jonasklein/Library/CloudStorage/OneDrive-Persoonlijk/TilburgAI/dPrep/static/files/dPrep/tsh_make_cheatsheet.pdf"
filename = pdf_path.split("dPrep/")[-1]
images = convert_from_path(pdf_path)

# Specify the pages you want to process
pages_to_process = [1]  # Example: process only pages 1, 3, and 5

# Process specified pages, get the description, create the embedding, and insert it into Pinecone
for i in pages_to_process:
    if i - 1 < len(images):  # Ensure the page number is within the range of the document
        image = images[i - 1]
        image_path = f"page_{i}.jpg"
        image.save(image_path, "JPEG")
        
        print(f"Processing Page {i}...")

        # Encode the image
        base64_image = encode_image(image_path)

        # Get the image description from OpenAI
        description = get_image_description(base64_image)
        print(f"Description for Page {i}: {description}")

        # Get the embedding for the description
        embedding = get_text_embedding(description)
        print(f"Embedding for Page {i} created.")

        # Insert the embedding into Pinecone
        insert_to_pinecone(embedding, description, i, filename)
        print(f"Description from Page {i} added to Pinecone.")
    else:
        print(f"Page {i} is out of range. Skipping...")

print("Specified pages processed and inserted into Pinecone.")