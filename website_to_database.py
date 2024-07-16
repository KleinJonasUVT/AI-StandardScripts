import time
import os
import requests
from bs4 import BeautifulSoup

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
    content = soup.find('div', id='content')
    with connection.cursor() as cursor:
            sql = """
                INSERT INTO ragdocuments.odcm (parts, source, page, author) VALUES (%s, %s, %s, %s);
                """
            cursor.execute(sql, (doc, "FieldsOfGold.pdf", i + 1, "Johannes Boegershausen, Hannes Datta, Abhishek Borah and Andrew T. Stephen"))
            connection.commit()

    # Sleep for a while to avoid overwhelming the server
    time.sleep(1)




