"""Domain models for glossary and knowledge base entries."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WordEntry(BaseModel):
    id: str
    term: str
    term_type: str = Field(default="word", description="word | abbreviation")
    definition_cn: Optional[str] = None
    definition_en: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WordEntryCreate(BaseModel):
    term: str
    term_type: str = "word"
    notes: Optional[str] = None
    source: Optional[str] = None
    owner_id: Optional[str] = None


class SemanticChunk(BaseModel):
    id: str
    entry_id: Optional[str] = None
    content: str
    source_path: Optional[str] = None
    embedding: list[float] = Field(default_factory=list)
