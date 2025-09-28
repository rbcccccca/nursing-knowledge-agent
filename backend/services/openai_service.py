"""Utility wrappers around OpenAI API usage for the nursing knowledge agent."""

from __future__ import annotations

from typing import Any


class OpenAIService:
    """Encapsulates requests to OpenAI for completions and embeddings."""

    def __init__(self, client: Any | None = None) -> None:
        # Client can be injected to ease testing; lazy init happens in configure.
        self._client = client

    async def explain_term(self, prompt: str) -> str:
        """Generate an explanatory answer for the supplied prompt."""
        # TODO: Wire to actual OpenAI completion call.
        return "Model response placeholder"

    async def translate_dual_language(self, text: str) -> dict[str, str]:
        """Return bilingual translation output template."""
        return {"original": text, "translated": "待集成翻译结果"}

    async def build_quiz(self, seed: dict[str, Any]) -> list[dict[str, Any]]:
        """Produce quiz items based on the supplied seed payload."""
        return [
            {
                "question": "Placeholder question",
                "options": [],
                "answer": "",
                "metadata": seed,
            }
        ]

    async def embed_text(self, chunks: list[str]) -> list[list[float]]:
        """Return fake embeddings until OpenAI integration is configured."""
        return [[0.0] * 4 for _ in chunks]
