# download_books.py
import os
import json
import time
import requests

DATA_DIR = os.environ.get("DATA_DIR", "data")
BOOKS_DIR = os.path.join(DATA_DIR, "books")
COVERS_DIR = os.path.join(DATA_DIR, "covers")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.json")

os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

TARGET_COUNT = 1664
MIN_WORDS = 10000
API = "https://gutendex.com/books"


def safe_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in " _-")[:60]


def fetch_page(page=1):
    retries = 3
    while retries:
        try:
            r = requests.get(API, params={"page": page, "page_size": 100}, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f" !! Network error on page {page}: {e}")
            retries -= 1
            time.sleep(2)
    return {"results": []}


def download_text(book_id, formats):
    # Try recommended plain text URLs
    for fmt, url in formats.items():
        if "text/plain" in fmt:
            try:
                r = requests.get(url, timeout=30)
                if r.status_code == 200:
                    return r.text
            except:
                pass

    # Fallback URLs
    fallback_urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    ]

    for url in fallback_urls:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                return r.text
        except:
            pass

    return None


def download_cover(book_id, formats):
    url = formats.get("image/jpeg")
    if not url:
        return None

    fname = f"cover_{book_id}.jpg"
    fpath = os.path.join(COVERS_DIR, fname)

    if os.path.exists(fpath):
        return fname

    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(fpath, "wb") as f:
                f.write(r.content)
            return fname
    except:
        pass

    return None


def load_existing_metadata():
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_metadata(metadata):
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


# ----------------------------------------
# Fetch metadata for an existing book
# ----------------------------------------
# -------------------------------
# GLOBAL cache to avoid re-fetching
# -------------------------------
GUTENDEX_CACHE = {}
GUTENDEX_URL = "https://gutendex.com/books/{}"

def fetch_gutendex(id):
    """Safe request with retries, sleeps, caching."""
    if id in GUTENDEX_CACHE:
        return GUTENDEX_CACHE[id]

    retries = 6
    wait = 2

    while retries:
        try:
            r = requests.get(GUTENDEX_URL.format(id), timeout=15)

            # RATE LIMIT signal
            if r.status_code == 429:
                print(f"429 Too Many Requests — sleeping {wait} sec...")
                time.sleep(wait)
                retries -= 1
                wait = min(wait * 2, 30)  # exponential backoff
                continue

            r.raise_for_status()
            data = r.json()

            # Cache result
            GUTENDEX_CACHE[id] = data

            # Smooth throttle
            time.sleep(1.5)

            return data

        except Exception as e:
            print(f"Error fetching ID {id}: {e}")
            time.sleep(wait)
            retries -= 1
            wait = min(wait * 2, 30)

    print(f"FAILED after retries: book {id}")
    return None


# -------------------------------
# Decide if a book needs enrichment
# -------------------------------
def needs_enrichment(entry):
    required = ["languages", "authors", "summary"]
    for k in required:
        if k not in entry:
            return True
        if entry[k] is None:
            return True
        if isinstance(entry[k], list) and len(entry[k]) == 0:
            return True
    return False


# -------------------------------
# Enrich a metadata entry
# -------------------------------
def enrich_metadata(entry):
    gid = entry["book_id"]

    if not needs_enrichment(entry):
        print(f"Book {gid} already enriched")
        return entry

    print(f"Enriching {gid} ({entry['title'][:40]}...)")

    data = fetch_gutendex(gid)
    if not data:
        print(f"Skipping {gid} (no data)")
        return entry

    entry["languages"] = data.get("languages", [])
    entry["authors"] = [a["name"] for a in data.get("authors", [])]

    summaries = data.get("summaries", []) or data.get("summary")
    if isinstance(summaries, list) and summaries:
        entry["summary"] = summaries[0]
    elif isinstance(summaries, str):
        entry["summary"] = summaries
    else:
        entry["summary"] = None

    print(f"✓ Enriched {gid}")
    return entry


def main():
    print("=== Gutenberg Downloader (with metadata enrichment) ===")

    metadata = load_existing_metadata()
    downloaded_ids = {m["book_id"] for m in metadata}
    downloaded_files = {m["filename"] for m in metadata}

    print(f"Loaded {len(metadata)} existing entries")

    # --------------------------------------------------------
    # STEP 1 — Enrich metadata for already-downloaded books
    # --------------------------------------------------------
    print("\n=== Enriching existing metadata ===")
    new_metadata = []

    for entry in metadata:
        enriched = enrich_metadata(entry)
        new_metadata.append(enriched)
    save_metadata(new_metadata)
    metadata = new_metadata
    print("Existing metadata enriched.\n")

    # --------------------------------------------------------
    # STEP 2 — Continue normal download process
    # --------------------------------------------------------
    count = len(metadata)
    page = 1

    while count < TARGET_COUNT:
        data = fetch_page(page)
        books = data.get("results", [])

        if not books:
            print("No more pages available.")
            break

        for b in books:
            book_id = b["id"]
            title = b["title"]
            formats = b["formats"]

            if book_id in downloaded_ids:
                print(f"[SKIP] Book {book_id} already downloaded.")
                continue

            print(f"\n------ Trying book {book_id}: {title}")

            text = download_text(book_id, formats)
            if not text:
                print(" -> ERROR: No usable text file.")
                continue

            wc = len(text.split())
            if wc < MIN_WORDS:
                print(f" -> TOO SHORT ({wc} words), skipping.")
                continue

            cover = download_cover(book_id, formats)

            fname = f"book_{count+1:04d}_{book_id}_{safe_filename(title)}.txt"
            fpath = os.path.join(BOOKS_DIR, fname)

            with open(fpath, "w", encoding="utf-8") as f:
                f.write(text)

            entry = {
                "book_id": book_id,
                "title": title,
                "filename": fname,
                "cover": cover,
                "path": fpath,
                "word_count": wc,
            }

            # NEW: metadata enrichment for fresh books
            entry = enrich_metadata(entry)

            metadata.append(entry)
            downloaded_ids.add(book_id)

            save_metadata(metadata)

            count += 1
            print(f" -> SAVED! total={count}")

            if count >= TARGET_COUNT:
                break

            time.sleep(1)

        page += 1
        time.sleep(2)

    print("\n=== DONE ===")
    print(f"Total metadata entries: {count}")


if __name__ == "__main__":
    main()
