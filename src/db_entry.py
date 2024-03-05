"""
something something docs

Ronik Bhaskar
"""

from tinydb.table import Document

NOTES_TEMPLATE = """# {0}

by {1}, {2}

## Background

---

## References

text source: {3}

1. """

class Entry:
    """
    doc_id : int
     - entry ID, should be unique 
    title : str
     - title of work
    author : str
     - author of work
    date : str
     - date of publication, typically just the year
    source : str
     - url source of text if digital, info string otherwise
    contents : str
     - contents of the text
    notes : str
     - personal notes on the text
    """

    def __init__(
        self,
        doc_id=None,
        title=None,
        author=None, 
        date=None, 
        source=None, 
        contents=None,
        notes=None
    ):
        self.doc_id = doc_id
        self.title = title
        self.author = author
        self.date = date
        self.source = source
        self.contents = contents
        self.notes = notes

    def generate_notes(self) -> None:
        """
        auto-populates some starter notes for the text
        uses fields in the instance
        
        Returns None
        """

        self.notes = NOTES_TEMPLATE.format(self.title, self.author, self.date, self.source)

    @staticmethod
    def from_doc(doc : Document):
        """
        creates an Entry from the given Document
        """

        if doc.get("contents"):
            with open(doc["contents"], "r") as f:
                contents = f.read()
        else:
            contents = None

        if doc.get("notes"):
            with open(doc["notes"], "r") as f:
                notes = f.read()
        else:
            notes = None

        return Entry(
            title=doc.get("title"),
            author=doc.get("author"),
            date=doc.get("date"),
            source=doc.get("source"),
            doc_id=doc.doc_id,
            contents=contents,
            notes=notes
        )
    
    def to_dict(self) -> dict:
        """
        generates a dictionary version of the fields for easy parsing
        omits the content and notes and doc_id
        """

        return {
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "source": self.source
        }