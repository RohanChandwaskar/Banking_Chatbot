import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
CHROMA_DIR = BASE_DIR / "data" / "chroma"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 4

# ONNX MiniLM (see rag.py) — same family as all-MiniLM-L6-v2, lighter for cloud deploy
EMBEDDING_MODEL = "onnx-MiniLM-L6-v2"
COLLECTION_NAME = "banking_docs"

SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Fallback if Groq isn't set (useful for local OpenAI-compatible endpoints)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MAX_HISTORY_TURNS = 6
