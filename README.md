# 📚 Book Search Engine

A full‑stack book search platform built on Project Gutenberg data.

This project combines **information retrieval**, **graph algorithms**, and **modern cloud‑native deployment**.  
It is designed both as a functional search engine and as an academic / engineering project showcasing end‑to‑end system design.

---

## 1. What This App Does

The Book Search Engine lets users:

- 🔍 Search books by **content** (keyword or regex)
- 🏷️ Search books by **title / author**
- 📊 Rank results using:
  - Term Frequency (TF)
  - PageRank (graph importance)
  - Combined TF × PageRank
- 📖 Open a book page with:
  - Metadata
  - Cover image
  - Similar book recommendations (Jaccard similarity)
- 📚 Read books in a **reader mode**:
  - Pagination
  - Adjustable font size
  - Dark / light mode

The same backend is consumed by:
- A **React web frontend**
- A **React‑Native mobile app (Expo)**

---

## 2. High‑Level Architecture

```
Browser / Mobile App
        |
        |  /api
        v
Frontend (React + Nginx)
        |
        v
Backend (FastAPI)
        |
        v
Indexed Dataset (PVC)
```
On Kubernetes:
- Backend and frontend run as separate Deployments
- Data is stored on a PersistentVolume
- Ingress exposes frontend and API
- ArgoCD handles GitOps synchronization

---

## 3. Repository Structure

```
bookSearchEngine/
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── download_books.py
│   ├── indexing.py
│   ├── similarity.py
│   ├── pagerank.py
│   ├── requirements.txt
│   └── scripts/build_data.sh
│
├── web/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── src/
│
├── mobile/
│   ├── App.tsx
│   └── src/
│
├── k8s/
│   ├── argocd-app.yml
│   ├── kustomization.yml
│   ├── backend-deployment.yml
│   ├── frontend-deploy.yml
│   ├── ingress-api.yml
│   ├── ingress-frontend.yml
│   ├── pvc.yaml
│   └── data-job.yaml
│
└── .github/workflows/
```

---

## 4. Search Modes Explained

### Keyword Search
- Tokenized full‑text search
- Optional regex matching
- Ranking by TF, PageRank, or TF × PageRank

### Title Search
- Matches book title and authors
- Ranked by PageRank

### Book Page
- Metadata (title, authors, language)
- Cover image
- Snippet preview
- Similar book recommendations

### Reader Mode
- Paginated reading
- Adjustable font size
- Dark / light mode

---

## 5. Backend — Local Run

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('stopwords')"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on:
```
http://<your-ip>:8000
```

---

## 6. Web Frontend — Local Run

```bash
cd web
npm install
npm run dev
```

Runs on:
```
http://localhost:5173
```

---

## 7. Mobile App (Expo)

```bash
cd mobile
npm install
npx expo start --tunnel
```

Scan the QR code with **Expo Go**.

---

## 8. Kubernetes & GitOps Model

- Docker images built by **GitHub Actions**
- Each image tagged with commit SHA
- Workflow updates `kustomization.yml`
- **ArgoCD** syncs cluster state automatically
- Backend and frontend pipelines are fully independent
- Data jobs are run manually

---

## 9. Data Pipeline

A Kubernetes Job:
- Downloads books and covers
- Builds metadata, index, similarity graph, and PageRank

```bash
kubectl apply -f k8s/data-job.yaml
kubectl logs -f job/book-data-build
```

---

## 10. Known Pitfalls

- Deleting the ArgoCD application deletes managed resources
- Data jobs should not be auto‑synced
- Frontend container filesystem is read‑only
- Runtime configuration must use ConfigMaps

---

## 11. Current Status

✅ Backend deployed  
✅ Frontend deployed  
✅ Ingress configured  
✅ CI pipelines working  
✅ ArgoCD syncing correctly  

---

## 12. Possible Improvements

- Horizontal Pod Autoscaling
- Backend caching layer
- Observability (Prometheus / Grafana)
- Separate ArgoCD apps (infra / backend / frontend)
