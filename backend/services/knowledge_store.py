"""Persistent knowledge store for terms, documents, and quizzes."""

from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

from PyPDF2 import PdfReader

DEFAULT_STORE_PATH = Path("data/knowledge_store.json")
DOCUMENTS_DIR = Path("data/documents")


class KnowledgeStore:
    """File-backed persistence layer for glossary terms, documents, and quizzes."""

    def __init__(self, file_path: Path | None = None) -> None:
        self._path = file_path or DEFAULT_STORE_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write({"terms": [], "documents": [], "quizzes": []})

    # Internal helpers -------------------------------------------------
    def _read(self) -> dict[str, Any]:
        with self._path.open("r", encoding="utf-8") as handle:
            try:
                return json.load(handle)
            except json.JSONDecodeError:
                return {"terms": [], "documents": [], "quizzes": []}

    def _write(self, payload: dict[str, Any]) -> None:
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    @staticmethod
    def _now() -> str:
        return datetime.utcnow().isoformat()

    # Term operations --------------------------------------------------
    def upsert_term(self, entry: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        terms: list[dict[str, Any]] = data.get("terms", [])

        entry_id = entry.get("id") or str(uuid4())
        term_lower = entry.get("term", "").strip()
        now = self._now()

        existing = None
        for item in terms:
            if item.get("id") == entry_id or item.get("term", "") == term_lower:
                existing = item
                break

        record = {
            "id": entry_id,
            "term": term_lower,
            "translation": entry.get("translation"),
            "notes": entry.get("notes"),
            "categories": entry.get("categories", []),
            "created_at": existing.get("created_at") if existing else now,
            "updated_at": now,
        }

        if existing:
            terms = [record if item.get("id") == existing.get("id") else item for item in terms]
        else:
            terms.append(record)

        terms.sort(key=lambda item: item.get("term", ""))
        data["terms"] = terms
        self._write(data)
        return record

    def update_term(self, entry_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        data = self._read()
        terms: list[dict[str, Any]] = data.get("terms", [])
        updated = None
        for item in terms:
            if item.get("id") == entry_id:
                item.update({k: v for k, v in updates.items() if k in {"term", "translation", "notes", "categories"}})
                item["updated_at"] = self._now()
                updated = item
                break
        if updated:
            terms.sort(key=lambda item: item.get("term", ""))
            data["terms"] = terms
            self._write(data)
        return updated

    def delete_term(self, entry_id: str) -> bool:
        data = self._read()
        terms: list[dict[str, Any]] = data.get("terms", [])
        new_terms = [item for item in terms if item.get("id") != entry_id]
        if len(new_terms) == len(terms):
            return False
        data["terms"] = new_terms
        self._write(data)
        return True

    def get_term(self, entry_id: str) -> dict[str, Any] | None:
        terms = self._read().get("terms", [])
        for item in terms:
            if item.get("id") == entry_id:
                return item
        return None

    def list_terms(self, search: str | None = None) -> list[dict[str, Any]]:
        terms = self._read().get("terms", [])
        if search:
            needle = search.lower()
            terms = [
                item
                for item in terms
                if needle in (item.get("term", "").lower())
                or needle in (item.get("translation", "") or "").lower()
                or needle in (item.get("notes", "") or "").lower()
            ]
        terms.sort(key=lambda item: item.get("term", ""))
        return terms

    # Document operations ----------------------------------------------
    def add_document(self, document: dict[str, Any], content: bytes) -> dict[str, Any]:
        data = self._read()
        docs: list[dict[str, Any]] = data.get("documents", [])
        doc_id = str(uuid4())
        filename = document.get("filename") or f"document-{doc_id}"
        now = self._now()

        extension = Path(filename).suffix.lower() or ".txt"
        original_path = DOCUMENTS_DIR / f"{doc_id}{extension}"
        original_path.write_bytes(content)

        extracted_text = self._extract_text(extension, content)
        text_path = DOCUMENTS_DIR / f"{doc_id}.txt"
        text_path.write_text(extracted_text, encoding="utf-8")

        record = {
            "id": doc_id,
            "filename": filename,
            "title": document.get("title") or Path(filename).stem,
            "summary": document.get("summary"),
            "categories": document.get("categories", []),
            "stored_path": str(text_path),
            "original_path": str(original_path),
            "created_at": now,
            "updated_at": now,
        }

        docs.append(record)
        data["documents"] = docs
        self._write(data)
        return record

    @staticmethod
    def _extract_text(extension: str, content: bytes) -> str:
        if extension in {".txt", ".md", ".csv"}:
            return content.decode("utf-8", errors="ignore")
        if extension == ".pdf":
            reader = PdfReader(BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        return content.decode("utf-8", errors="ignore")

    def update_document(self, doc_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        data = self._read()
        docs: list[dict[str, Any]] = data.get("documents", [])
        updated = None
        for doc in docs:
            if doc.get("id") == doc_id:
                doc.update({k: v for k, v in updates.items() if k in {"title", "summary", "categories"}})
                doc["updated_at"] = self._now()
                updated = doc
                break
        if updated:
            data["documents"] = docs
            self._write(data)
        return updated

    def delete_document(self, doc_id: str) -> bool:
        data = self._read()
        docs: list[dict[str, Any]] = data.get("documents", [])
        new_docs = []
        text_path: Path | None = None
        original_path: Path | None = None
        for doc in docs:
            if doc.get("id") == doc_id:
                text_path = Path(doc.get("stored_path", ""))
                original_path = Path(doc.get("original_path", ""))
            else:
                new_docs.append(doc)
        if len(new_docs) == len(docs):
            return False
        if text_path and text_path.exists():
            text_path.unlink()
        if original_path and original_path.exists():
            original_path.unlink()
        data["documents"] = new_docs
        self._write(data)
        return True

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        docs = self._read().get("documents", [])
        for doc in docs:
            if doc.get("id") == doc_id:
                return doc
        return None

    def list_documents(self, search: str | None = None) -> list[dict[str, Any]]:
        docs = self._read().get("documents", [])
        if search:
            needle = search.lower()
            docs = [
                doc
                for doc in docs
                if needle in (doc.get("title", "").lower())
                or needle in (doc.get("filename", "").lower())
                or needle in " ".join(doc.get("categories", [])).lower()
            ]
        docs.sort(key=lambda doc: doc.get("title", ""))
        return docs

    def read_document_text(self, doc_id: str) -> str | None:
        doc = self.get_document(doc_id)
        if not doc:
            return None
        path = Path(doc.get("stored_path", ""))
        if not path.exists():
            return None
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1", errors="ignore")

    # Quiz operations ---------------------------------------------------
    def add_quiz(self, quiz: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        quizzes: list[dict[str, Any]] = data.get("quizzes", [])
        quiz_id = quiz.get("id") or str(uuid4())
        now = self._now()
        questions = quiz.get("questions", [])
        for question in questions:
            question.setdefault("id", str(uuid4()))
        record = {
            "id": quiz_id,
            "title": quiz.get("title") or "Study Quiz",
            "category": quiz.get("category"),
            "questions": questions,
            "created_at": quiz.get("created_at") or now,
            "updated_at": now,
            "metadata": quiz.get("metadata", {}),
        }
        existing = False
        for idx, item in enumerate(quizzes):
            if item.get("id") == quiz_id:
                quizzes[idx] = record
                existing = True
                break
        if not existing:
            quizzes.append(record)
        quizzes.sort(key=lambda item: item.get("created_at", now), reverse=True)
        data["quizzes"] = quizzes
        self._write(data)
        return record

    def list_quizzes(self, category: str | None = None) -> list[dict[str, Any]]:
        quizzes = self._read().get("quizzes", [])
        if category:
            quizzes = [quiz for quiz in quizzes if quiz.get("category") == category]
        quizzes.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return quizzes

    def get_quiz(self, quiz_id: str) -> dict[str, Any] | None:
        quizzes = self._read().get("quizzes", [])
        for quiz in quizzes:
            if quiz.get("id") == quiz_id:
                return quiz
        return None

    def delete_quiz(self, quiz_id: str) -> bool:
        data = self._read()
        quizzes: list[dict[str, Any]] = data.get("quizzes", [])
        new_quizzes = [quiz for quiz in quizzes if quiz.get("id") != quiz_id]
        if len(new_quizzes) == len(quizzes):
            return False
        data["quizzes"] = new_quizzes
        self._write(data)
        return True

    def update_quiz_question(self, quiz_id: str, question_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        data = self._read()
        quizzes: list[dict[str, Any]] = data.get("quizzes", [])
        updated = None
        for quiz in quizzes:
            if quiz.get("id") == quiz_id:
                for question in quiz.get("questions", []):
                    if question.get("id") == question_id:
                        question.update(updates)
                        updated = question
                        quiz["updated_at"] = self._now()
                        break
        if updated:
            data["quizzes"] = quizzes
            self._write(data)
        return updated
