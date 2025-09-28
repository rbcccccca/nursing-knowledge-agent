# Development Roadmap

## Persistence Layer
- Design Supabase schema for glossary entries, file uploads, quiz sessions, and attempt history.
- Implement migrations/DDL scripts and document table ownership + RLS policies.
- Create CRUD routes in FastAPI for word entries, file metadata, and quiz tracking.

## File Ingestion
- Add PDF/Docx upload endpoint that streams to Supabase Storage.
- Add background worker or async task to chunk uploads and push embeddings to Qdrant.
- Track ingestion status per file for dashboard visibility.

## Quiz Experience
- Expand OpenAI prompt design for different question types.
- Persist generated sessions and user responses; compute spaced-repetition schedule.
- Surface quiz analytics in the frontend dashboard.

## Quality Bar
- Configure lint/test scripts: `ruff` or `flake8` + `pytest` for backend, `eslint` + `vitest` or `jest` for frontend.
- Add GitHub Actions workflow to run unit tests, linting, and type checks on push/PR.
- Define seeding scripts and fixtures for local development.
