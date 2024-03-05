"""
something something docs

Ronik Bhaskar
"""

from db_entry import Entry
from enum import Enum
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "templates")

class Template(Enum):
    """
    enumeration of all sources that are able to be scraped
    """
    DEFAULT = 1

TEMPLATES = {
    Template.DEFAULT: "default.html"
}

def render_default(entry: Entry) -> str:
    """
    default rendering of the text
    """

    with open(os.path.join(TEMPLATE_DIR, TEMPLATES[Template.DEFAULT]), "r") as f:
        template = f.read()

    body = ""

    for line in entry.contents.split("\n"):
        if not line.strip():
            body += "<br>"
        else:
            body += f"<p>{line}</p>"

    return template.format(**(entry.to_dict() | {"body": body}))

RENDER_FUNCTIONS = {
    Template.DEFAULT: render_default
}

def render(entry: Entry, template: Template=None) -> str:
    """
    At the moment, there is only one renderer, the default renderer. 
    Generates an HTML string that can be used to view the text.
    
    Returns str
    """

    if template is None:
        template = Template.DEFAULT

    return RENDER_FUNCTIONS[template](entry)