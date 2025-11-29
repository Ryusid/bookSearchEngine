# backend/main.py

import json
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from indexing import load_metadata_and_index, DATA_DIR, BOOKS_DIR, COVERS_DIR
from similarity import load_similarity_graph

# ----------------------------------------------------
# FastAPI setup
# ----------------------------------------------------
app = FastAPI(title="Book Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")

# ----------------------------------------------------
# Load index + metadata + pagerank + similarity graph
# ----------------------------------------------------
meta_by_id, inverted_index = load_metadata_and_index()  # book_id_str -> meta

with (DATA_DIR / "pagerank.json").open("r", encoding="utf-8") as f:
    pagerank_scores = json.load(f)                      # book_id_str -> PR

similarity_graph = load_similarity_graph()              # book_id_str -> {other_id: similarity score}


# ----------------------------------------------------
# Helpers
# ----------------------------------------------------
def make_cover_url(meta: dict):
    cover = meta.get("cover")
    if not cover:
        return None
    return f"/covers/{cover}"


def empty_result(q, page, page_size):
    return {
        "query": q,
        "page": page,
        "page_size": page_size,
        "total": 0,
        "results": [],
    }


def format_snippet(meta: dict, length: int = 300) -> str:
    book_path = BOOKS_DIR / meta["filename"]
    with book_path.open("r", encoding="utf-8", errors="ignore") as f:
        text = f.read(length)
    return text.replace("\n", " ") + "..."


# ----------------------------------------------------
# Unified Keyword Search (with optional regex)
# Ranking mode: TF / PR / TF×PR
# ----------------------------------------------------
@app.get("/search-keyword")
def search_keyword(
    q: str,
    advanced: bool = False,
    rank_mode: str = "tf",
    page: int = 1,
    page_size: int = 20,
):
    query = q.strip().lower()
    if not query:
        return empty_result(q, page, page_size)

    # -----------------------------------
    # Regex on terms (advanced = True)
    # -----------------------------------
    if advanced:
        try:
            pattern = re.compile(query, re.IGNORECASE)
        except re.error:
            raise HTTPException(400, "Invalid regex pattern")

        matched_terms = [t for t in inverted_index.keys() if pattern.search(t)]
        if not matched_terms:
            return empty_result(q, page, page_size)

        scores = {}  # book_id_str -> {"tf": ..., "pr": ..., "terms": set(...)}

        for term in matched_terms:
            for book_id_str, tf in inverted_index[term].items():
                pr = float(pagerank_scores.get(book_id_str, 0.0))
                info = scores.setdefault(
                    book_id_str, {"tf": 0, "pr": pr, "terms": set()}
                )
                info["tf"] += tf
                info["terms"].add(term)

    # -----------------------------------
    # Simple keyword
    # -----------------------------------
    else:
        if query not in inverted_index:
            return empty_result(q, page, page_size)

        scores = {}
        for book_id_str, tf in inverted_index[query].items():
            pr = float(pagerank_scores.get(book_id_str, 0.0))
            scores[book_id_str] = {"tf": tf, "pr": pr, "terms": {query}}

    # -----------------------------------
    # Apply ranking mode
    # -----------------------------------
    def rank_value(info):
        if rank_mode == "pr":
            return info["pr"]
        elif rank_mode == "tfpr":
            return info["tf"] * info["pr"]
        else:  # "tf"
            return info["tf"]

    ranked = sorted(scores.items(), key=lambda kv: rank_value(kv[1]), reverse=True)

    total = len(ranked)
    start = (page - 1) * page_size
    sliced = ranked[start:start + page_size]

    results = []
    for book_id_str, info in sliced:
        meta = meta_by_id[int(book_id_str)]
        snippet = format_snippet(meta)

        if rank_mode == "pr":
            display_score = info["pr"]
        elif rank_mode == "tf":
            display_score = info["tf"]
        else:
            display_score = info["tf"] * info["pr"]

        results.append({
            "book_id": meta["book_id"],           # int for frontend
            "title": meta["title"],
            "snippet": snippet,
            "cover_url": make_cover_url(meta),
            "tf": info["tf"],
            "pagerank": info["pr"],
            "matched_terms": sorted(info["terms"]),
            "score": display_score,
        })

    return {
        "query": q,
        "page": page,
        "page_size": page_size,
        "rank_mode": rank_mode,
        "advanced": advanced,
        "total": total,
        "results": results,
    }


# ----------------------------------------------------
# Title Search (uses PageRank for ranking)
# ----------------------------------------------------
@app.get("/search-title")
def search_title(q: str, page: int = 1, page_size: int = 20):
    term = q.strip().lower()
    if not term:
        return empty_result(q, page, page_size)

    matches = []
    for book_id, meta in meta_by_id.items():
        if term in meta["title"].lower():
            pr = float(pagerank_scores.get(str(book_id), 0.0))
            matches.append((book_id, pr))

    matches.sort(key=lambda x: x[1], reverse=True)

    total = len(matches)
    start = (page - 1) * page_size
    sliced = matches[start:start + page_size]
    results = []
    for book_id, pr in sliced:
        meta = meta_by_id[book_id]
        snippet = format_snippet(meta)
        results.append({
            "book_id": meta["book_id"],
            "title": meta["title"],
            "snippet": snippet,
            "cover_url": make_cover_url(meta),
            "pagerank": pr,
        })
    return {
        "query": q,
        "page": page,
        "page_size": page_size,
        "total": total,
        "results": results,
    }


# ----------------------------------------------------
# Book info  /book/{book_id}
# ----------------------------------------------------
@app.get("/book/{book_id}")
def get_book(book_id: int):
    key = str(book_id)
    meta = meta_by_id.get(book_id)
    if not meta:
        raise HTTPException(404, "Book not found")

    book_path = BOOKS_DIR / meta["filename"]
    with book_path.open("r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    snippet = text[:800].replace("\n", " ") + "..."

    return {
        "book_id": meta["book_id"],
        "title": meta["title"],
        "cover_url": make_cover_url(meta),
        "content": text,
        "snippet": snippet,
    }


# ----------------------------------------------------
# Paginated reading  /book-page/{book_id}
# ----------------------------------------------------
@app.get("/book-page/{book_id}")
def get_book_page(book_id: int, page: int = 1, size: int = 5000):
    key = str(book_id)
    meta = meta_by_id.get(book_id)
    if not meta:
        raise HTTPException(404, "Book not found")

    book_path = BOOKS_DIR / meta["filename"]
    if not book_path.exists():
        raise HTTPException(404, "Book file not found")

    with book_path.open("r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    total_pages = (len(text) + size - 1) // size
    page = max(1, min(page, total_pages))

    start = (page - 1) * size
    end = start + size
    chunk = text[start:end]

    return {
        "book_id": meta["book_id"],
        "title": meta["title"],
        "cover_url": make_cover_url(meta),
        "page": page,
        "total_pages": total_pages,
        "text": chunk,
    }


# ----------------------------------------------------
# Jaccard-based recommendations  /recommend/{book_id}
# ----------------------------------------------------
@app.get("/recommend/{book_id}")
def recommend(book_id: int, limit: int = 5):
    key = str(book_id)
    if key not in similarity_graph:
        raise HTTPException(404, "Book not found in similarity graph")

    neighbors = similarity_graph[key]  # { other_id_str: sim }

    ranked = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:limit]

    results = []
    for other_id_str, sim in ranked:
        meta = meta_by_id[int(other_id_str)]
        results.append({
            "book_id": meta["book_id"],
            "title": meta["title"],
            "cover_url": make_cover_url(meta),
            "score": sim,
        })

    return {"book_id": book_id, "recommendations": results}
