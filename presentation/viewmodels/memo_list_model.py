"""QML için Notlarım (Memo) Listeleme Modeli (QAbstractListModel)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal, Slot

from core.text_normalization import normalize_search_text
from domain.models.memo import Memo

from PySide6.QtGui import QTextDocument

logger = logging.getLogger(__name__)


def _clean_body_markdown(text: Optional[str]) -> str:
    if not text:
        return ""
    lower = text.lower()
    if "<!doctype" in lower or "<html" in lower or "<body" in lower:
        doc = QTextDocument()
        doc.setHtml(text)
        return doc.toMarkdown().strip()
    return text


class MemoListModel(QAbstractListModel):
    """Notların QML GridView/ListView içinde listelenmesini ve filtrelenmesini sağlar."""

    IdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    BodyRole = Qt.ItemDataRole.UserRole + 3
    DrawingDataRole = Qt.ItemDataRole.UserRole + 4
    SortOrderRole = Qt.ItemDataRole.UserRole + 5
    UpdatedAtRole = Qt.ItemDataRole.UserRole + 6

    countChanged = Signal()

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent=parent)
        self._all_memos: list[Memo] = []
        self._filtered_memos: list[Memo] = []
        self._search_query: str = ""

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.IdRole: QByteArray(b"memoId"),
            self.TitleRole: QByteArray(b"title"),
            self.BodyRole: QByteArray(b"body"),
            self.DrawingDataRole: QByteArray(b"drawingData"),
            self.SortOrderRole: QByteArray(b"sortOrder"),
            self.UpdatedAtRole: QByteArray(b"updatedAt"),
        }

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._filtered_memos)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._filtered_memos)):
            return None
        m = self._filtered_memos[index.row()]
        if role == self.IdRole:
            return m.id
        if role == self.TitleRole:
            return m.title
        if role == self.BodyRole:
            return _clean_body_markdown(m.body)
        if role == self.DrawingDataRole:
            return m.drawing_data or ""
        if role == self.SortOrderRole:
            return m.sort_order
        if role == self.UpdatedAtRole:
            return m.updated_at.strftime("%d.%m.%Y %H:%M") if m.updated_at else ""
        return None

    def set_memos(self, memos: list[Memo]) -> None:
        self._all_memos = list(memos)
        self._apply_filter()

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._search_query = normalize_search_text(query.strip())
        self._apply_filter()

    def _apply_filter(self) -> None:
        self.beginResetModel()
        if not self._search_query:
            self._filtered_memos = list(self._all_memos)
        else:
            q = self._search_query
            self._filtered_memos = [
                m for m in self._all_memos
                if q in normalize_search_text(m.title) or q in normalize_search_text(m.body)
            ]
        self.endResetModel()
        self.countChanged.emit()
