"""Seed ChromaDB from files in data/documents on first startup."""

from backend.config import DOCUMENTS_DIR
from backend.rag import document_count, ingest_directory


def seed_if_empty() -> int:
    if document_count() > 0:
        return 0
    if not DOCUMENTS_DIR.exists():
        return 0
    return ingest_directory(DOCUMENTS_DIR)
