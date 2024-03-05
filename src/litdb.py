"""
something something docs

Ronik Bhaskar
"""

from tinydb import TinyDB, Query
from tinydb.table import Document
from db_entry import Entry
from scraper import scrape
import os
import shutil

DEFAULT_DB_NAME = "litdb"
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), DEFAULT_DB_NAME)
DEFAULT_DB_JSON = os.path.join(DEFAULT_DB_PATH, "db.json")
METADATA = "metadata"
CONTENTS_FILE = "contents.txt"
NOTES_FILE = "notes.md"

class LitDB(TinyDB):

    def __init__(self, json_path=None, db_path=None):

        json_path = json_path if json_path else DEFAULT_DB_JSON
        super().__init__(json_path)
        
        metadata_query = Query().name == METADATA
        metadata = self.get(metadata_query)

        if metadata and metadata.get("db_path") and not db_path:
            return
        else:
            db_path = DEFAULT_DB_PATH
            self.upsert({"name": METADATA, "db_path": db_path}, metadata_query)

    def get_entry(self, *args, **kwargs) -> Entry:
        """
        wrapper around get
        Returns an Entry rather than a Document
        """

        doc = self.get(*args, **kwargs)

        return Entry.from_doc(doc)

    def get_doc(self, entry : Entry) -> Document | None:
        """
        given an Entry, attempts to find the corresponding Document
        
        Returns Optional[Document]
        """

        if not entry.doc_id is None:
            return self.get(doc_id=entry.doc_id)
        elif not entry.source is None:
            return self.get(Query().source == entry.source)
        elif not entry.title is None and not entry.author is None:
            return self.get(Query().fragment(entry.to_dict()))
        
        return None


    def save(self, entry: Entry, overwrite: bool=False) -> int:
        """
        First checks if an entry exists. 
        If it does and overwrite is False, then only None fields are updated.
        If it does not exist or overwrite is True, the entry is saved in the database.
        The contents and notes are saved in separate text files.

        entry : Entry
         - entry to be saved
        overwrite : bool 
         - Optional, defaults to False
         - if true, ignores existing entry

        Returns doc_id : int
        """

        existing_doc = self.get_doc(entry)
        
        if existing_doc and not overwrite:
            return self.update_fields(existing_doc, entry)
        else:
            return self._save(entry)
        
    def update_fields(self, doc : Document, entry : Entry) -> int:
        """
        updates the given doc using fields from entry
        only updates the null or non-existent fields
        
        Returns doc_id : int
        """

        # merge in new data, don't overwrite anything that already exists
        doc = Document(entry.to_dict() | {k:v for k, v in doc.items() if not v is None}, doc.doc_id)

        # getting path of saved documents, if they exist
        metadata = self.get(Query().name == METADATA)
        doc_path = os.path.join(metadata["db_path"], str(doc.doc_id))
        if not os.path.exists(doc_path): # don't want to accidentally overwrite 
            os.mkdir(doc_path)

        if not doc.get("contents") and entry.contents:
            contents_file = os.path.join(doc_path, CONTENTS_FILE)
            with open(contents_file, "w") as f:
                f.write(entry.contents)
            doc["contents"] = contents_file
        
        if not doc.get("notes") and entry.notes:
            notes_file = os.path.join(doc_path, NOTES_FILE)
            with open(notes_file, "w") as f:
                f.write(entry.notes)
            doc["notes"] = notes_file

        # updating the database
        self.update(doc, doc_ids=[doc.doc_id])

        return doc.doc_id

    def _save(self, entry: Entry) -> int:
        """
        Forces an entry to be saved, regardless of the status of any pre-existing entry.
        NOT atomic (though I don't think any tinydb operations are)
        
        entry: Entry
         - entry to be saved
         
        Returns doc_id : int
        """

        doc_id = self.insert(entry.to_dict())

        metadata = self.get(Query().name == METADATA)
        doc_path = os.path.join(metadata["db_path"],str(doc_id))
        os.mkdir(doc_path)

        if entry.contents:
            contents_file = os.path.join(doc_path, CONTENTS_FILE)
            with open(contents_file, "w", encoding="utf-8") as f:
                f.write(entry.contents)
            self.update({"contents": contents_file}, doc_ids=[doc_id])
        
        if entry.notes:
            notes_file = os.path.join(doc_path, NOTES_FILE)
            with open(notes_file, "w", encoding="utf-8") as f:
                f.write(entry.notes)
            self.update({"notes": notes_file}, doc_ids=[doc_id])

        return doc_id
    
    def scrape(self, url: str, title=None, author=None, date=None) -> int:
        """
        Adds an entry to the database based on the URL for scraping.
        Auto-generates a notes template.
        Does not overwrite.

        Returns doc_id: int
        """

        entry = scrape(url)
        if title:
            entry.title = title
        if author:
            entry.author = author
        if date:
            entry.date = date

        entry.generate_notes()

        return self.save(entry)

    
    def remove_cascade(self, entry : Entry | Document | int) -> Document | None:
        """
        Attemps to remove the Document corresponding to the Entry from the database.

        Also deletes the associated files (notes and contents).

        If the document does not exist, nothing is returned.

        entry : Entry | Document | int
         - entry, doc, or doc_id
        
        Returns Optional[Document]
        """

        if type(entry) == Entry:
            doc = self.get_doc(entry)
        elif type(entry) == int:
            doc = self.get(doc_id=entry)
        else:
            doc = entry
        
        if doc:
            file_path = doc.get("contents") or doc.get("notes")
            if file_path:
                directory = os.path.dirname(file_path)
                shutil.rmtree(directory)
            self.remove(doc_ids=[doc.doc_id])
            return doc
        else:
            return None