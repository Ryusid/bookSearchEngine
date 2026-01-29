#!/usr/bin/env sh
set -eu

DATA_DIR="${DATA_DIR:-data}"
FORCE_REBUILD="${FORCE_REBUILD:-false}"

BOOKS_DIR="${DATA_DIR}/books"
COVERS_DIR="${DATA_DIR}/covers"

META="${DATA_DIR}/metadata.json"
INDEX="${DATA_DIR}/index.json"
SIM="${DATA_DIR}/similarity.json"
PR="${DATA_DIR}/pagerank.json"
VERSION_FILE="${DATA_DIR}/.data_version"
DATA_VERSION="${DATA_VERSION:-v1}"

mkdir -p "$DATA_DIR"

should_rebuild=false

# Force rebuild
if [ "$FORCE_REBUILD" = "true" ]; then
  should_rebuild=true
fi

# Version-based rebuild (optional but nice)
if [ -f "$VERSION_FILE" ]; then
  old="$(cat "$VERSION_FILE" || true)"
  if [ "$old" != "$DATA_VERSION" ]; then
    should_rebuild=true
  fi
else
  # No version file yet => first run
  should_rebuild=false
fi

if [ "$should_rebuild" = "true" ]; then
  echo "Rebuilding dataset (FORCE_REBUILD=$FORCE_REBUILD, DATA_VERSION=$DATA_VERSION)..."
  rm -f "$META" "$INDEX" "$SIM" "$PR"
  rm -rf "$BOOKS_DIR" "$COVERS_DIR"
fi

# Step 1: download only if missing
if [ ! -f "$META" ] || [ ! -d "$BOOKS_DIR" ] || [ -z "$(ls -A "$BOOKS_DIR" 2>/dev/null || true)" ]; then
  echo "Downloading books/covers/metadata..."
  python download_books.py
else
  echo "Books/metadata already present, skipping download."
fi

# Step 2: build artifacts only if missing
if [ ! -f "$INDEX" ]; then
  echo "Building index..."
  python indexing.py
else
  echo "index.json exists, skipping."
fi

if [ ! -f "$SIM" ]; then
  echo "Building similarity graph..."
  python similarity.py
else
  echo "similarity.json exists, skipping."
fi

if [ ! -f "$PR" ]; then
  echo "Computing pagerank..."
  python pagerank.py
else
  echo "pagerank.json exists, skipping."
fi

echo "$DATA_VERSION" > "$VERSION_FILE"
echo "Done."
