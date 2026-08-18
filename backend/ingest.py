import argparse
from pathlib import Path
from pypdf import PdfReader
from app.config import get_settings
from app.rag.chunker import chunk_text
from app.rag.embeddings import EmbeddingService
from app.rag.store import VectorStore


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest role-specific books and notes into Chroma")
    parser.add_argument("--role", required=True, choices=["AI / ML Engineer", "Backend Engineer", "Data Scientist"])
    parser.add_argument("--path", required=True, help="PDF, TXT, MD file or directory")
    args = parser.parse_args()
    source = Path(args.path)
    files = [source] if source.is_file() else [p for p in source.rglob("*") if p.suffix.lower() in {".pdf", ".txt", ".md"}]
    settings = get_settings()
    store = VectorStore(settings.chroma_path, EmbeddingService(settings.embedding_model))
    total = 0
    for path in files:
        chunks = chunk_text(read_document(path), path.name, args.role)
        total += store.ingest(args.role, chunks)
        print(f"{path.name}: {len(chunks)} chunks")
    print(f"Ingested {total} chunks for {args.role}")


if __name__ == "__main__":
    main()
