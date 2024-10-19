from azure.storage.blob import BlobServiceClient
from openai import OpenAI
import os
import requests
from io import BytesIO
from PIL import Image
# Import module to track time
import time

client = OpenAI(api_key=os.environ.get("general_API"))

SAS_AZURE = os.environ.get("SAS_AZURE")
## Replace with your connection string
#connection_string = os.environ.get("AZURE_CONNECTION_STRING")
#container_name = "tilburgai"
#blob_name = "week1.mp4"  # The name of the file in the container (can be different from local file)
#local_file_path = "/Users/jonasklein/Desktop/EconomischeAanpak.png"
#
## Create a BlobServiceClient to interact with the storage account
#blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#
## Create a ContainerClient to interact with a specific container
#container_client = blob_service_client.get_container_client(container_name)
#
## Upload the file to the container
#with open(local_file_path, "rb") as data:
#    blob_client = container_client.get_blob_client(blob_name)
#    blob_client.upload_blob(data, overwrite=True)
#
#print(f"File {local_file_path} uploaded to blob {blob_name} in container {container_name}")

#download_file_path = "Downloaded_Video.mp4"
#
## Download the blob to a local file
#with open(download_file_path, "wb") as download_file:
#    download_stream = blob_client.download_blob()
#    download_file.write(download_stream.readall())
#
#print(f"Blob {blob_name} downloaded to {download_file_path}")

# Download the image from the URL
picture_name_1 = "EconomischeAanpak.png"
url1 = f"https://tilburgai.blob.core.windows.net/organisatieenstrategie/{picture_name_1}?{SAS_AZURE}"

picture_name_2 = "bookpage2.png"
url2 = f"https://tilburgai.blob.core.windows.net/organisatieenstrategie/{picture_name_2}?{SAS_AZURE}"

# Start time
start = time.time()

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Summarize this image"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://tilburgai.blob.core.windows.net/organisatieenstrategie/bookpage1.png?sp=racwdli&st=2024-09-26T09:47:16Z&se=2030-10-01T17:47:16Z&spr=https&sv=2022-11-02&sr=c&sig=RMUahAoyP2avFpytYKUb9SP1fP74EIUTDJxG4YNqv8s%3D",
          },
        },
      ],
    }
  ],
  stream=True
)

end = time.time()
print(f"Time taken with image: {end - start}\n============================\n")

for chunk in completion:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)

print("\n\n")

# Start time
start = time.time()

answer = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": 
     """
many. For several hundred years, scholars of scholarship had consid- ered that they might be like dwarves seeing farther by standing on the shoulders of giants, but they tended to believe more in rediscov- ery than in progress.
(p. 29)
Newton’s great achievement was to shift our understanding of the
world away from philosophical speculation to empirical analysis based on testable hypotheses. A similar process is currently happening in education where, in the last 30 years, findings from cognitive psychology have radically changed our understanding of how we learn. Up until relatively recently, pedagogy, and more specifically instructional
design was largely based on theory drawing on tangential fields such as philosophy, politics, sociology, anthropology, and linguistics, often to
the exclusion of research on psychology, cognition, and the brain. For example, Vygotsky’s theory of the zone of proximal development and
the idea that knowledge is socially constructed is a sine qua non in most teacher training courses while Baddeley’s model of working memory
is often omitted. Many teachers could go through their whole training without ever hearing about cognitive load theory despite the fact that Dylan Wiliam (2017) has referred to it as the “single most important thing that teachers need to know”.
Research on how we learn should endeavour to stand on the shoulders of giants and aim to move toward a broad consensus where multiple different disciplines converge on a common, agreed set of principles.
E. D. Hirsch (2002) refers to this as “the principle of independent convergence” which he claims
has always been the hallmark of dependable science. In the nineteenth century, for example, evidence from many directions converged on the germ theory of disease. Once policymakers accepted that consensus, hospital operating rooms, under penalty of being shut down, had to meet high standards of cleanliness. The case has been very different with schools.
We can see this convergence in some areas. For example, one of the most uncontested areas of research on learning is on the testing effect; the finding that retrieving something from our long-term memory is enhanced when the to-be-remembered information is retrieved through testing with proper feedback. This retrieval practice is possibly the most effective way of retaining knowledge and yet this discovery is often used poorly in schools with testing being used as the final endpoint
in a process of learning as opposed to a means of facilitating learning.

Summarize this text
"""}
  ],
  stream=True
)

end = time.time()
print(f"Time taken for only chat: {end - start}\n============================\n")

for chunk in answer:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)

