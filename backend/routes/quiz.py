"""Quiz-oriented API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..models.quiz import QuizQuestion, QuizSession
from ..services.openai_service import OpenAIService
from ..services.supabase_service import SupabaseService

router = APIRouter()


class QuizGenerationRequest(BaseModel):
    user_id: str | None = None
    seed_terms: list[str] = Field(default_factory=list)
    question_types: list[str] = Field(default_factory=list)
    total_questions: int = 5


class QuizGenerationResponse(BaseModel):
    session: QuizSession


class QuizSubmissionRequest(BaseModel):
    session_id: str
    answers: list[dict[str, str]]


async def get_openai_service() -> OpenAIService:
    return OpenAIService()


async def get_supabase_service() -> SupabaseService:
    return SupabaseService()


@router.post("/generate", response_model=QuizGenerationResponse)
async def generate_quiz(
    payload: QuizGenerationRequest,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
) -> QuizGenerationResponse:
    """Use AI to craft a lightweight study session."""
    questions_payload = await openai_service.build_quiz(payload.model_dump())
    questions = [
        QuizQuestion(
            id=f"q-{index}",
            prompt=item.get("question", ""),
            type=item.get("type", "definition"),
            options=item.get("options", []),
            answer=item.get("answer", ""),
            explanation=item.get("explanation"),
        )
        for index, item in enumerate(questions_payload)
    ]
    session = QuizSession(id="session-placeholder", user_id=payload.user_id or "anonymous", questions=questions)
    return QuizGenerationResponse(session=session)


@router.post("/submit")
async def record_quiz_submission(
    payload: QuizSubmissionRequest,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, str]:
    """Persist quiz attempts for spaced repetition analytics."""
    await supabase_service.record_quiz_attempt(payload.model_dump())
    return {"status": "recorded"}
