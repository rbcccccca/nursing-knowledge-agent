"""Agent-facing FastAPI routes for glossary lookup and RAG queries."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
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


class WordEntryUpdate(BaseModel):
    term: str | None = None
    translation: str | None = None
    notes: str | None = None
    categories: list[str] | None = None


class DocumentUploadResponse(BaseModel):
    id: str
    title: str
    filename: str
    summary: str | None = None
    categories: list[str] = Field(default_factory=list)


class DocumentListResponse(BaseModel):
    items: list[DocumentUploadResponse]


class DocumentDetailResponse(DocumentUploadResponse):
    content: str | None = None


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
            "categories": ["agent-query"],
        }
    )

    if "quiz" in payload.query.lower():
        quiz_items = await openai_service.build_quiz({"prompt": payload.query, "answer": answer})
        await supabase_service.add_quiz(
            {
                "title": payload.query[:80],
                "category": "agent",
                "questions": quiz_items,
                "metadata": {"source": "agent_query", "query": payload.query},
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
            "translation": payload.definition_cn,
            "categories": [],
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
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
    q: Annotated[str | None, Query(alias="search")] = None,
) -> WordEntryListResponse:
    """Return stored word entries filtered by optional search term."""
    items = await supabase_service.list_word_entries(q)
    return WordEntryListResponse(items=items)


@router.get("/entries/{entry_id}", response_model=dict)
async def get_word_entry(
    entry_id: str,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, Any]:
    record = await supabase_service.get_word_entry(entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="Entry not found")
    return record


@router.put("/entries/{entry_id}", response_model=dict)
async def update_word_entry(
    entry_id: str,
    payload: WordEntryUpdate,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, Any]:
    updated = await supabase_service.update_word_entry(entry_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")
    return updated


@router.delete("/entries/{entry_id}", response_model=dict)
async def delete_word_entry(
    entry_id: str,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, str]:
    deleted = await supabase_service.delete_word_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}


@router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
    file: UploadFile = File(...),
    title: Annotated[str | None, Form()] = None,
    summary: Annotated[str | None, Form()] = None,
    categories: Annotated[str | None, Form()] = None,
) -> DocumentUploadResponse:
    content = await file.read()
    record = await supabase_service.store_document(
        {
            "filename": file.filename,
            "title": title,
            "summary": summary,
            "categories": [item.strip() for item in (categories or "").split(",") if item.strip()],
        },
        content,
    )
    record.setdefault("categories", [])
    return DocumentUploadResponse(**record)


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
    search: Annotated[str | None, Query()] = None,
) -> DocumentListResponse:
    items = await supabase_service.list_documents(search)
    processed = [
        DocumentUploadResponse(**{**item, "categories": item.get("categories", [])}) for item in items
    ]
    return DocumentListResponse(items=processed)


@router.get("/documents/{doc_id}", response_model=DocumentDetailResponse)
async def get_document(
    doc_id: str,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> DocumentDetailResponse:
    record = await supabase_service.get_document(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    content = await supabase_service.read_document_text(doc_id)
    record.setdefault("categories", [])
    return DocumentDetailResponse(**record, content=content)


@router.delete("/documents/{doc_id}", response_model=dict)
async def delete_document(
    doc_id: str,
    supabase_service: Annotated[SupabaseService, Depends(get_supabase_service)],
) -> dict[str, str]:
    deleted = await supabase_service.delete_document(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted"}
