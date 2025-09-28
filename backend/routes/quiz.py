"""Quiz-oriented API endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
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
    category: str | None = None


class QuizGenerationResponse(BaseModel):
    session: QuizSession


class QuizSubmissionRequest(BaseModel):
    session_id: str
    answers: list[dict[str, str]]


class QuizListResponse(BaseModel):
    items: list[dict[str, Any]]


async def get_openai_service() -> OpenAIService:
    return OpenAIService()


async def get_supabase_service() -> SupabaseService:
    return SupabaseService()


@router.post("/generate", response_model=QuizGenerationResponse)
async def generate_quiz(
    payload: QuizGenerationRequest,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> QuizGenerationResponse:
    """Use AI to craft a lightweight study session."""
    questions_payload = await openai_service.build_quiz(payload.model_dump())
    quiz_record = await supabase_service.add_quiz(
        {
            "title": "Quiz from agent" if not payload.seed_terms else f"Quiz: {'/'.join(payload.seed_terms[:3])}",
            "category": payload.category,
            "questions": questions_payload,
            "metadata": {"seed_terms": payload.seed_terms},
        }
    )
    questions = [
        QuizQuestion(
            id=item.get("id", f"q-{index}"),
            prompt=item.get("question", ""),
            type=item.get("type", "definition"),
            options=item.get("options", []),
            answer=item.get("answer", ""),
            explanation=item.get("explanation"),
        )
        for index, item in enumerate(quiz_record.get("questions", []))
    ]
    session = QuizSession(id=quiz_record.get("id", "quiz-session"), user_id=payload.user_id or "anonymous", questions=questions)
    return QuizGenerationResponse(session=session)


@router.get("/", response_model=QuizListResponse)
async def list_quizzes(
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
    category: Annotated[str | None, Query()] = None,
) -> QuizListResponse:
    items = await supabase_service.list_quizzes(category)
    return QuizListResponse(items=items)


@router.get("/{quiz_id}", response_model=dict)
async def get_quiz(
    quiz_id: str,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, Any]:
    record = await supabase_service.get_quiz(quiz_id)
    if not record:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return record


@router.delete("/{quiz_id}", response_model=dict)
async def delete_quiz(
    quiz_id: str,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, str]:
    deleted = await supabase_service.delete_quiz(quiz_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"status": "deleted"}


@router.patch("/{quiz_id}/questions/{question_id}", response_model=dict)
async def update_quiz_question(
    quiz_id: str,
    question_id: str,
    payload: dict[str, Any],
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, Any]:
    updated = await supabase_service.update_quiz_question(quiz_id, question_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated


@router.post("/submit")
async def record_quiz_submission(
    payload: QuizSubmissionRequest,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, str]:
    """Persist quiz attempts for spaced repetition analytics."""
    await supabase_service.record_quiz_attempt(payload.model_dump())
    return {"status": "recorded"}
