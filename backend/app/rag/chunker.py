from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    role: str
    index: int


def chunk_text(text: str, source: str, role: str, chunk_words: int = 220, overlap_words: int = 40) -> list[Chunk]:
    words = text.split()
    if not words:
        return []
    step = max(1, chunk_words - overlap_words)
    chunks = []
    for index, start in enumerate(range(0, len(words), step)):
        section = words[start:start + chunk_words]
        if len(section) < 35 and chunks:
            break
        chunks.append(Chunk(id=f"{role}:{source}:{index}", text=" ".join(section), source=source, role=role, index=index))
    return chunks
