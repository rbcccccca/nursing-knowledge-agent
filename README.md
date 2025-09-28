# Nursing Knowledge Agent

Multi-module project that delivers a bilingual nursing knowledge base, an AI-powered agent with RAG search, and adaptive quiz tooling.

## Repository Layout

- `frontend/` - Next.js UI with Supabase auth integration and API client stubs.
- `backend/` - FastAPI service orchestrating OpenAI, Qdrant, and Supabase connectors.
- `vectorstore/` - Utilities to chunk and ingest documents into Qdrant.
- `.env.example` - Environment variables required across services.

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Existing accounts: Vercel, Supabase, Qdrant Cloud, OpenAI (keys stored in `.env`).

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Key environment variables:

- `OPENAI_API_KEY` - required for explanations, translations, quiz generation, and embeddings.
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` - reserved for future Supabase integration (file-backed store used locally).
- `QDRANT_URL`, `QDRANT_API_KEY` - optional until semantic search is wired to a live vector store.
- `CORS_ALLOWED_ORIGINS` - comma-separated list of origins (e.g. `https://nursing-knowledge-agent.vercel.app`); defaults to `*` for local testing.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` to point at your FastAPI instance.

### Vectorstore Ingestion

```bash
python -m vectorstore.ingestion data/my-notes.txt
```

This script performs minimal chunking and will reuse the OpenAI embeddings service once credentials are supplied.

## Feature Highlights

- **Knowledge Base** - Agent lookups automatically save bilingual notes. Terms are fully editable, sortable, and deletable. Upload TXT/PDF files to enrich the retrieval corpus; text is extracted and stored for RAG use.
- **AI Assistant** - Markdown-rendered answers with optional semantic citations and automatic quiz capture when prompts mention "quiz".
- **Quiz Vault** - Generated quizzes persist with categories and timestamps, supporting review, deletion, and future scheduling logic.
- **Mobile-first UI** - Polished glassmorphism layout optimized for iPhone-sized screens with quick navigation between modules.

## Next Steps

1. Replace the local JSON store with Supabase/Postgres tables and Storage buckets for collaborative usage.
2. Wire Qdrant search to uploaded document embeddings for richer RAG answers.
3. Expand quiz analytics with spaced repetition scheduling and answer tracking.
4. Harden auth flows on the frontend using Supabase Auth helpers.
5. Add automated tests and CI workflows covering backend endpoints and frontend utilities.
