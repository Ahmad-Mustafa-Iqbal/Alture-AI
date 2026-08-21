# 🚀 Alture AI — Production Deployment Guide

This guide provides step-by-step instructions for deploying **Alture AI** across modern cloud platforms (Render, Railway, Docker, and Hugging Face Spaces) for **100% free**.

---

## 🌐 Option 1: Deploy on Render (Recommended — 100% Free)

Render provides free hosting for Python web services and connects directly to your GitHub repository.

### Step-by-Step:
1. Go to [Render.com](https://render.com) and create a free account.
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository: `https://github.com/Ahmad-Mustafa-Iqbal/Alture-AI`.
4. Configure the following settings:
   - **Name**: `alture-ai`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**:
     ```bash
     uvicorn deployment.backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `RAPIDAPI_KEY`: `616b70a6a5msh6eee497e99ef8cap135e12jsncb8e7d0f79bc`
   - `RAPIDAPI_HOST`: `jsearch.p.rapidapi.com`
   - `GEMINI_API_KEY`: *(Your Google AI Studio key)*
6. Click **Create Web Service**.
7. Once built, you will receive a public URL: `https://alture-ai.onrender.com`.

---

## 🚂 Option 2: Deploy on Railway (Ultra-Fast Free Tier)

1. Go to [Railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select `Ahmad-Mustafa-Iqbal/Alture-AI`.
4. Add Environment Variables (`RAPIDAPI_KEY`, `RAPIDAPI_HOST`, `GEMINI_API_KEY`).
5. Under **Settings**, click **Generate Domain**.
6. Your live app is accessible at `https://alture-ai.up.railway.app`.

---

## 🐳 Option 3: Run with Docker (Local or Cloud VPS)

You can run the entire platform locally or on any server using Docker:

### 1. Build and Start Container:
```bash
docker compose up --build -d
```

### 2. View Running Logs:
```bash
docker compose logs -f
```

### 3. Open in Browser:
- Interactive UI: [http://localhost:8000](http://localhost:8000)
- OpenAPI Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Stop Container:
```bash
docker compose down
```

---

## 📊 Available Production Endpoints

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/` | Serves Interactive React Frontend |
| `GET` | `/health` | System Health & Model Verification |
| `POST` | `/api/v1/upload-resume` | Multi-format Resume Parser (PDF, DOCX, TXT) |
| `POST` | `/api/v1/search-and-match-jobs` | Live JSearch RapidAPI Streaming & ATS Ranking |
| `POST` | `/api/v1/ai-coach` | Google Gemini 2.0 Career Coach (Tips, Cover Letter, Q&A) |
| `POST` | `/api/v1/download-ats-report` | Enterprise Branded ATS Audit Report (PDF Download) |
| `GET` | `/api/v1/sample-data` | Pre-loaded Candidate Personas & Benchmark Jobs |
