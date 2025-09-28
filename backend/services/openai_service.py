"""Utility wrappers around OpenAI API usage for the nursing knowledge agent."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Iterable

from openai import OpenAI

from backend.config import get_settings

DEFAULT_COMPLETION_MODEL = "gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


class OpenAIService:
    """Encapsulates requests to OpenAI for completions and embeddings."""

    def __init__(self, client: OpenAI | None = None) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        self._client = client or OpenAI(api_key=settings.openai_api_key)
        self._completion_model = DEFAULT_COMPLETION_MODEL
        self._embedding_model = DEFAULT_EMBEDDING_MODEL

    async def explain_term(self, prompt: str) -> str:
        """Generate an explanatory answer for the supplied prompt."""
        system_prompt = (
            "You are a bilingual nursing tutor. Provide concise, clinically accurate explanations "
            "with Chinese and English context when helpful."
        )
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self._completion_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    async def translate_dual_language(self, text: str) -> dict[str, str]:
        """Return bilingual translation output template."""
        prompt = (
            "Translate the following nursing text into simplified Chinese while keeping key terms in English when necessary."
        )
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self._completion_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )
        translated = response.choices[0].message.content.strip()
        return {"original": text, "translated": translated}

    async def build_quiz(self, seed: dict[str, Any]) -> list[dict[str, Any]]:
        """Produce quiz items based on the supplied seed payload."""
        instructions = (
            "Generate a JSON array of quiz questions for nursing students. Each question must include "
            "fields: question, type (spelling|definition|abbreviation|usage), options (array, empty allowed), "
            "answer, explanation. Ensure valid JSON."
        )
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self._completion_model,
            messages=[
                {"role": "system", "content": instructions},
                {
                    "role": "user",
                    "content": (
                        "Seed data for quiz generation: " + json.dumps(seed, ensure_ascii=False)
                    ),
                },
            ],
            temperature=0.6,
        )
        raw_content = response.choices[0].message.content.strip()
        try:
            quiz_items = json.loads(raw_content)
        except json.JSONDecodeError:
            quiz_items = []
        if not isinstance(quiz_items, list):
            quiz_items = []
        return quiz_items

    async def embed_text(self, chunks: Iterable[str]) -> list[list[float]]:
        """Generate embeddings for the supplied text chunks."""
        inputs = list(chunks)
        if not inputs:
            return []
        response = await asyncio.to_thread(
            self._client.embeddings.create,
            model=self._embedding_model,
            input=inputs,
        )
        return [item.embedding for item in response.data]
