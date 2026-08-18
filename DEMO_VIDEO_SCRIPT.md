# Demo video checklist

The assignment requires the candidate to submit a short recorded demonstration. Use this sequence for a focused 3–5 minute video.

1. Show the GitHub repository and briefly explain the Next.js frontend, FastAPI backend, SQLite interview store, and Chroma vector database.
2. Open `backend/knowledge_base/` and explain that the included original notes make the project runnable; prescribed-book PDFs can be added locally and ingested with `python ingest.py`.
3. Start the stack with `docker compose up --build` and open `http://localhost:3000`.
4. Select a target role, upload a PDF or TXT resume, and point out the extracted skills.
5. Start the interview and expand the source-evidence panel to show the retrieved chunk IDs, excerpts, and relevance scores.
6. Submit one strong answer and one deliberately weak answer so the adaptive difficulty and follow-up behavior are visible.
7. Finish the interview and show the score, strengths, gaps, recommendation, and per-question evidence.
8. End on the README setup section and mention that `OPENAI_API_KEY` enables model-generated questions; the grounded fallback works without it.

Before submitting, confirm that the recording clearly shows the application URL, one complete interview flow, RAG traceability, and the final report.
