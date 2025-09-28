"""Quiz model definitions supporting multiple learning modes.""" 

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

QuestionType = Literal["spelling", "definition", "abbreviation", "usage"]


class QuizQuestion(BaseModel):
    id: str
    prompt: str
    type: QuestionType
    options: list[str] = Field(default_factory=list)
    answer: str
    explanation: Optional[str] = None
    source_term_id: Optional[str] = None


class QuizSession(BaseModel):
    id: str
    user_id: str
    questions: list[QuizQuestion]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class QuizSubmission(BaseModel):
    question_id: str
    user_input: str
    is_correct: bool
    answered_at: datetime = Field(default_factory=datetime.utcnow)
