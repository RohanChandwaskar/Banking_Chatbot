"""Build Chroma index locally, then commit data/chroma for Render (optional)."""

from backend.rag import document_count, ingest_directory
from backend.config import DOCUMENTS_DIR, CHROMA_DIR


def main():
    import shutil

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    n = ingest_directory(DOCUMENTS_DIR)
    print(f"Indexed {n} chunks. Total in DB: {document_count()}")
    print(f"Chroma path: {CHROMA_DIR}")
    print("Commit data/chroma/ to git and set SEED_ON_STARTUP=false on Render.")


if __name__ == "__main__":
    main()
