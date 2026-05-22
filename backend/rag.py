import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from pypdf import PdfReader

from backend.config import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DOCUMENTS_DIR,
    EMBEDDING_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    MAX_HISTORY_TURNS,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    TOP_K,
)

# In-memory session history (fine for a 2-day MVP; swap for Redis later)
_sessions: dict[str, list[dict[str, str]]] = {}

_collection = None


def _chunk_text(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if end < len(text):
            last_space = chunk.rfind(" ")
            if last_space > CHUNK_SIZE // 2:
                chunk = chunk[:last_space]
                end = start + last_space
        chunks.append(chunk.strip())
        start = end - CHUNK_OVERLAP
        if start < 0:
            start = 0
        if end >= len(text):
            break
    return [c for c in chunks if c]


def _read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def _get_collection():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # 🌟 Uses a lightweight, low-memory production embedding function
    # Fast startup, handles file uploads perfectly, and uses less than 40MB RAM!
    from chromadb.utils import embedding_functions
    ef = embedding_functions.DefaultEmbeddingFunction()
    
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

def ingest_document(file_path: Path) -> int:
    """Load a PDF/TXT file, chunk it, and store embeddings in ChromaDB."""
    text = _read_file(file_path)
    chunks = _chunk_text(text)
    if not chunks:
        return 0

    collection = _get_collection()
    base_id = file_path.stem
    ids = [f"{base_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": file_path.name, "chunk": i} for i in range(len(chunks))]

    # Upsert so re-uploading the same doc refreshes chunks
    collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def ingest_directory(directory: Path | None = None) -> int:
    directory = directory or DOCUMENTS_DIR
    total = 0
    for path in sorted(directory.glob("*")):
        if path.suffix.lower() in {".txt", ".pdf"}:
            total += ingest_document(path)
    return total


def document_count() -> int:
    collection = _get_collection()
    return collection.count()


def _retrieve(query: str) -> list[dict]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_texts=[query], n_results=min(TOP_K, collection.count()))
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return [{"text": d, "source": m.get("source", "unknown")} for d, m in zip(docs, metas)]


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant documents found."
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[{i}] ({c['source']})\n{c['text']}")
    return "\n\n".join(parts)


def _history_for_prompt(session_id: str) -> str:
    history = _sessions.get(session_id, [])
    if not history:
        return ""
    lines = []
    for turn in history[-MAX_HISTORY_TURNS:]:
        lines.append(f"User: {turn['user']}")
        lines.append(f"Assistant: {turn['assistant']}")
    return "\n".join(lines)


def _call_llm(system: str, user: str) -> str:
    if GROQ_API_KEY:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        return response.choices[0].message.content or ""

    if OPENAI_API_KEY:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        return response.choices[0].message.content or ""

    raise RuntimeError(
        "No LLM API key configured. Set GROQ_API_KEY or OPENAI_API_KEY in .env"
    )


def chat(message: str, session_id: str = "default") -> dict:
    chunks = _retrieve(message)
    context = _format_context(chunks)
    history = _history_for_prompt(session_id)

    system = """You are Headway Bank's customer support assistant.
Answer ONLY using the provided context and conversation history.
If the answer is not in the context, say you don't have that information and suggest contacting support.
Be concise, friendly, and accurate. Do not invent rates, fees, or policies."""

    user_prompt = f"""Conversation so far:
{history or "(none)"}

Retrieved context:
{context}

Customer question: {message}

Answer the question. If the user refers to something earlier (e.g. "it", "that loan"), use the conversation history."""

    answer = _call_llm(system, user_prompt)

    _sessions.setdefault(session_id, []).append({"user": message, "assistant": answer})
    sources = list({c["source"] for c in chunks})

    return {"answer": answer, "sources": sources, "session_id": session_id}
