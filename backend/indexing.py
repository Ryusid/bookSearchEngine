# backend/indexing.py

import os
import json
import re
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
BOOKS_DIR = DATA_DIR / "books"
COVERS_DIR = DATA_DIR / "covers"
METADATA_PATH = DATA_DIR / "metadata.json"
INDEX_PATH = DATA_DIR / "index.json"

WORD_RE = re.compile(r"\w+", re.UNICODE)

def tokenize(text: str):
    return [w.lower() for w in WORD_RE.findall(text)]


def build_index():
    # Load metadata
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    inverted_index = defaultdict(lambda: defaultdict(int))
    processed = 0

    for entry in metadata:
        bid = entry["book_id"]
        fname = entry["filename"]
        book_path = BOOKS_DIR / fname

        with book_path.open("r", encoding="utf-8", errors="ignore") as f:
            tokens = tokenize(f.read())

        for w in tokens:
            inverted_index[w][str(bid)] += 1  # JSON needs str keys

        processed += 1
        print(f"Indexed book_id={bid} → {fname}")

    # save index
    index_dict = {w: dict(counts) for w, counts in inverted_index.items()}
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(index_dict, f)

    print(f"Done. Indexed {processed} books.")


def load_metadata_and_index():
    # Load metadata
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    meta_by_id = {m["book_id"]: m for m in raw}

    # Load index
    if not INDEX_PATH.exists():
        raise FileNotFoundError("Missing index.json — run indexing.py")

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        inverted_index = json.load(f)

    return meta_by_id, inverted_index


if __name__ == "__main__":
    build_index()
