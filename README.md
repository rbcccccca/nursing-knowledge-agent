# Nursing Knowledge Agent

Multi-module project that delivers a bilingual nursing knowledge base, an AI-powered agent with RAG search, and adaptive quiz tooling.

## Repository Layout

- `frontend/` 每 Next.js UI with Supabase auth integration and API client stubs.
- `backend/` 每 FastAPI service orchestrating OpenAI, Qdrant, and Supabase connectors.
- `vectorstore/` 每 Utilities to chunk and ingest documents into Qdrant.
- `.env.example` 每 Environment variables required across services.

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

This script currently performs minimal chunking and uses placeholder embeddings until API keys are configured.

## Next Steps

1. Wire `OpenAIService`, `QdrantService`, and `SupabaseService` to their respective SDKs using keys from `.env`.
2. Flesh out RAG pipelines: document upload API, chunking strategy, metadata storage.
3. Build authenticated flows in Next.js (Supabase Auth helpers, protected routes).
4. Implement quiz persistence and spaced repetition scheduling logic.
5. Connect GitHub repo (`nursing-knowledge-agent`) and create `main` + `dev` branches for deployment to Vercel.
