from app.resume import extract_profile, parse_resume


def test_text_resume_parsing_and_skill_extraction():
    content = ("Backend engineer with Python, FastAPI, PostgreSQL, Docker, AWS, and system design experience. " * 3).encode()
    text = parse_resume("resume.txt", content)
    skills, summary = extract_profile(text)
    assert {"python", "fastapi", "postgresql", "docker", "aws", "system design"}.issubset(set(skills))
    assert len(summary) > 80


def test_rejects_unsupported_resume():
    try:
        parse_resume("resume.docx", b"content" * 30)
    except ValueError as exc:
        assert "PDF" in str(exc)
    else:
        raise AssertionError("Unsupported file should be rejected")
