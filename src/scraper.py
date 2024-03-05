"""
something something docs

Ronik Bhaskar
"""

from db_entry import Entry

import requests
from bs4 import BeautifulSoup
from enum import Enum
import json
import re
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
]

class Source(Enum):
    """
    enumeration of all sources that are able to be scraped
    """
    POETRY_FOUNDATION = 1
    TEXT = 2
    HTML = 3

def scrape_poetry_foundation(url: str) -> Entry:
    """
    scrape poems from the Poetry Foundation website
    takes url from poetryfoundation.org
    returns partially-completed Entry
    """

    # initial scrape
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    

    # parse non-content sections for db entry
    c_txt_attribution = soup.find("span", class_="c-txt_attribution")

    c_txt_note = soup.find("span", class_="c-txt_note")
    if c_txt_note:
        c_txt_note = c_txt_note.get_text()

    h1 = soup.find("h1")

    script = soup.find("script", attrs={"type": "application/ld+json"}).get_text()
    obj = json.loads(script)

    for tag in obj["@graph"]:
        if tag["@type"] == "CreativeWork":
            info = tag
            break

    # parse title
    if "name" in info:
        title = info["name"]
    elif h1:
        title = h1.get_text()
    else:
        title = None
    
    # parse author
    if "author" in info and "name" in info["author"]:
        author = info["author"]["name"]
    elif c_txt_attribution:
        author_tag = c_txt_attribution.find("a")
        if author_tag: # can't find any that don't have link
            author = author_tag.get_text()
        else:
            author = None
    else:
        author = None

    # parse date published
    if "datePublished" in info:
        date = info["datePublished"]
    elif c_txt_note:
        dateRe = re.compile("Copyright © (\d{4})")
        date = re.search(dateRe, c_txt_note)
        if date:
            date = date.group(1)
        else:
            date = None
    else:
        date = None

    # parse content of poem
    poem_div = soup.find("div", class_="o-poem")
    lines = poem_div.findAll("div")
    poem = "\n".join((line.get_text().strip() for line in lines))

    return Entry(title=title, author=author, date=date, source=url, contents=poem)

def scrape_text(url: str) -> Entry:
    """
    scrapes text file resource from web
    returns partially-completed Entry
    """
    # initial scrape
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
    }
    page = requests.get(url, headers=headers)

    return Entry(source=url, contents=page.text)

def scrape_html(url: str) -> Entry:
    """
    default option for the web scraper
    takes all the paragraphs and headers from a webpage
    returns partially-completed Entry
    """

    # initial scrape
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    # grab all paragraphs and headers
    text_elements = soup.findAll(re.compile("(p)|(h\d)"))
    body = "\n".join((el.get_text().strip() for el in text_elements))

    return Entry(source=url, contents=body)

# jump table of web scrapers
SCRAPE_FUNCTIONS = {
    Source.POETRY_FOUNDATION: scrape_poetry_foundation,
    Source.TEXT: scrape_text,
    Source.HTML: scrape_html
}

def scrape(url : str, source: Source=None) -> Entry:
    """
    web scraping function
    attempts to predict the source if one is not provided
    """

    if source is None:
        if "poetryfoundation" in url:
            source = Source.POETRY_FOUNDATION
        elif url.endswith(".txt"):
            source = Source.TEXT
        else:
            source = Source.HTML
        
    return SCRAPE_FUNCTIONS[source](url)
