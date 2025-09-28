"""Agent-facing FastAPI routes for glossary lookup and RAG queries."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from ..models.word_entry import WordEntry, WordEntryCreate
from ..services.openai_service import OpenAIService
from ..services.qdrant_service import QdrantService
from ..services.supabase_service import SupabaseService

router = APIRouter()


class AgentQueryRequest(BaseModel):
    query: str
    user_id: str | None = None
    enable_rag: bool = True


class AgentQueryResponse(BaseModel):
    answer: str
    sources: list[dict[str, str]] = Field(default_factory=list)


class WordEntryResponse(BaseModel):
    entry: WordEntry


class WordEntryListResponse(BaseModel):
    items: list[dict[str, str | None]]


async def get_openai_service() -> OpenAIService:
    return OpenAIService()


async def get_qdrant_service() -> QdrantService:
    return QdrantService()


async def get_supabase_service() -> SupabaseService:
    return SupabaseService()


@router.post("/query", response_model=AgentQueryResponse)
async def query_agent(
    payload: AgentQueryRequest,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
    qdrant_service: Annotated[QdrantService, Depends(get_qdrant_service)],
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> AgentQueryResponse:
    """Return an LLM generated explanation plus optional semantic matches."""
    answer = await openai_service.explain_term(payload.query)
    sources: list[dict[str, str]] = []

    if payload.enable_rag:
        embeddings = await openai_service.embed_text([payload.query])
        if embeddings:
            search_results = await qdrant_service.semantic_search(embeddings[0])
            sources = [
                {"title": item.get("title", ""), "snippet": item.get("text", "")}
                for item in search_results
            ]

    translation_payload = await openai_service.translate_dual_language(payload.query)
    await supabase_service.upsert_word_entry(
        {
            "term": payload.query.strip(),
            "translation": translation_payload.get("translated"),
            "notes": answer,
        }
    )

    return AgentQueryResponse(answer=answer, sources=sources)


@router.post("/entries", response_model=WordEntryResponse)
async def create_word_entry(
    payload: WordEntryCreate,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
) -> WordEntryResponse:
    """Create a knowledge base entry with optional AI-generated metadata."""
    if not payload.notes:
        ai_notes = await openai_service.explain_term(payload.term)
    else:
        ai_notes = payload.notes

    record = await supabase_service.upsert_word_entry(
        {
            "term": payload.term,
            "term_type": payload.term_type,
            "notes": ai_notes,
        }
    )

    entry = WordEntry(
        id=str(record.get("id", payload.term)),
        term=record.get("term", payload.term),
        term_type=record.get("term_type", payload.term_type),
        definition_cn=record.get("translation"),
        definition_en=record.get("definition_en"),
        notes=record.get("notes", ai_notes),
    )

    return WordEntryResponse(entry=entry)


@router.get("/entries", response_model=WordEntryListResponse)
async def list_word_entries(
    q: Annotated[str | None, Query(default=None, alias="search")],
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> WordEntryListResponse:
    """Return stored word entries filtered by optional search term."""
    items = await supabase_service.list_word_entries(q)
    return WordEntryListResponse(items=items)
