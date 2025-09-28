"""Supabase data access helpers for the knowledge base."""

from __future__ import annotations

from typing import Any, Optional

from .knowledge_store import KnowledgeStore


class SupabaseService:
    """Read/write operations against Supabase tables (file-backed stub)."""

    def __init__(self, client: Any | None = None, store: KnowledgeStore | None = None) -> None:
        self._client = client
        self._store = store or KnowledgeStore()

    async def get_user_profile(self, user_id: str) -> Optional[dict[str, Any]]:
        """Fetch a user profile by identifier (not implemented in stub)."""
        return None

    async def upsert_word_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Persist a glossary entry using the knowledge store."""
        return self._store.upsert_term(entry)

    async def update_word_entry(self, entry_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        return self._store.update_term(entry_id, updates)

    async def delete_word_entry(self, entry_id: str) -> bool:
        return self._store.delete_term(entry_id)

    async def get_word_entry(self, entry_id: str) -> Optional[dict[str, Any]]:
        return self._store.get_term(entry_id)

    async def list_word_entries(self, search: str | None = None) -> list[dict[str, Any]]:
        return self._store.list_terms(search)

    async def store_document(self, document: dict[str, Any], content: bytes) -> dict[str, Any]:
        return self._store.add_document(document, content)

    async def list_documents(self, search: str | None = None) -> list[dict[str, Any]]:
        return self._store.list_documents(search)

    async def get_document(self, doc_id: str) -> Optional[dict[str, Any]]:
        return self._store.get_document(doc_id)

    async def read_document_text(self, doc_id: str) -> Optional[str]:
        return self._store.read_document_text(doc_id)

    async def delete_document(self, doc_id: str) -> bool:
        return self._store.delete_document(doc_id)

    async def add_quiz(self, quiz: dict[str, Any]) -> dict[str, Any]:
        return self._store.add_quiz(quiz)

    async def list_quizzes(self, category: str | None = None) -> list[dict[str, Any]]:
        return self._store.list_quizzes(category)

    async def get_quiz(self, quiz_id: str) -> Optional[dict[str, Any]]:
        return self._store.get_quiz(quiz_id)

    async def delete_quiz(self, quiz_id: str) -> bool:
        return self._store.delete_quiz(quiz_id)

    async def update_quiz_question(self, quiz_id: str, question_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        return self._store.update_quiz_question(quiz_id, question_id, updates)

    async def record_quiz_attempt(self, attempt: dict[str, Any]) -> dict[str, Any]:
        """Store quiz attempt metadata for spaced repetition (not implemented)."""
        await self.update_quiz_question(
            attempt.get("quiz_id", ""),
            attempt.get("question_id", ""),
            {
                "user_answer": attempt.get("user_input"),
                "is_correct": attempt.get("is_correct"),
                "answered_at": attempt.get("answered_at"),
            },
        )
        return attempt
