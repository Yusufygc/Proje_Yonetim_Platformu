"""MemoService — Memo iş kuralları katmanı."""
from __future__ import annotations

from typing import Any, Optional

from core.exceptions.memo_exceptions import MemoNotFoundError, MemoValidationError
from domain.models.memo import Memo
from infrastructure.repositories.memo_repository import MemoRepository


class MemoService:
    def __init__(self, repository: MemoRepository) -> None:
        self._repo = repository

    def get_all(self) -> list[Memo]:
        return self._repo.get_all()

    def get_by_id(self, memo_id: int) -> Memo:
        memo = self._repo.get_by_id(memo_id)
        if memo is None:
            raise MemoNotFoundError(memo_id)
        return memo

    def get_by_id_optional(self, memo_id: int) -> Optional[Memo]:
        return self._repo.get_by_id(memo_id)

    def create(self, title: str, body: str = "", drawing_data: str | None = None) -> Memo:
        if not title or not title.strip():
            raise MemoValidationError("Memo başlığı boş olamaz.")
        memo = Memo(title=title.strip(), body=body, drawing_data=drawing_data)
        return self._repo.create(memo)

    def update(self, memo_id: int, **kwargs: Any) -> Memo:
        memo = self.get_by_id(memo_id)
        if "title" in kwargs and not str(kwargs["title"]).strip():
            raise MemoValidationError("Memo başlığı boş olamaz.")
        for key, value in kwargs.items():
            if hasattr(memo, key):
                setattr(memo, key, value)
        return self._repo.update(memo)

    def delete(self, memo_id: int) -> None:
        self._repo.delete(memo_id)

    def reorder(self, ordered_ids: list[int]) -> None:
        if not ordered_ids:
            return
        self._repo.reorder(ordered_ids)
