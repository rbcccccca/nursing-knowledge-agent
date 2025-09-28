"""Supabase data access helpers for the knowledge base."""

from __future__ import annotations

from typing import Any, Optional

from .glossary_store import GlossaryEntry, GlossaryStore


class SupabaseService:
    """Read/write operations against Supabase tables (file-backed stub)."""

    def __init__(self, client: Any | None = None, store: GlossaryStore | None = None) -> None:
        self._client = client
        self._store = store or GlossaryStore()

    async def get_user_profile(self, user_id: str) -> Optional[dict[str, Any]]:
        """Fetch a user profile by identifier (not implemented in stub)."""
        return None

    async def upsert_word_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Persist a glossary entry using the local glossary store."""
        glossary_entry = GlossaryEntry(
            term=entry.get("term", ""),
            translation=entry.get("translation"),
            notes=entry.get("notes"),
        )
        return self._store.upsert(glossary_entry)

    async def list_word_entries(self, search: str | None = None) -> list[dict[str, Any]]:
        """Return stored entries filtered by optional search term."""
        return self._store.list(search)

    async def record_quiz_attempt(self, attempt: dict[str, Any]) -> dict[str, Any]:
        """Store quiz attempt metadata for spaced repetition (not implemented)."""
        return attempt
