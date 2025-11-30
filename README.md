# 📚 Book Search Engine : Full Project Documentation

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
- **Python 3.10+** 
- **Node.js 18+** and npm
- **Expo CLI**
- A phone with **Expo Go** OR an emulator

---

# 3. Backend — Setup & Run

### 3.1. Create virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### 3.2. Install dependencies
```
cd backend
pip install -r requirements.txt
```

### 3.3. Install NLTK data (run once)
```
python3 -c "import nltk; nltk.download('stopwords')"
```

### 3.4. Build the index 
```
python3 indexing.py
```

### 3.5. Build similarity graph
```
python3 similarity.py
```

### 3.6. Compute PageRank
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
npm run dev (or npm run dev -- --host)
```

The web app runs at:
```
http://localhost:5173 (or http://YOUR_LOCAL_IP:5173 if you run with --host)
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

Then scan the QR code with **Expo Go** on your phone. (or else you can access it through any web either on phone or PC in localhost:8081)

---

# 6. Features Overview

### Search Keyword Mode
- Tokenized full-text search
- Regex mode
- Ranking by:
  - **TF** (term frequency)
  - **PR** (PageRank importance)
  - **TF × PR**

### 🏷️ Search Title Mode
- Title + author matching (authors are saved in metadata as `Last Name, First Name` so a search with full name needs adjustments)
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

# 7. Troubleshooting

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
