from azure.storage.blob import BlobServiceClient
from flask import Flask, send_file, abort, render_template, send_from_directory
import os
from io import BytesIO

# Configuration (replace with your details)
AZURE_CONNECTION_STRING = os.environ.get("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "organisatieenstrategie"
BLOB_NAME = "Organisatie_en_strategie2024Syllabus.pdf"
VIDEO_BLOB_NAME = "week1.mp4"
STATIC_FOLDER = "static/files"

# Initialize Azure Blob client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-pdf')
def get_pdf():
    #try:
        # Download the PDF from Azure Blob Storage
        blob_client = container_client.get_blob_client(BLOB_NAME)
        pdf_stream = BytesIO()
        blob_data = blob_client.download_blob()
        blob_data.readinto(pdf_stream)
        pdf_stream.seek(0)

        # Send the PDF file securely
        return send_file(pdf_stream, mimetype='application/pdf')
    #except Exception as e:
    #    print(f"Error: {e}")
    #    abort(404)

@app.route('/get-video')
def get_video():
    try:
        # Download the video from Azure Blob Storage
        blob_client = container_client.get_blob_client(VIDEO_BLOB_NAME)
        video_path = os.path.join(STATIC_FOLDER, VIDEO_BLOB_NAME)

        # Check if the video already exists
        if not os.path.exists(video_path):
            # Create the static folder if it does not exist
            if not os.path.exists(STATIC_FOLDER):
                os.makedirs(STATIC_FOLDER)

            # Download the video and save it to the static folder
            with open(video_path, 'wb') as video_file:
                blob_data = blob_client.download_blob()
                blob_data.readinto(video_file)

        # Send the video file securely
        return send_from_directory(STATIC_FOLDER, VIDEO_BLOB_NAME)
    except Exception as e:
        print(f"Error: {e}")
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
