# backend/indexing.py

import os
import json
import re
from collections import defaultdict
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from langcodes import Language

DATA_DIR = Path(__file__).parent / "data"
BOOKS_DIR = DATA_DIR / "books"
COVERS_DIR = DATA_DIR / "covers"
METADATA_PATH = DATA_DIR / "metadata.json"
INDEX_PATH = DATA_DIR / "index.json"

WORD_RE = re.compile(r"\w+", re.UNICODE)

# ---------------------------------------------
# Build multilingual stopword list
# ---------------------------------------------
STOPWORDS = set()

def load_language_stopwords(all_languages):
    global STOPWORDS
    STOPWORDS = set()

    available = stopwords.fileids()

    for lang in all_languages:
        lang = Language.get(lang).display_name().lower()
        if lang in available:
            STOPWORDS.update(stopwords.words(lang))

    # also add generic garbage
    STOPWORDS.update({"also", "would", "could", "shall"})


# ---------------------------------------------
# Tokenizer
# ---------------------------------------------
def tokenize(text: str):
    tokens = WORD_RE.findall(text.lower())
    return [w for w in tokens if w not in STOPWORDS]


# ---------------------------------------------
# BUILD INDEX
# ---------------------------------------------
def build_index():
    # Load metadata
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    # build the stopword set
    all_langs = set()
    for m in metadata:
        all_langs.update(m.get("languages", []))
    load_language_stopwords(all_langs)

    inverted_index = defaultdict(lambda: defaultdict(int))
    processed = 0

    for entry in metadata:
        bid = entry["book_id"]
        fname = entry["filename"]
        book_path = BOOKS_DIR / fname

        with book_path.open("r", encoding="utf-8", errors="ignore") as f:
            tokens = tokenize(f.read())

        for w in tokens:
            inverted_index[w][bid] += 1  # KEEP integer book_id

        processed += 1
        print(f"{processed} - Indexed book_id={bid} ({len(tokens)} tokens)")

    # Save index
    index_dict = {w: dict(counts) for w, counts in inverted_index.items()}
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(index_dict, f)

    print(f"\nDone. Indexed {processed} books.")


# ---------------------------------------------
# Loader for backend
# ---------------------------------------------
def load_metadata_and_index():
    # Load metadata
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    meta_by_id = {m["book_id"]: m for m in raw}

    # Load index
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        inverted_index = json.load(f)

    return meta_by_id, inverted_index


if __name__ == "__main__":
    build_index()

