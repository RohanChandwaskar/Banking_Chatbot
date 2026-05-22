# Headwy Banking Support Chatbot

RAG-powered banking assistant built for the Headwy GenAI assignment. Answers customer questions on loans, credit cards, and FAQs using document retrieval + an LLM.

**Live Demo:** 
- **Backend API:** [https://banking-chatbot-api-z2dq.onrender.com](https://banking-chatbot-api-z2dq.onrender.com)
- **Frontend UI:** [https://banking-chatbot-ui.onrender.com](https://banking-chatbot-ui.onrender.com)

## What it does

- Chat UI (Streamlit) with history, typing state, and per-session memory
- Full RAG: ingest → chunk → embed → ChromaDB → retrieve → generate
- PDF & TXT upload via API
- FastAPI: `POST /chat`, `POST /upload`, `GET /health`
- Deployed on Render free tier

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Vector DB | ChromaDB (persistent) |
| Embeddings | `all-MiniLM-L6-v2` (local, free) |
| LLM | Groq (`llama-3.1-8b-instant`) |

## Quick start (local)

```bash
cd banking-chatbot
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # add GROQ_API_KEY
```

**Terminal 1 — API**

```bash
uvicorn backend.main:app --reload --port 8000
```

On first run, documents in `data/documents/` are indexed automatically.

**Terminal 2 — UI**

```bash
set API_URL=http://localhost:8000
streamlit run frontend/streamlit_app.py
```

Open http://localhost:8501

## API examples

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is the personal loan interest rate?\", \"session_id\": \"demo1\"}"

curl -X POST http://localhost:8000/upload \
  -F "file=@data/documents/personal_loans_faq.txt"
```

## Deploy on Render

1. Push repo to GitHub
2. [Render Dashboard](https://dashboard.render.com) → **New Blueprint** → connect repo (`render.yaml` creates 2 services)
3. Set `GROQ_API_KEY` on the API service
4. Set `API_URL` on the UI service to the API public URL 
5. Wait for build (~5–10 min first time)

**Out of memory (512MB) on deploy?** The API uses `requirements-api.txt` (no PyTorch / `sentence-transformers`). Embeddings use Chroma’s **ONNX MiniLM** (~80MB RAM vs ~400MB+ for PyTorch).

If the API still OOMs on startup seeding, pre-build the index locally and commit it:

```bash
pip install -r requirements-api.txt
python scripts/build_index.py
# Re-enable data/chroma/ in .gitignore (comment it out), then:
git add data/chroma
git commit -m "Add prebuilt Chroma index for Render"
```

On Render API service, set env `SEED_ON_STARTUP=false`.

> Free tier sleeps after inactivity — first request may take 30–60s to wake.

## Project structure

```
banking-chatbot/
├── backend/          # FastAPI + RAG
├── frontend/         # Streamlit chat
├── data/documents/   # Synthetic banking docs (6 files)
├── render.yaml
├── architecture.md
└── VIDEO_SCRIPT.md
```

## Data

Synthetic Headway Bank documents (Option B in the brief): loan FAQs, card policy, home loan guide, support KB, digital banking manual, general FAQs.

## Notes / limitations

- Session memory is in-process (resets on server restart). Redis would be the next step.
- ChromaDB persists under `data/chroma/` locally; on Render, disk is ephemeral unless you add a disk — re-seeds on cold start from `data/documents/`.
- Answers are grounded in retrieved chunks; if info isn't in docs, the bot says so.

## Author

Built with focus on production-ready structures for the Headwy placement selection assignment.
(Timeline - 3 Days)
