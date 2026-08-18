from pathlib import Path
from ingest import read_document
from app.config import get_settings
from app.rag.chunker import chunk_text
from app.rag.embeddings import EmbeddingService
from app.rag.store import VectorStore

ROLE_FOLDERS = {"AI / ML Engineer": "ai_ml", "Backend Engineer": "backend", "Data Scientist": "data_science"}

settings = get_settings()
store = VectorStore(settings.chroma_path, EmbeddingService(settings.embedding_model))
root = Path(settings.knowledge_base_path)
for role, folder in ROLE_FOLDERS.items():
    files = [p for p in (root / folder).rglob("*") if p.suffix.lower() in {".pdf", ".txt", ".md"}]
    chunks = [chunk for path in files for chunk in chunk_text(read_document(path), path.name, role)]
    print(f"{role}: {store.ingest(role, chunks)} chunks")
