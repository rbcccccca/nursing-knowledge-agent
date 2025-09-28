"""Pydantic models describing user-related entities."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = Field(default=None, alias="displayName")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    timezone: str | None = None


class StudyStats(BaseModel):
    user_id: str
    mastered_terms: int = 0
    pending_reviews: int = 0
    last_review_at: datetime | None = None
