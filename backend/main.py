import shutil
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

from backend.config import DOCUMENTS_DIR, SEED_ON_STARTUP
from backend.models import ChatRequest, ChatResponse, HealthResponse
from backend.rag import chat, document_count, ingest_document
from backend.seed_data import seed_if_empty

ALLOWED_EXTENSIONS = {".txt", ".pdf"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    # On Render: set SEED_ON_STARTUP=false if data/chroma is committed to the repo
    seeded = seed_if_empty() if SEED_ON_STARTUP else 0
    app.state.seeded_chunks = seeded
    yield


app = FastAPI(
    title="Headway Banking Support API",
    description="RAG-powered banking chatbot backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        documents_indexed=document_count(),
        vector_db="ChromaDB",
    )


@app.post("/chat", response_model=ChatResponse)
def post_chat(body: ChatRequest):
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        result = chat(message, session_id=body.session_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate response") from e

    return ChatResponse(**result)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    safe_name = Path(file.filename).name
    dest = DOCUMENTS_DIR / safe_name
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        chunks = ingest_document(dest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}") from e

    return {
        "filename": safe_name,
        "chunks_indexed": chunks,
        "total_documents_in_db": document_count(),
    }
