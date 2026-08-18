from functools import lru_cache
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str):
        self.model_name = model_name

    @lru_cache(maxsize=1)
    def _model(self) -> SentenceTransformer:
        return SentenceTransformer(self.model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()
