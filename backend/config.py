import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
CHROMA_DIR = BASE_DIR / "data" / "chroma"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 4

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "banking_docs"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Fallback if Groq isn't set (useful for local OpenAI-compatible endpoints)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MAX_HISTORY_TURNS = 6
