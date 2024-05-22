from bs4 import BeautifulSoup
import requests
from pytube import YouTube


def extract_text_from_url(url, limit=2000):
    content = requests.get(url).text

    soup = BeautifulSoup(content, "html.parser")
    paragraphs = soup.find_all("p")
    text = "\n".join([p.get_text() for p in paragraphs])[:limit]
    return text


def extract_description_from_yt(url):
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
