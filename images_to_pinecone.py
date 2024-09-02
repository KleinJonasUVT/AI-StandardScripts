import os
import base64
import requests
from pinecone import Pinecone
from openai import OpenAI
import uuid

# Initialize OpenAI API
openai_api_key = os.environ.get("general_API")
client = OpenAI(api_key=openai_api_key)

# Initialize Pinecone with your API key
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Define the Pinecone index name
index_name = "odcm"
index = pc.Index(index_name)

Broader_context = """It is an image with practical information about the course Online Data Collection and Management. It should be clearly explained what practical information is provided in the image."""

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
                        "text": f"""Describe this image very accurately.
                                {Broader_context}
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
def insert_to_pinecone(embedding, description, source):
    metadata = {
        "text": description,
        "page": "",
        "author": "Hannes Datta",
        "source": source
    }
    index.upsert(vectors=[{"id": str(uuid.uuid4()), "values": embedding, "metadata": metadata}])

# Path to the main folder containing subfolders with images
main_folder_path = "/Users/jonasklein/Library/CloudStorage/OneDrive-Personal/TilburgAI/AI-StandardScripts/images"

# Get a list of all subfolders in the main folder
subfolders = [f.path for f in os.scandir(main_folder_path) if f.is_dir()]

# Process each subfolder
for subfolder in subfolders:
    source_name = f"{os.path.basename(subfolder)}.pdf"
    print(f"\033[1mProcessing Folder:\033[0m {source_name}...")
    print("-----------------------------------------------------------------------------------------------------")

    # Get a list of all image files in the current subfolder
    image_files = [f for f in os.listdir(subfolder) if os.path.isfile(os.path.join(subfolder, f))]

    # Process each image in the subfolder
    for image_file in image_files:
        image_path = os.path.join(subfolder, image_file)
        
        print(f"\033[1mProcessing Image:\033[0m {image_file}...")

        # Encode the image
        base64_image = encode_image(image_path)

        # Get the image description from OpenAI
        description = get_image_description(base64_image)
        print(f"\033[1mDescription for {image_file}: \n \033[0m{description}")
        print("\n\n")

        # Get the embedding for the description
        embedding = get_text_embedding(description)
        print(f"Embedding for {image_file} created.")

        # Insert the embedding into Pinecone
        insert_to_pinecone(embedding, description, source_name)
        print(f"Description from {image_file} added to Pinecone under source '{source_name}'.")

print("All images in all folders processed and inserted into Pinecone.")

