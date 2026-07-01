"""MemoController — Memo sinyalleri ve iş akışı köprüsü."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from domain.models.memo import Memo
from services.memo_service import MemoService

logger = logging.getLogger(__name__)


class MemoController(QObject):
    memos_loaded   = Signal(list)
    memo_created   = Signal(object)
    memo_updated   = Signal(object)
    memo_deleted   = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, service: MemoService) -> None:
        super().__init__()
        self._service = service

    def load_all(self) -> None:
        try:
            memos = self._service.get_all()
            self.memos_loaded.emit(memos)
        except Exception as exc:
            logger.error("Memolar yüklenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def create(self, title: str, body: str = "", drawing_data: str | None = None) -> None:
        try:
            memo = self._service.create(title, body, drawing_data)
            self.memo_created.emit(memo)
        except Exception as exc:
            logger.error("Memo oluşturulamadı: %s", exc)
            self.error_occurred.emit(str(exc))

    def update(self, memo_id: int, **kwargs: Any) -> None:
        try:
            memo = self._service.update(memo_id, **kwargs)
            self.memo_updated.emit(memo)
        except Exception as exc:
            logger.error("Memo güncellenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def delete(self, memo_id: int) -> None:
        try:
            self._service.delete(memo_id)
            self.memo_deleted.emit(memo_id)
        except Exception as exc:
            logger.error("Memo silinemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def get_sync(self, memo_id: int) -> Optional[Memo]:
        return self._service.get_by_id_optional(memo_id)

    def reorder(self, ordered_ids: list[int]) -> None:
        try:
            self._service.reorder(ordered_ids)
        except Exception as exc:
            logger.error("Memolar yeniden siralanamadi: %s", exc)
            self.error_occurred.emit("Memolar sıralanırken hata oluştu.")
