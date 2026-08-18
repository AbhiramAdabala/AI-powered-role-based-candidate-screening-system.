# Nexus — AI-Powered Role-Based Candidate Screening

Nexus is a complete resume-aware technical interview system. It parses a candidate resume, retrieves role-specific evidence from a vector database, generates grounded questions, adapts to prior answers, persists the full interview, and produces an evidence-based report.

## Assignment coverage

- React/Vinext frontend with resume upload, role selection, interview, source trace, and results
- Python FastAPI service with validation, service separation, and consistent errors
- PDF and text resume parsing with skill and experience-signal extraction
- Role-specific document ingestion with overlapping chunking
- Sentence Transformer embeddings stored in persistent Chroma collections
- Dynamic queries combining role, resume evidence, and the previous answer
- OpenAI-generated questions grounded in retrieved chunks, with a no-key grounded fallback
- Adaptive follow-ups and progressive difficulty
- SQLite persistence for sessions, questions, answers, reports, and trace metadata
- Source chunk IDs, excerpts, relevance scores, and book filenames attached to every question
- Docker Compose for one-command local operation
- Unit tests for resume processing and chunking

## Architecture

```text
Resume PDF/TXT
    ↓
FastAPI upload validation → resume parser → skills + summary
    ↓                                      ↓
dynamic retrieval query ← role + profile + previous answer
    ↓
Sentence Transformer → Chroma vector search → top evidence chunks
    ↓
grounded question generator → question + trace metadata
    ↓
React interview UI → candidate answer → SQLite session store
    ↓
adaptive follow-up or structured final report
```

The backend is split into configuration, resume processing, persistence, RAG components, and interview orchestration. The frontend never calls the model or vector database directly.

## Quick start with Docker

Requirements: Docker Desktop and Docker Compose.

```bash
cp .env.example .env
# Add OPENAI_API_KEY to .env for LLM-generated questions.
docker compose up --build
```

Open:

- Frontend: http://localhost:3000
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

The container ingests the included original foundation notes at startup. The vector index and interview database persist in the `nexus-data` volume.

## Run without Docker

Use Node.js 22.13+ and Python 3.11+.

```bash
# Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # use cp on macOS/Linux
python bootstrap.py
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
npm install
copy .env.example .env.local  # use cp on macOS/Linux
npm run dev
```

## Use the prescribed books

The assignment names books such as *Machine Learning* by Tom Mitchell, *The Hundred-Page Machine Learning Book*, and *Introduction to Machine Learning with Python*. Obtain the PDFs legally, place them under the matching folder in `backend/knowledge_base/`, and ingest them:

```bash
cd backend
python ingest.py --role "AI / ML Engineer" --path knowledge_base/ai_ml
python ingest.py --role "Backend Engineer" --path knowledge_base/backend
python ingest.py --role "Data Scientist" --path knowledge_base/data_science
```

PDFs are intentionally not committed because redistribution rights vary. The included original notes make the complete pipeline runnable immediately.

## API lifecycle

### Start an interview

`POST /api/interviews/start` as multipart form data:

- `resume`: PDF or TXT, up to 10 MB
- `role`: `AI / ML Engineer`, `Backend Engineer`, or `Data Scientist`
- `candidate_name`: optional

The response includes extracted skills, resume summary, the first generated question, and its retrieved source traces.

### Submit an answer

`POST /api/interviews/{session_id}/answers`

```json
{"question_id":"...","answer":"..."}
```

The service stores the answer and returns either an adaptive next question or the final report.

### Retrieve the report

`GET /api/interviews/{session_id}/report`

Returns the report and complete traceable transcript.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY` | Enables LLM question and report generation | grounded fallback |
| `OPENAI_MODEL` | OpenAI model | `gpt-4.1-mini` |
| `DATABASE_URL` | SQLite file | `./data/nexus.db` |
| `CHROMA_PATH` | Persistent vector store | `./data/chroma` |
| `EMBEDDING_MODEL` | Sentence Transformer model | `all-MiniLM-L6-v2` |
| `MAX_QUESTIONS` | Questions per interview | `5` |
| `FRONTEND_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | Browser-visible API URL | `http://localhost:8000` |

## Tests and builds

```bash
cd backend && pytest -q
cd .. && npm run build
```

## Project structure

```text
app/                         React interview experience
backend/app/main.py          FastAPI routes
backend/app/service.py       Interview lifecycle orchestration
backend/app/database.py      SQLite repository and schema
backend/app/resume.py        Resume parsing and skill extraction
backend/app/rag/             Chunking, embeddings, Chroma, generation
backend/knowledge_base/      Role-specific source documents
backend/tests/               Unit tests
docker-compose.yml           Full local stack
```

## Demo video checklist

Record a short video showing:

1. `docker compose up --build`
2. API health and the ingested role collections
3. Resume upload and extracted skills
4. A generated question and its retrieved source chunks
5. An answer producing an adaptive follow-up
6. Completion of the interview and final report
7. SQLite records or the report endpoint proving persistence

The demo video itself must be recorded and submitted by the candidate; it is the only assignment deliverable that cannot be generated from source code alone.
