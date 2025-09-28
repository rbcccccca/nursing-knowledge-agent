"""Thin helper around Qdrant operations (search, upsert)."""

from __future__ import annotations

from typing import Any, Iterable


class QdrantService:
    """Minimal interface for vector search lifecycle."""

    def __init__(self, client: Any | None = None, collection: str | None = None) -> None:
        self._client = client
        self._collection = collection or "nursing-notes"

    async def semantic_search(self, query_embedding: list[float], limit: int = 5) -> list[dict[str, Any]]:
        """Run a semantic query against the configured collection."""
        return []

    async def upsert_embeddings(self, payloads: Iterable[dict[str, Any]]) -> None:
        """Store embeddings in Qdrant (no-op placeholder)."""
        return None
