import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator
from .config import Settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY, candidate_name TEXT, role TEXT NOT NULL,
  resume_name TEXT NOT NULL, resume_text TEXT NOT NULL,
  resume_summary TEXT NOT NULL, skills_json TEXT NOT NULL,
  status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS questions (
  id TEXT PRIMARY KEY, session_id TEXT NOT NULL, ordinal INTEGER NOT NULL,
  prompt TEXT NOT NULL, topic TEXT NOT NULL, difficulty TEXT NOT NULL,
  sources_json TEXT NOT NULL, answer TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id)
);
CREATE INDEX IF NOT EXISTS idx_questions_session_ordinal ON questions(session_id, ordinal);
CREATE TABLE IF NOT EXISTS reports (
  session_id TEXT PRIMARY KEY, report_json TEXT NOT NULL, created_at TEXT NOT NULL,
  FOREIGN KEY(session_id) REFERENCES sessions(id)
);
"""


class Repository:
    def __init__(self, settings: Settings):
        self.path = settings.database_url
        with self.connection() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def create_session(self, role: str, resume_name: str, resume_text: str, summary: str, skills: list[str], candidate_name: str | None) -> dict:
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self.connection() as conn:
            conn.execute("INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (session_id, candidate_name, role, resume_name, resume_text, summary, json.dumps(skills), "active", now))
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> dict:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            raise KeyError(session_id)
        result = dict(row)
        result["skills"] = json.loads(result.pop("skills_json"))
        return result

    def add_question(self, session_id: str, prompt: str, topic: str, difficulty: str, sources: list[dict]) -> dict:
        question_id = str(uuid.uuid4())
        with self.connection() as conn:
            ordinal = conn.execute("SELECT COUNT(*) FROM questions WHERE session_id = ?", (session_id,)).fetchone()[0] + 1
            conn.execute("INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?)", (question_id, session_id, ordinal, prompt, topic, difficulty, json.dumps(sources), datetime.now(timezone.utc).isoformat()))
        return self.get_question(question_id)

    def get_question(self, question_id: str) -> dict:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
        if not row:
            raise KeyError(question_id)
        result = dict(row)
        result["sources"] = json.loads(result.pop("sources_json"))
        return result

    def answer_question(self, session_id: str, question_id: str, answer: str) -> None:
        with self.connection() as conn:
            cur = conn.execute("UPDATE questions SET answer = ? WHERE id = ? AND session_id = ? AND answer IS NULL", (answer, question_id, session_id))
            if cur.rowcount != 1:
                raise ValueError("Question was not found or was already answered")

    def list_questions(self, session_id: str) -> list[dict]:
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM questions WHERE session_id = ? ORDER BY ordinal", (session_id,)).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["sources"] = json.loads(item.pop("sources_json"))
            results.append(item)
        return results

    def complete(self, session_id: str, report: dict) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self.connection() as conn:
            conn.execute("UPDATE sessions SET status = 'complete' WHERE id = ?", (session_id,))
            conn.execute("INSERT OR REPLACE INTO reports VALUES (?, ?, ?)", (session_id, json.dumps(report), now))

    def get_report(self, session_id: str) -> dict | None:
        with self.connection() as conn:
            row = conn.execute("SELECT report_json FROM reports WHERE session_id = ?", (session_id,)).fetchone()
        return json.loads(row[0]) if row else None
