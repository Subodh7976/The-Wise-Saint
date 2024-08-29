import os
import requests
from typing import List
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def google_search(query: str) -> List[str]:
    service = build(
        "customsearch", "v1", developerKey=os.getenv("GOOGLE_API_KEY")
    )

    res = (
        service.cse()
        .list(
            q=query,
            cx=os.getenv("SEARCH_ENGINE_IDENTIFIER"),
        )
        .execute()
    )

    try:
        return [item['link'] for item in res['items']]
    except:
        return []


def google_search_scrape(query: str) -> str:
    '''
    function performs a Google search for a given query and then scrapes the content from the most relevant search result. It fetches the URL of the first organic search result, retrieves the content of the page, and extracts the main text content using BeautifulSoup.

    Parameters:
        query (str): The text query for which the Google search is to be performed.

    Returns:
        str: The combined text content extracted from all paragraph tags (<p>) on the first search result page.
    '''

    links = google_search(query)

    if not links:
        return "Could not fetch any results!"

    page_text = ""
    for url in links[:3]:
        try:
            page_response = requests.get(url)
        except Exception as e:
            print(f"Got error for link: {url} - ", e)
            continue
        page_content = page_response.content

        soup = BeautifulSoup(page_content, "html.parser")

        paragraphs = soup.find_all('p')
        page_text += " ".join([para.get_text() for para in paragraphs])

    return page_text


# google_search_scrape("sample")