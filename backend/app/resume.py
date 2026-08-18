import io
import re
from pypdf import PdfReader

SKILLS = ["python", "fastapi", "flask", "django", "sql", "postgresql", "mongodb", "redis", "docker", "kubernetes", "aws", "gcp", "azure", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "machine learning", "deep learning", "nlp", "rag", "llm", "react", "next.js", "typescript", "java", "c++", "system design", "microservices"]


def parse_resume(filename: str, content: bytes) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1]
    if suffix == "pdf":
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix in {"txt", "md"}:
        text = content.decode("utf-8", errors="replace")
    else:
        raise ValueError("Resume must be a PDF or UTF-8 text file")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 80:
        raise ValueError("The resume does not contain enough readable text")
    return text[:50000]


def extract_profile(text: str) -> tuple[list[str], str]:
    lower = text.lower()
    skills = [skill for skill in SKILLS if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", lower)]
    lines = [line.strip(" •-\t") for line in text.splitlines() if len(line.strip()) > 20]
    evidence = " ".join(lines[:8])
    summary = evidence[:1200] or text[:1200]
    return skills[:15], summary
