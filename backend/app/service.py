from .config import Settings
from .database import Repository
from .rag.generator import QuestionGenerator
from .rag.store import VectorStore


class InterviewService:
    def __init__(self, settings: Settings, repo: Repository, store: VectorStore, generator: QuestionGenerator):
        self.settings, self.repo, self.store, self.generator = settings, repo, store, generator

    def start(self, role: str, resume_name: str, resume_text: str, summary: str, skills: list[str], candidate_name: str | None) -> tuple[dict, dict]:
        if self.store.count(role) == 0:
            raise RuntimeError(f"No knowledge base is available for {role}. Run the ingestion command first.")
        session = self.repo.create_session(role, resume_name, resume_text, summary, skills, candidate_name)
        query = f"{role} technical interview topics {' '.join(skills)} {summary[:600]}"
        context = self.store.query(role, query)
        generated = self.generator.question(role, summary, skills, context, 1)
        question = self.repo.add_question(session["id"], generated["prompt"], generated["topic"], generated["difficulty"], self._traces(context))
        return session, question

    def answer(self, session_id: str, question_id: str, answer: str) -> tuple[dict | None, dict | None]:
        session = self.repo.get_session(session_id)
        if session["status"] != "active":
            raise ValueError("This interview is already complete")
        self.repo.answer_question(session_id, question_id, answer)
        questions = self.repo.list_questions(session_id)
        if len(questions) >= self.settings.max_questions:
            report = self.generator.report(session["role"], questions)
            self.repo.complete(session_id, report)
            return None, report
        query = f"{session['role']} {' '.join(session['skills'])} follow-up based on candidate answer: {answer[:1200]}"
        context = self.store.query(session["role"], query)
        generated = self.generator.question(session["role"], session["resume_summary"], session["skills"], context, len(questions) + 1, answer)
        question = self.repo.add_question(session_id, generated["prompt"], generated["topic"], generated["difficulty"], self._traces(context))
        return question, None

    def report(self, session_id: str) -> dict:
        session = self.repo.get_session(session_id)
        report = self.repo.get_report(session_id)
        if not report:
            raise ValueError("The interview is not complete")
        return {"session_id": session_id, "role": session["role"], "report": report, "transcript": self.repo.list_questions(session_id)}

    @staticmethod
    def _traces(context: list[dict]) -> list[dict]:
        return [{"chunk_id": c["chunk_id"], "source": c["source"], "excerpt": c["text"][:360], "relevance": round(max(0.0, 1 - float(c["distance"])), 4)} for c in context]
