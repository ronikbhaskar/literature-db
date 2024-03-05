# Literature DB (WIP)

Simple database for easily scraping and storing small/medium text files, mostly literature.

## Overview

Literature DB (LitDB) is a lightweight literature database that allows users to store and manage texts. Entries can be added manually or by scraping websites. Each entry maintains simple, bibliographic data. Separate text files are used for storing the contents of the text and an associated Markdown file for notes. Texts can be rendered as HTML for easy reading, and texts can be quickly searched using a multithreaded search for both substrings and regex.

## Installation

Clone the project and install the requirements.

```Bash
git clone 
cd literature-db
# create an environment if you so choose
pip install -r requirements.txt
```

## Usage

Currently, there is no user interface, but the functions have been simplified enough for Python itself to be the interface. Begin by running the main script with the REPL flag.

```Bash
python3 -i main.py
```

The database can be accessed as the variable `litdb`. 

### Adding Entries

To add an entry from a URL, use:

```Python
>>> litdb.scrape(url)
```

This will autopopulate as many fields as possible. It also generates a notes template.

### Searching for Entries

To search for entries, use:

```Python
>>> search(term)
```

where `term` is either a substring or a regex. `re` is already imported, so you can run `search(re.compile(...))` with no additional code.

### Removing Entries

To remove an entry, use:

```Python
>>> litdb.remove_cascade(doc_id)
```

where `doc_id` is the numeric id of the entry. This is also the name of the directory in which the text is stored. Use `remove_cascade` instead of `remove` to get rid of the associated text files.

### Rendering Entries

To render an entry as HTML, use either of the following:

```Python
>>> render_doc_id(doc_id)
>>> render(entry) # entry must be of the Entry class, not Document
```

The function will print the location of the saved `index.html`, though it can also be found in the `litdb` directory.