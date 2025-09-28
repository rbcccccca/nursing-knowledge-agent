# Integration Checklist

## Supabase
- Create tables: `word_entries`, `quiz_sessions`, `quiz_attempts`, `study_stats`.
- Configure Row Level Security policies for user-isolated data access.
- Generate service role key and anon key from project settings.
- Enable Storage bucket `uploads` for PDF/Docx assets.

## Qdrant
- Create collection `nursing-notes` with cosine distance, vector size matching OpenAI embedding output.
- Store connection URL and API key in `.env`.
- Consider payload schema: `text`, `source_path`, `entry_id`, `metadata`.

## OpenAI
- Set usage caps and choose default models: `gpt-4o-mini` and `text-embedding-3-small`.
- Configure rate limiting safeguards inside backend service later.
- Keep key in deployment secrets (Vercel, local `.env`).

## Vercel
- Link GitHub repo `rbcccccca/nursing-knowledge-agent`.
- Add environment variables for production preview: API keys, Supabase, Qdrant.
- Configure deployment to use `frontend` directory with framework preset `Next.js`.

## Workflow
- Establish `main` (production) and `dev` (integration) branches in GitHub.
- Protect `main` with review checks; enable preview deployments from `dev`.
- Automate backend deployment via Render/Fly/Heroku or Supabase Edge Functions (future task).
- Schedule dependency updates and lint/test pipelines using GitHub Actions.

## Render Deployment Notes
- Ensure all backend source files are saved with UTF-8 encoding; non-ASCII placeholders can break build steps.
- When replacing placeholder text, prefer ASCII until OpenAI integration is wired to avoid codec errors.
- After rotating keys or updating `.env`, redeploy the Render service to pick up fresh configuration.
