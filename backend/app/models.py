from pydantic import BaseModel, Field


class SourceTrace(BaseModel):
    chunk_id: str
    source: str
    excerpt: str
    relevance: float


class QuestionOut(BaseModel):
    id: str
    ordinal: int
    prompt: str
    topic: str
    difficulty: str
    sources: list[SourceTrace]


class StartOut(BaseModel):
    session_id: str
    role: str
    skills: list[str]
    resume_summary: str
    question: QuestionOut
    max_questions: int


class AnswerIn(BaseModel):
    question_id: str
    answer: str = Field(min_length=10, max_length=12000)


class AnswerOut(BaseModel):
    complete: bool
    question: QuestionOut | None = None
    report: dict | None = None


class ReportOut(BaseModel):
    session_id: str
    role: str
    report: dict
    transcript: list[dict]
