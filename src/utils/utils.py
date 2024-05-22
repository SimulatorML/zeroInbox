from bs4 import BeautifulSoup
import requests
from pytube import YouTube


def extract_text_from_url(url: str, limit: int = 2000) -> str:
    """
    Extract text from provided URL.

    Args:
        url (str): URL to parse.
        limit (int, optional): Word limit in the output. Defaults to 2000.

    Returns:
        str: Parsed text from the URL.
    """
    content = requests.get(url).text

    soup = BeautifulSoup(content, "html.parser")
    paragraphs = soup.find_all("p")
    text = "\n".join([p.get_text() for p in paragraphs])[:limit]
    return text


def extract_description_from_yt(url: str) -> str:
    """
    Extract description from YouTube link.

    Args:
        url (str): Valid YouTube link.

    Returns:
        str: Video description.
    """
    yt = YouTube(url)
    for n in range(6):
        try:
            description = yt.initial_data["engagementPanels"][n][
                "engagementPanelSectionListRenderer"
            ]["content"]["structuredDescriptionContentRenderer"]["items"][1][
                "expandableVideoDescriptionBodyRenderer"
            ][
                "attributedDescriptionBodyText"
            ][
                "content"
            ]
            return yt.title + " " + description
        except:
            continue
    return False
