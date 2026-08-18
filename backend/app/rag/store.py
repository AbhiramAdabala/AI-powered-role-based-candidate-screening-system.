import re
import chromadb
from .chunker import Chunk
from .embeddings import EmbeddingService


def collection_name(role: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", role.lower()).strip("-")
    return f"nexus-{normalized}"[:63]


class VectorStore:
    def __init__(self, path: str, embeddings: EmbeddingService):
        self.client = chromadb.PersistentClient(path=path)
        self.embeddings = embeddings

    def ingest(self, role: str, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0
        collection = self.client.get_or_create_collection(collection_name(role), metadata={"hnsw:space": "cosine"})
        collection.upsert(ids=[c.id for c in chunks], documents=[c.text for c in chunks], embeddings=self.embeddings.embed([c.text for c in chunks]), metadatas=[{"source": c.source, "role": c.role, "index": c.index} for c in chunks])
        return len(chunks)

    def count(self, role: str) -> int:
        return self.client.get_or_create_collection(collection_name(role)).count()

    def query(self, role: str, query: str, limit: int = 4) -> list[dict]:
        collection = self.client.get_or_create_collection(collection_name(role))
        if collection.count() == 0:
            return []
        result = collection.query(query_embeddings=self.embeddings.embed([query]), n_results=min(limit, collection.count()), include=["documents", "metadatas", "distances"])
        return [{"chunk_id": result["ids"][0][i], "text": result["documents"][0][i], "source": result["metadatas"][0][i]["source"], "distance": result["distances"][0][i]} for i in range(len(result["ids"][0]))]
