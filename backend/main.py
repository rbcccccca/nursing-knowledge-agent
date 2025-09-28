from fastapi import FastAPI

from routes.agent import router as agent_router
from routes.quiz import router as quiz_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Nursing Knowledge Agent API")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nursing-knowledge-agent.vercel.app"],  # 或改成 ["https://nursing-knowledge-agent.vercel.app"]
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
