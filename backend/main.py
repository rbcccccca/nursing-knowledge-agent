"""Main FastAPI application setup."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes.agent import router as agent_router
from .routes.quiz import router as quiz_router


settings = get_settings()
app = FastAPI(title="Nursing Knowledge Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router, prefix="/agent", tags=["agent"])
app.include_router(quiz_router, prefix="/quiz", tags=["quiz"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health probe for deployment checks."""
    return {"status": "ok"}
