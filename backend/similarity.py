# backend/similarity.py
import json
from pathlib import Path
from indexing import BOOKS_DIR, METADATA_PATH, tokenize
from tqdm import tqdm

SIMILARITY_PATH = Path(__file__).parent / "data" / "similarity.json"

# --------------------------------------
# Load metadata
# --------------------------------------
def load_metadata():
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------------------
# Read & tokenize each book into a set
# --------------------------------------
def load_book_wordsets():
    meta = load_metadata()

    book_wordsets = {}
    for entry in meta:
        fname = entry["filename"]
        book_path = BOOKS_DIR / fname

        with book_path.open("r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        words = set(tokenize(text))
        book_wordsets[fname] = words

    return book_wordsets

# --------------------------------------
# Compute Jaccard similarity
# --------------------------------------
def jaccard(setA, setB):
    if not setA or not setB:
        return 0.0

    inter = len(setA & setB)
    union = len(setA | setB)
    return inter / union

# --------------------------------------
# Build full similarity graph
# --------------------------------------
def build_similarity_graph(threshold=0.15):
    print("Loading books...")
    book_wordsets = load_book_wordsets()
    books = list(book_wordsets.keys())

    graph = {b: {} for b in books}

    print("Computing pairwise Jaccard similarity...")
    for i in tqdm(range(len(books))):
        A = books[i]
        for j in range(i+1, len(books)):
            B = books[j]

            sim = jaccard(book_wordsets[A], book_wordsets[B])

            if sim >= threshold:
                graph[A][B] = sim
                graph[B][A] = sim

    print(f"Saving similarity graph → {SIMILARITY_PATH}")
    with SIMILARITY_PATH.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print("DONE.")
    return graph

# --------------------------------------
# Loader used by backend endpoints
# --------------------------------------
def load_similarity_graph():
    if not SIMILARITY_PATH.exists():
        raise FileNotFoundError("similarity.json not found, run similarity builder")
    with SIMILARITY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

# Run manually
if __name__ == "__main__":
    build_similarity_graph()
