"""
something something docs

Ronik Bhaskar
"""

from litdb import LitDB
from db_entry import Entry
from renderer import render
from scraper import scrape

from tinydb import Query

import os
import re
from glob import glob
from concurrent.futures import ThreadPoolExecutor

litdb = LitDB()

def doc_id_to_string(doc_id):
    """
    gets associated entry, then generates string
    """

    entry = litdb.get_entry(doc_id=doc_id)
    return f"{doc_id}: {entry.title}. {entry.author}, {entry.date}. {entry.source}."

def search_substring(substring: str, directory: str) -> None:
    """
    Searches for substring in files in directory.
    Prints the db entry if it contains the substring.
    """

    print("thread")

    # strip off the trailing slash (linux, mac, or windows) and get the id
    doc_id = int(os.path.basename(re.sub(r"\$|/$", "", directory)))

    for text_file in glob(os.path.join(directory, "*")):
        with open(text_file, "r", encoding="utf-8") as f:
            if substring in f.read():
                print(doc_id_to_string(doc_id))
                break

def search_regex(regex: re.Pattern, directory: str) -> None:
    """
    Searches for regex in files in directory.
    Prints the db entry if it contains the substring.
    """

    # strip off the trailing slash (linux, mac, or windows) and get the id
    doc_id = int(os.path.basename(re.sub(r"\$|/$", "", directory)))

    for text_file in glob(os.path.join(directory, "*")):
        with open(text_file, "r", encoding="utf-8") as f:
            if regex.search(f.read()):
                print(doc_id_to_string(doc_id))
                break

def search(term: str | re.Pattern) -> None:
    """
    Searches all fields and files to find any matches for the term.
    
    term : str | re.Pattern
     - either a substring or a regex to search for
     
    Prints results, returns nothing.
    """

    if type(term) == re.Pattern:
        is_match = lambda x: bool(term.search(x))
        process = lambda x: search_regex(term, x)
    else:
        is_match = lambda x: term in x
        process = lambda x: search_substring(term, x)

    print("Results from db entries:")

    entries = litdb.search(~ (Query().name == "metadata"))
    for entry in entries:
        for k, v in entry.items():
            if is_match(k) or is_match(v):
                print(doc_id_to_string(entry.doc_id))
                break

    db_path = litdb.get(Query().name == "metadata")["db_path"]

    directories = list(glob(os.path.join(db_path, "*", "")))

    print("\nResults from saved files:")

    with ThreadPoolExecutor() as executor:
        executor.map(process, directories)

def render_doc_id(doc_id):
    """
    converts the associated document to HTML
    
    saves the HTML in index.html in the litdb directory
    """

    entry = litdb.get_entry(doc_id=doc_id)
    html = render(entry)

    db_path = litdb.get(Query().name == "metadata")["db_path"]
    html_path = os.path.join(db_path, "index.html")

    with open(html_path, "w") as f:
        f.write(html)

    print(f"HTML rendering has been saved to {html_path}")