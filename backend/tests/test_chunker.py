from app.rag.chunker import chunk_text


def test_chunking_preserves_overlap_and_trace_ids():
    text = " ".join(f"word{i}" for i in range(520))
    chunks = chunk_text(text, "book.txt", "AI / ML Engineer", chunk_words=100, overlap_words=20)
    assert len(chunks) >= 6
    assert chunks[0].id == "AI / ML Engineer:book.txt:0"
    assert chunks[0].text.split()[-20:] == chunks[1].text.split()[:20]


def test_empty_document_has_no_chunks():
    assert chunk_text("", "empty.txt", "Backend Engineer") == []
