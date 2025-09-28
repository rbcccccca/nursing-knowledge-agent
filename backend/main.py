from fastapi import FastAPI

from .routes.agent import router as agent_router
from .routes.quiz import router as quiz_router


app = FastAPI(title="Nursing Knowledge Agent API")

app.include_router(agent_router, prefix="/agent", tags=["agent"])
app.include_router(quiz_router, prefix="/quiz", tags=["quiz"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health probe for deployment checks."""
    return {"status": "ok"}
