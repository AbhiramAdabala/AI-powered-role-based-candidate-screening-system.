from functools import lru_cache
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import Repository
from .models import AnswerIn, AnswerOut, QuestionOut, ReportOut, SourceTrace, StartOut
from .rag.embeddings import EmbeddingService
from .rag.generator import QuestionGenerator
from .rag.store import VectorStore
from .resume import extract_profile, parse_resume
from .service import InterviewService

settings = get_settings()
app = FastAPI(title="Nexus Interview API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.frontend_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@lru_cache
def service() -> InterviewService:
    embeddings = EmbeddingService(settings.embedding_model)
    return InterviewService(settings, Repository(settings), VectorStore(settings.chroma_path, embeddings), QuestionGenerator(settings))


def question_out(question: dict) -> QuestionOut:
    return QuestionOut(id=question["id"], ordinal=question["ordinal"], prompt=question["prompt"], topic=question["topic"], difficulty=question["difficulty"], sources=[SourceTrace(**source) for source in question["sources"]])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm": "openai" if settings.openai_api_key else "grounded-fallback"}


@app.post("/api/interviews/start", response_model=StartOut)
async def start_interview(role: str = Form(...), candidate_name: str | None = Form(None), resume: UploadFile = File(...)) -> StartOut:
    try:
        content = await resume.read()
        if len(content) > 10 * 1024 * 1024:
            raise ValueError("Resume exceeds the 10 MB limit")
        text = parse_resume(resume.filename or "resume.pdf", content)
        skills, summary = extract_profile(text)
        session, question = service().start(role, resume.filename or "resume", text, summary, skills, candidate_name)
        return StartOut(session_id=session["id"], role=role, skills=skills, resume_summary=summary, question=question_out(question), max_questions=settings.max_questions)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc


@app.post("/api/interviews/{session_id}/answers", response_model=AnswerOut)
def submit_answer(session_id: str, payload: AnswerIn) -> AnswerOut:
    try:
        question, report = service().answer(session_id, payload.question_id, payload.answer)
        return AnswerOut(complete=report is not None, question=question_out(question) if question else None, report=report)
    except KeyError as exc:
        raise HTTPException(404, "Interview session not found") from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.get("/api/interviews/{session_id}/report", response_model=ReportOut)
def get_report(session_id: str) -> dict:
    try:
        return service().report(session_id)
    except KeyError as exc:
        raise HTTPException(404, "Interview session not found") from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
