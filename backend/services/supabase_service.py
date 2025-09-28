"""Supabase data access helpers for the knowledge base."""

from __future__ import annotations

from typing import Any, Optional


class SupabaseService:
    """Read/write operations against Supabase tables."""

    def __init__(self, client: Any | None = None) -> None:
        self._client = client

    async def get_user_profile(self, user_id: str) -> Optional[dict[str, Any]]:
        """Fetch a user profile by identifier."""
        return None

    async def upsert_word_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Persist a glossary entry (placeholder response)."""
        return entry

    async def record_quiz_attempt(self, attempt: dict[str, Any]) -> dict[str, Any]:
        """Store quiz attempt metadata for spaced repetition."""
        return attempt
