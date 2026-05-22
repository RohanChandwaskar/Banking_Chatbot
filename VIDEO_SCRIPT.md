# Demo Video Script (5–10 min)

Use this outline when recording your Loom / screen recording for submission.

---

## 1. Intro (30 sec)

> "Hi, I'm [name]. This is my Headway GenAI banking support chatbot. It's a RAG app — it retrieves answers from internal banking documents instead of making things up. I'll walk through architecture, the RAG pipeline, deployment, and what I'd improve next."

Show: GitHub repo + deployed Streamlit URL.

---

## 2. Architecture overview (1.5 min)

Open `architecture.md` or draw on screen:

- **Streamlit** = chat UI
- **FastAPI** = `/chat`, `/upload`, `/health`
- **ChromaDB** = vector store
- **Groq** = LLM for final answer
- **Synthetic docs** in `data/documents/`

> "I kept the stack simple so I could finish in two days: Python end-to-end, no separate React frontend."

---

## 3. RAG walkthrough (2 min)

In repo, open `backend/rag.py`:

1. **Ingestion** — `_read_file` for PDF/TXT  
2. **Chunking** — `_chunk_text` (~500 chars)  
3. **Embeddings** — SentenceTransformers `all-MiniLM-L6-v2` via Chroma  
4. **Retrieval** — `collection.query`, top 4  
5. **Generation** — prompt with context + history → Groq  

> "On startup, `seed_data.py` indexes everything in data/documents if the DB is empty."

Optional: show one document in `data/documents/personal_loans_faq.txt`.

---

## 4. Live demo (2–3 min)

1. Open deployed UI (or local).
2. Ask: **"What is a personal loan?"**  
3. Follow-up: **"What is the interest rate for it?"**  
   - Point out session memory understood "it" = personal loan.
4. Show **sources** caption under the answer.
5. Upload a small TXT in sidebar → confirm success toast.
6. `curl` or Swagger `/health` — show chunk count.

---

## 5. Vector DB (1 min)

> "Chroma stores embeddings on disk. Similarity search is cosine — I retrieve the top 4 chunks and pass them in the prompt. If nothing matches, the bot is instructed to say it doesn't know."

Show `data/chroma/` locally or mention re-seed on Render cold start.

---

## 6. Deployment (1 min)

Open `render.yaml`:

- Two free web services (API + UI)
- `GROQ_API_KEY` in dashboard
- `API_URL` on UI service

> "First request after sleep takes a while on free tier — that's expected."

Paste both public URLs in README.

---

## 7. Challenges (1 min)

Pick 2–3 honest points:

- Embedding model download makes first Render build slow  
- In-memory session resets on deploy restart  
- PDF text extraction quality varies  
- Grounding vs. helpfulness — tuned system prompt to reduce hallucination  

---

## 8. Future improvements (45 sec)

- Streaming responses  
- Redis session store  
- Reranking retrieved chunks  
- CI/CD pipeline  
- Auth on upload endpoint  

---

## 9. Close (15 sec)

> "Thanks for watching — repo and live links are in the README."

---

## Checklist before submitting

- [ ] GitHub repo public
- [ ] README has both deployment URLs
- [ ] `architecture.md` included
- [ ] Video 5–10 minutes
- [ ] Demo shows follow-up question (context retention)
