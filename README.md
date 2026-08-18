# Nexus — Adaptive Technical Interviews

Nexus is a full-stack candidate screening experience based on the AI/ML & Backend Intern assignment. Candidates upload a resume, choose a target role, complete a grounded technical interview, and receive a structured report.

## Features

- Resume upload and experience-signal extraction
- AI/ML, backend, and data-science interview tracks
- Role-specific questions grounded in curated knowledge topics
- Continuous interview state and answer capture
- Persistent sessions with Cloudflare D1
- Structured results with strengths and recommended focus areas
- Responsive interface and printable reports
- Dynamic Open Graph sharing card

## Requirements

- Node.js 22.13 or newer
- npm 10 or newer

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

The local development environment simulates the `DB` binding declared in `.openai/hosting.json`. The sessions table is created automatically on the first completed interview.

## Production build

```bash
npm run build
npm start
```

## Project structure

- `app/page.tsx` — candidate setup, interview, and report experience
- `app/api/sessions/route.ts` — session persistence API
- `app/globals.css` — responsive visual system
- `db/schema.ts` — interview session schema
- `drizzle/` — database migration
- `worker/index.ts` — Cloudflare-compatible worker entry point

## Architecture

The client owns short-lived interview UI state. Completed sessions are sent to the API route, validated, and stored in D1. The question bank carries a traceable knowledge-source label for every prompt. The Cloudflare Worker-compatible build is produced by Vinext and Vite.

## Notes

The included question engine is deterministic and works without an API key. To connect a live LLM/RAG service, replace the question-bank selection in `app/page.tsx` with a server-side generation route while preserving the existing question, source, and answer data model.
