# download_books.py
import os
import json
import time
import requests

DATA_DIR = "data"
BOOKS_DIR = os.path.join(DATA_DIR, "books")
COVERS_DIR = os.path.join(DATA_DIR, "covers")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.json")

os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

# PROJECT REQUIREMENT
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

    # Fallback: Gutenberg generic
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


def main():
    print("=== Gutenberg Downloader START ===")

    metadata = load_existing_metadata()
    downloaded_filenames = {m["filename"] for m in metadata}
    downloaded_ids = {m["book_id"] for m in metadata}

    print(f"Already have {len(metadata)} books in metadata.json")

    count = len(metadata)
    page = 1

    while count < TARGET_COUNT:
        data = fetch_page(page)
        books = data.get("results", [])

        if not books:
            print("No more pages from Gutendex.")
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
                print(" -> ERROR: No usable text file, skipping.")
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

            # Add to metadata
            entry = {
                "book_id": book_id,
                "title": title,
                "filename": fname,
                "cover": cover,
                "path": fpath,
                "word_count": wc
            }
            metadata.append(entry)
            downloaded_ids.add(book_id)

            # Save metadata after EVERY book → safe resume
            save_metadata(metadata)

            count += 1
            print(f" -> SAVED! total={count} (metadata updated)")

            if count >= TARGET_COUNT:
                break

            time.sleep(1)

        page += 1
        time.sleep(2)

    print("\n=== COMPLETED ===")
    print(f"Downloaded {count} books.")
    print(f"Metadata written to {METADATA_PATH}")


if __name__ == "__main__":
    main()
