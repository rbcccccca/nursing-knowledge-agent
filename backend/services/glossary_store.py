"""Simple file-based glossary storage for demo purposes."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_STORE_PATH = Path("data/glossary.json")


@dataclass
class GlossaryEntry:
    term: str
    translation: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "term": self.term,
            "translation": self.translation,
            "notes": self.notes,
        }


class GlossaryStore:
    """Lightweight JSON persistence layer for glossary entries."""

    def __init__(self, file_path: Path | None = None) -> None:
        self._path = file_path or DEFAULT_STORE_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        with self._path.open("r", encoding="utf-8") as handle:
            try:
                data = json.load(handle)
            except json.JSONDecodeError:
                data = []
        if isinstance(data, list):
            return data
        return []

    def _save(self, items: Iterable[dict[str, Any]]) -> None:
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(list(items), handle, ensure_ascii=False, indent=2)

    def upsert(self, entry: GlossaryEntry) -> dict[str, Any]:
        items = self._load()
        term_key = entry.term.lower()
        updated = False
        for item in items:
            if item.get("term", "").lower() == term_key:
                item.update(entry.to_dict())
                updated = True
                break
        if not updated:
            items.append(entry.to_dict())
        items.sort(key=lambda obj: obj.get("term", "").lower())
        self._save(items)
        return entry.to_dict()

    def list(self, search: str | None = None) -> list[dict[str, Any]]:
        items = self._load()
        if search:
            needle = search.lower()
            items = [
                item
                for item in items
                if needle in item.get("term", "").lower()
                or needle in (item.get("translation") or "").lower()
            ]
        items.sort(key=lambda obj: obj.get("term", "").lower())
        return items
