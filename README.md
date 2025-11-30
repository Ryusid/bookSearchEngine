# 📚 Book Search Engine — Full Project Documentation

This project includes:
- A **FastAPI backend** (full‑text search, PageRank, regex search, Jaccard similarity).
- A **React web frontend** with book pages + reader mode.
- An **Expo React‑Native mobile app** with the same functionalities.

Below is everything you need to run, rebuild, and understand the project.

---

# 1. Project Structure

```
projet3/
│
├── backend/
│   ├── main.py
│   ├── indexing.py
│   ├── similarity.py
│   ├── pagerank.py
│   ├── requirements.txt
│   └── data/
│       ├── books/
│       ├── covers/
│       ├── metadata.json
│       ├── index.json
│       ├── similarity.json
│       └── pagerank.json
│
├── web/
│   ├── package.json
│   ├── src/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── main.jsx
│   │   └── pages/
│   │       ├── SearchPage.tsx
│   │       ├── BookPage.tsx
│   │       └── ReadPage.tsx
│
└── mobile/
    ├── App.tsx
    ├── src/
    │   ├── api.ts
    │   ├── config.ts
    │   └── screens/
    │       ├── SearchScreen.tsx
    │       ├── BookScreen.tsx
    │       └── MobileReadScreen.tsx
```

---

# 2. Prerequisites

### Required globally:
- **Python 3.10+** (you use 3.11)
- **Node.js 18+** and npm
- **Expo CLI** (no install needed — we use npx)
- A phone with **Expo Go** OR an emulator

---

# 3. Backend — Setup & Run

### 3.1. Create virtual environment
```
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 3.2. Install dependencies
```
pip install -r requirements.txt
```

### 3.3. Install NLTK data (run once)
```
python3 -c "import nltk; nltk.download('stopwords')"
```

### 3.4. Rebuild the index (optional if index.json exists)
```
python3 indexing.py
```

### 3.5. Rebuild similarity graph (optional)
```
python3 similarity.py
```

### 3.6. Recompute PageRank (optional)
```
python3 pagerank.py
```

### 3.7. Run FastAPI backend
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend is now available at:
```
http://YOUR_LOCAL_IP:8000
```

---

# 4. Web App (React) — Setup & Run

### 4.1. Install dependencies
```
cd web
npm install
```

### 4.2. Set API IP
Edit `web/src/api.ts`:

```
export const API_BASE = "http://YOUR_LOCAL_IP:8000";
```

### 4.3. Start development server
```
npm run dev
```

The web app runs at:
```
http://localhost:5173
```

---

# 5. Mobile App (React-Native + Expo)

### 5.1. Install npm packages
```
cd mobile
npm install
```

### 5.2. Set backend IP
Edit:
```
mobile/src/config.ts
```

Example:
```
export const API_BASE = "http://192.168.0.31:8000";
```

### 5.3. Start Expo
**Use tunnel mode so your phone can connect easily:**

```
npx expo start --tunnel
```

Then scan the QR code with **Expo Go** on your phone.

---

# 6. Features Overview

### 🔍 Search Keyword Mode
- Tokenized full-text search
- Regex mode
- Ranking by:
  - **TF** (term frequency)
  - **PR** (PageRank importance)
  - **TF × PR**

### 🏷️ Search Title Mode
- Title + author matching
- Ranked by PageRank

### 📖 Book Page
- Cover
- Summary
- Authors
- Recommendations (Jaccard similarity)
- Button → Reader mode

### 📚 Reader Mode
- Paginated reading (`/book-page/{id}`)
- Dark / light mode
- Adjustable font size

### 📱 Mobile App
- All web features rewritten in React Native
- Expo-compatible
- Works on real device with Expo Go

---

# 7. Useful Rebuild Commands

Rebuild stopwords + index:
```
python3 indexing.py
```

Recompute similarity graph:
```
python3 similarity.py
```

Recompute PageRank:
```
python3 pagerank.py
```

Reset backend:
```
rm data/index.json data/similarity.json data/pagerank.json
```

---

# 8. Troubleshooting

### 📌 Covers not loading?
Ensure your backend is mounted properly:
```
app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")
```

Open one manually:
```
http://YOUR_IP:8000/covers/cover_1342.jpg
```

### 📌 Mobile app cannot connect?
Use:
```
npx expo start --tunnel
```
And ensure both phone + PC are on same Wi‑Fi.

### 📌 CORS errors?
FastAPI uses:
```
allow_origins=["*"]
```
So usually safe.

---

# 9. License

Free to use for academic / educational purposes.

---

Done ✔  
This version **will not break**, because it's inside a fenced code block and the interface won't try to render it as UI.

If you want, I can also:
✅ Generate a PDF version  
✅ Generate multiple README variants (short, long, academic)  
