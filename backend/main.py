import json
import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import re
from pathlib import Path
from typing import List
from similarity import load_similarity_graph

from indexing import load_metadata_and_index, DATA_DIR, BOOKS_DIR, COVERS_DIR
from models import BookSummary, BookDetail, SearchResponse

app = FastAPI(title="Book Search API")

# CORS so React web + mobile can talk to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static serving of covers
# This mounts /covers/ to serve files from data/covers
app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")

# Load index on startup
meta_by_filename, inverted_index = load_metadata_and_index()


def make_cover_url(book_meta):
    """
    Convert local path to URL that frontend can use.
    We serve covers from /covers, so just point there if we know the filename.
    """
    cover_path = book_meta.get("cover_path")
    if not cover_path:
        return None
    filename = Path(cover_path).name
    return f"/covers/{filename}"


def compute_tfidf(term: str, book_id: str):
    """

    Computes TF-IDF score for better results when searching a term in a book

    """
    tf = inverted_index[term].get(book_id, 0)

    if tf == 0:
        return 0.0

    df = len(inverted_index[term]) # Number of books containing the word/term
    N = len(meta_by_filename) # Number of books (1664)

    idf = math.log((N + 1)/(df + 1)) + 1 # similar to elsaticsearch simplified
    return tf * idf

@app.get("/search")
def search(q: str, page: int =1, page_size: int = 20):

    query = q.strip().lower()
    if not query:
        return {
            "query": q,
            "page": page,
            "page_size": page_size,
            "total": 0,
            "results": []
        }

    if query not in inverted_index:
        return {
            "query": q,
            "page": page,
            "page_size": page_size,
            "total": 0,
            "results": []
        }

    # --- Ranking entire result set using TF-IDF ---
    sorted_books = sorted(
        ((book_id, compute_tfidf(query, book_id)) for book_id in inverted_index[query].keys()),
        key=lambda x: x[1],
        reverse=True
    )


    total = len(sorted_books)

    # --- Pagination ---
    start = (page - 1) * page_size
    end = start + page_size
    sliced = sorted_books[start:end]

    results = []
    for book_id, count in sliced:
        meta = meta_by_filename[book_id]

        # snippet
        with open(meta["path"], "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)
        snippet = content[:200].replace("\n", " ") + "..."

        results.append({
            "book_id": book_id,
            "title": meta["title"],
            "snippet": snippet,
            "cover_url": make_cover_url(meta),
            "score": float(count),
        })

    return {
        "query": q,
        "page": page,
        "page_size": page_size,
        "total": total,
        "results": results
    }


@app.get("/advanced-search")
def advanced_search(regex: str, page: int = 1, page_size: int = 20):
    try:
        pattern = re.compile(regex, re.IGNORECASE)
    except re.error as e:
        raise HTTPException(400, f"Invalid regex: {e}")

    matches = []


    for term in inverted_index.keys():
        if pattern.search(term):
            matches.append(term)
    if not matches:
        return { 
            "query": regex,
            "page": page,
            "page_size": page_size,
            "total": 0,
            "results": []
        }
    candidate_books = {}
    for term in matches:
        for book_id in inverted_index[term].keys():
            candidate_books.setdefault(book_id, 0.0)
            candidate_books[book_id] += compute_tfidf(term, book_id)

    sorted_books = sorted(candidate_books.items(), key=lambda x: x[1], reverse=True)

    total = len(sorted_books)

    # --- Pagination ---
    start = (page - 1) * page_size
    end = start + page_size

    sliced = sorted_books[start:end]

    results = []
    for book_id, score in sliced:
        meta = meta_by_filename[book_id]

        with open(meta["path"], "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)

        snippet = content[:200].replace("\n", " ") + "..."

        results.append({
            "book_id": book_id,
            "title": meta["title"],
            "snippet": snippet,
            "cover_url": make_cover_url(meta),
            "score": float(score),
        })

    return {
        "query": regex,
        "page": page,
        "page_size": page_size,
        "total": total,
        "results": results
    }


@app.get("/book/{filename}")
def get_book(filename: str):
    meta = meta_by_filename.get(filename)
    if not meta:
        raise HTTPException(status_code=404, detail="Book not found")

    # Load book text
    try:
        with open(meta["path"], "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except:
        raise HTTPException(status_code=500, detail="Failed to read book file")

    snippet = text[:800].replace("\n"," ") + "..."
    # Return full data
    return {
        "title": meta["title"],
        "cover_url": meta["cover_path"],
        "content": text,
        "snippet": snippet
    }


@app.get("/book-page/{filename}")
def get_book_page(filename: str, page: int = 1, size: int = 5000):
    """Paginate a book by characters, preserving original formatting."""
    file_path = BOOKS_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "Book not found")

    # Load full text
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    total_length = len(text)
    total_pages = (total_length + size - 1) // size

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start = (page - 1) * size
    end = min(page * size, total_length)

    chunk = text[start:end]

    meta = meta_by_filename.get(filename, {})
    cover_url = None
    if meta.get("cover_path"):
        cover_url = f"/covers/{Path(meta['cover_path']).name}"

    return {
        "title": meta.get("title", filename),
        "cover_url": cover_url,
        "page": page,
        "total_pages": total_pages,
        "text": chunk
    }

similarity_graph = load_similarity_graph()
@app.get("/recommend/{filename}")
def recommend(filename: str, limit: int = 5):
    if filename not in meta_by_filename:
        raise HTTPException(status_code=404, detail="Book not found")

    # Get neighbors
    neighbors = similarity_graph.get(filename, {})

    # Sort by similarity descending
    sorted_neighbors = sorted(
        neighbors.items(), key=lambda kv: kv[1], reverse=True
    )[:limit]

    results = []
    for other_filename, score in sorted_neighbors:
        meta = meta_by_filename[other_filename]

        results.append({
            "filename": other_filename,
            "title": meta["title"],
            "cover_url": meta["cover_path"],
            "score": score
        })

    return {"book": filename, "recommendations": results}

with open("data/pagerank.json", "r") as f:
    pagerank_scores = json.load(f)

@app.get("/recommend-pagerank/{filename}")
def recommend_pagerank(filename: str, limit: int = 5):

    if filename not in pagerank_scores:
        raise HTTPException(404, "Book not found")

    ranked = sorted(
        [(b, s) for b, s in pagerank_scores.items() if b != filename],
        key=lambda x: x[1],
        reverse=True
    )[:limit]

    results = []
    for fname, score in ranked:
        meta = meta_by_filename[fname]
        results.append({
            "filename": fname,
            "title": meta["title"],
            "cover_url": meta["cover_path"],
            "score": score
        })

    return {"book": filename, "recommendations": results}


# --- TODO: Jaccard graph + recommendation ---
# You can build a graph based on word sets per book, store it, and load it similarly.
# Then expose /recommend/{book_id} endpoint based on that graph.
