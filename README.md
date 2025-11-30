===============================================================
                      PROJECT README
    (Backend + Web Frontend + Mobile App - Full Instructions)
===============================================================

This document explains exactly how to install, prepare, and run:
- Python FastAPI backend (search engine + ranking + similarity + covers)
- Web frontend (React + Vite)
- Mobile app (React Native + Expo)
- Preprocessing steps (indexing, similarity graph, PageRank)

Everything is consolidated in one place.

===============================================================
1. PROJECT STRUCTURE
===============================================================

projet3/
│
├── backend/
│   ├── main.py
│   ├── indexing.py
│   ├── similarity.py
│   ├── pagerank.py
│   ├── requirements.txt
│   └── data/
│       ├── books/          (100 .txt books)
│       ├── covers/         (cover_XXXX.jpg)
│       ├── metadata.json
│       ├── index.json
│       ├── similarity.json
│       └── pagerank.json
│
├── web/
│   ├── src/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   └── pages/
│   │       ├── SearchPage.tsx
│   │       ├── BookPage.tsx
│   │       └── ReadPage.tsx
│   ├── package.json
│   └── vite.config.js
│
└── mobile/
    ├── App.tsx
    ├── src/
    │   ├── config.ts
    │   ├── api.ts
    │   └── screens/
    │       ├── SearchScreen.tsx
    │       ├── BookScreen.tsx
    │       └── MobileReadScreen.tsx
    └── package.json


===============================================================
2. PREREQUISITES
===============================================================

Backend:
    Python 3.10+ (you use 3.11)
    pip
    nltk stopwords downloaded automatically if required

Web frontend:
    Node.js 18+
    npm

Mobile app:
    Node.js 18+
    npm
    Expo CLI (auto-installed)
    A physical phone (Android/iOS) or emulator
    → For phone usage, run mobile with:
        npx expo start --tunnel

Shared:
    On SAME network when using phone (web/mobile must reach backend IP)


===============================================================
3. BACKEND — INSTALLATION & RUNNING
===============================================================

1. Enter backend folder:
       cd backend

2. Create virtual environment:
       python3 -m venv venv
       source venv/bin/activate
   (on Windows: venv\Scripts\activate)

3. Install dependencies:
       pip install -r requirements.txt

4. Make sure NLTK stopwords are installed:
       python3
       >>> import nltk
       >>> nltk.download("stopwords")
       >>> exit()

5. Run preprocessing (ONLY RUN ONCE):
       python indexing.py
       python similarity.py
       python pagerank.py

   These generate:
     data/index.json
     data/similarity.json
     data/pagerank.json

6. RUN BACKEND SERVER:
       uvicorn main:app --reload --host 0.0.0.0 --port 8000

7. Test:
       http://127.0.0.1:8000/search-keyword?q=love
       http://127.0.0.1:8000/book/1342


===============================================================
4. WEB FRONTEND — INSTALL & RUN
===============================================================

1. Enter folder:
       cd web

2. Install dependencies:
       npm install

3. Update backend URL in:
       src/api.ts
   Example:
       export const API_BASE = "http://192.168.0.31:8000";

4. Run dev server:
       npm run dev

5. Open browser:
       http://localhost:5173/


===============================================================
5. MOBILE APP — INSTALL & RUN (EXPO)
===============================================================

1. Enter folder:
       cd mobile

2. Install:
       npm install

3. Set backend IP in:
       src/config.ts
   Example:
       export const API_BASE = "http://192.168.0.31:8000";

4. Start Expo with phone support:
       npx expo start --tunnel

5. Scan QR code with:
       - Expo Go (Android)
       - Expo Go (iOS)

The app loads:
   Search → Book → Read (paginated, dark mode, font size, etc.)


===============================================================
6. SUMMARY OF API ENDPOINTS
===============================================================

GET /search-keyword?q=...&advanced=bool&rank_mode=tf|pr|tfpr&page=1&page_size=20
GET /search-title?q=...&page=1&page_size=20
GET /book/{book_id}
GET /book-page/{book_id}?page=N&size=S
GET /recommend/{book_id}

Returned fields include:
  book_id, title, cover_url, snippet, tf, pagerank, matched_terms, score, content, summary, authors


===============================================================
7. WHAT TO RUN FIRST (ABSOLUTE MINIMUM)
===============================================================

Backend:
    python indexing.py
    python similarity.py
    python pagerank.py
    uvicorn main:app --reload

Web:
    npm install
    npm run dev

Mobile:
    npm install
    npx expo start --tunnel

===============================================================
8. NOTES & TROUBLESHOOTING
===============================================================

• If covers don’t load → check CORS/IP mismatch.
• If phone cannot reach backend:
      - backend must run with host 0.0.0.0
      - use LAN IP (192.168.x.x:8000)
• If expo shows network errors → always use:
      npx expo start --tunnel
• If search returns 0 results:
      - index.json not regenerated
      - metadata.json mismatch
• If book content displays only title:
      - /book/{id} must return "content"


===============================================================
END OF README
===============================================================
