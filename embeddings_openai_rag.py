from openai import OpenAI
import pandas as pd
import pymysql
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Set your OpenAI API key here
client = OpenAI(api_key=os.environ.get("general_API"))
EMBEDDING_MODEL = "text-embedding-3-small"

# Connect to TiDB database function
def connect_to_db():
    connection = pymysql.connect(
        host = "gateway01.eu-central-1.prod.aws.tidbcloud.com",
        port = 4000,
        user = os.environ.get("TIDB_USER"),
        password = os.environ.get("TIDB_PASSWORD"),
        database = "ragdocuments",
        ssl_verify_cert = True,
        ssl_verify_identity = True,
        ssl_ca = "/etc/ssl/cert.pem"
        )
    return connection

# Load data from SQL
def load_from_sql():
    connection = connect_to_db()
    df = pd.read_sql(f"SELECT parts FROM lelli_web", con=connection)
    return df

# Function to save embeddings to SQL
def save_embeddings_to_sql(df):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        for index, row in df.iterrows():
            description = row["parts"]
            embedding = client.embeddings.create(input = description, model=EMBEDDING_MODEL).data[0].embedding

            embedding_str = ' '.join(map(str, embedding))
            
            # Update the embedding in the embeddings table
            sql = """
            UPDATE lelli_web 
            SET embedding = %s 
            WHERE parts = %s;
            """
            cursor.execute(sql, (embedding_str, description))
            print(f"Embedding added to SQL")
        
            # Commit the transaction to ensure the changes are saved
            connection.commit()

# Call the function to save embeddings to SQL
df = load_from_sql()
save_embeddings_to_sql(df)
print("Successfully added embeddings to SQL")