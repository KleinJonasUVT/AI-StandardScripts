import time
import os
import requests
from bs4 import BeautifulSoup
import pymysql

def connect_to_db():
    connection = pymysql.connect(
        host = "gateway01.eu-central-1.prod.aws.tidbcloud.com",
        port = 4000,
        user = os.environ.get("TIDB_USER"),
        password = os.environ.get("TIDB_PASSWORD"),
        database = "ragdocuments",
        ssl_verify_cert = True,
        ssl_verify_identity = True,
        ssl_ca = os.environ.get("SSL_CA")
        )
    return connection

# Define the initial URL
url = 'https://francescolelli.info/news/'

# Initialize an empty list to store hrefs
hrefs = []

# Loop until there is no previous button
while True:
    # Get the HTML of the current URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all article tags in the main section
    articles = soup.find('main').find_all('article')

    # Add all hrefs in the articles to the hrefs list
    hrefs.extend(article.find('a')['href'] for article in articles)

    # Find the previous button
    previous_button = soup.find('li', class_='previous')
    
    # Update the URL to the previous page's URL
    try:
        url = previous_button.find('a')['href']
    except TypeError:
        break
    
    # Print the current state (optional, for debugging)
    print(f"Collected {len(hrefs)} links so far.")
    print(f"Next URL: {url}")

# For each href, get the HTML of the article and store it in a file
for i, href in enumerate(hrefs):
    response = requests.get(href)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the content of the article and strip text
    content = soup.find('div', id='content').get_text().strip()
    connection = connect_to_db()
    with connection.cursor() as cursor:
            sql = """
                INSERT INTO ragdocuments.lelli_web (source, parts, author) VALUES (%s, %s, %s);
                """
            cursor.execute(sql, (href, content, "Francesco Lelli"))
            connection.commit()
            print(f"Inserted article {i + 1}/{len(hrefs)} into the database.")

    # Sleep for a while to avoid overwhelming the server
    time.sleep(1)




