# backend/similarity.py

import json
from indexing import DATA_DIR, BOOKS_DIR, METADATA_PATH, tokenize
from tqdm import tqdm

SIM_PATH = DATA_DIR / "similarity.json"


def load_metadata():
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_book_wordsets():
    meta = load_metadata()
    wordsets = {}

    for entry in meta:
        bid = entry["book_id"]
        fname = entry["filename"]

        with (BOOKS_DIR / fname).open("r", encoding="utf-8", errors="ignore") as f:
            wordsets[bid] = set(tokenize(f.read()))

    return wordsets


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def build_similarity_graph(threshold=0.12):
    print("Loading wordsets...")
    ws = load_book_wordsets()
    ids = list(ws.keys())

    graph = {bid: {} for bid in ids}

    print("Computing similarities...")
    for i in tqdm(range(len(ids))):
        A = ids[i]
        for j in range(i + 1, len(ids)):
            B = ids[j]

            sim = jaccard(ws[A], ws[B])
            if sim >= threshold:
                graph[A][B] = sim
                graph[B][A] = sim

    print("Saving:", SIM_PATH)
    with SIM_PATH.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    return graph


def load_similarity_graph():
    with SIM_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): {int(n): w for n, w in v.items()} for k, v in raw.items()}


if __name__ == "__main__":
    build_similarity_graph()
