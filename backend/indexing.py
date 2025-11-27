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

WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ']+")


def tokenize(text: str):
    return [w.lower() for w in WORD_RE.findall(text)]


def build_index():
    # -----------------------------------------------
    # 1. Load the clean metadata from metadata.json
    # -----------------------------------------------
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"metadata.json not found at {METADATA_PATH}")

    with METADATA_PATH.open("r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    # Mapping filename -> metadata entry
    meta_by_filename = {m["filename"]: m for m in metadata_list}

    # -----------------------------------------------
    # 2. Preparing index + output structure
    # -----------------------------------------------
    inverted_index = defaultdict(lambda: defaultdict(int))
    processed_books = []

    # -----------------------------------------------
    # 3. Indexing all books in data/books/
    # -----------------------------------------------
    for book_file in sorted(BOOKS_DIR.glob("*.txt")):
        fname = book_file.name

        if fname not in meta_by_filename:
            print(f"[WARN] No metadata for file: {fname}, skipping.")
            continue

        meta = meta_by_filename[fname]

        with book_file.open("r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        tokens = tokenize(content)

        # Updating inverted index
        for w in tokens:
            inverted_index[w][fname] += 1

        processed_books.append(fname)
        print(f"Indexed: {fname} ({len(tokens)} words)")

    # -----------------------------------------------
    # 4. Saving inverted index to index.json
    # -----------------------------------------------
    print("Saving index...")
    index_dict = {word: dict(counts) for word, counts in inverted_index.items()}
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(index_dict, f)

    print("Index saved to", INDEX_PATH)
    print("Processed books:", len(processed_books))


def load_metadata_and_index():
    # 1. Loading metadata.json
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        raw_meta = json.load(f)

    meta_by_filename = {}

    for entry in raw_meta:
        filename = entry["filename"]
        title = entry["title"]
        cover = entry.get("cover")

        book_path = BOOKS_DIR / filename
        cover_path = (COVERS_DIR / cover) if cover else None

        meta_by_filename[filename] = {
            "title": title,
            "path": str(book_path),
            "cover_path": f"/covers/{cover}" if cover else None
        }

    # 2. Loading index.json
    if not INDEX_PATH.exists():
        raise FileNotFoundError("index.json not found! Run: python indexing.py")

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        inverted_index = json.load(f)

    return meta_by_filename, inverted_index


if __name__ == "__main__":
    build_index()
