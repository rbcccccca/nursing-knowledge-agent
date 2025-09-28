"""CLI helpers for ingesting study materials into the Qdrant vector store."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from backend.services.openai_service import OpenAIService
from backend.services.qdrant_service import QdrantService


async def chunk_document(path: Path) -> list[str]:
    """Split a document into naive chunks placeholder."""
    text = path.read_text(encoding="utf-8")
    return [segment.strip() for segment in text.split("\n\n") if segment.strip()]


async def ingest_files(file_paths: Iterable[Path]) -> None:
    openai_service = OpenAIService()
    qdrant_service = QdrantService()

    for path in file_paths:
        chunks = await chunk_document(path)
        embeddings = await openai_service.embed_text(chunks)
        payloads = [
            {"id": f"{path.name}-{index}", "text": chunk, "embedding": vector}
            for index, (chunk, vector) in enumerate(zip(chunks, embeddings, strict=False))
        ]
        await qdrant_service.upsert_embeddings(payloads)


if __name__ == "__main__":
    import asyncio
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python ingestion.py <files...>")

    file_args = [Path(arg) for arg in sys.argv[1:]]
    asyncio.run(ingest_files(file_args))
