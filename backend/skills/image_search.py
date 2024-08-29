import os
import requests
from typing import List
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def google_image_search(query: str) -> List[str]:
    service = build(
        "customsearch", "v1", developerKey=os.getenv("GOOGLE_API_KEY")
    )

    res = (
        service.cse()
        .list(
            q=query,
            cx=os.getenv("SEARCH_ENGINE_IDENTIFIER"),
            searchType="image"
        )
        .execute()
    )

    try:
        return [item['link'] for item in res['items']]
    except:
        return []


# print(google_image_search("dog"))
