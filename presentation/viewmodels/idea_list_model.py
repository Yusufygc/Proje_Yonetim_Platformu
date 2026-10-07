"""QML için Fikir Havuzu Listeleme Modeli (QAbstractListModel)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
    Slot,
)

from core.text_normalization import normalize_search_text
from domain.models.idea import Idea

logger = logging.getLogger(__name__)


class IdeaListModel(QAbstractListModel):
    """Fikirlerin QML ListView/GridView içinde filtrelenebilir ve listelenebilir olarak sunulmasını sağlar."""

    IdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    ProblemRole = Qt.ItemDataRole.UserRole + 3
    SolutionRole = Qt.ItemDataRole.UserRole + 4
    TargetUserRole = Qt.ItemDataRole.UserRole + 5
    StatusRole = Qt.ItemDataRole.UserRole + 6
    PriorityRole = Qt.ItemDataRole.UserRole + 7
    NotesRole = Qt.ItemDataRole.UserRole + 8
    SourceLinkRole = Qt.ItemDataRole.UserRole + 9
    SortOrderRole = Qt.ItemDataRole.UserRole + 10
    ConvertedProjectIdRole = Qt.ItemDataRole.UserRole + 11

    countChanged = Signal()

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent=parent)
        self._all_ideas: list[Idea] = []
        self._filtered_ideas: list[Idea] = []
        self._search_query: str = ""
        self._status_filter: str = "ALL"

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.IdRole: QByteArray(b"ideaId"),
            self.TitleRole: QByteArray(b"title"),
            self.ProblemRole: QByteArray(b"problem"),
            self.SolutionRole: QByteArray(b"solution"),
            self.TargetUserRole: QByteArray(b"targetUser"),
            self.StatusRole: QByteArray(b"status"),
            self.PriorityRole: QByteArray(b"priority"),
            self.NotesRole: QByteArray(b"notes"),
            self.SourceLinkRole: QByteArray(b"sourceLink"),
            self.SortOrderRole: QByteArray(b"sortOrder"),
            self.ConvertedProjectIdRole: QByteArray(b"convertedProjectId"),
        }

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self._filtered_ideas)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._filtered_ideas)):
            return None
        idea = self._filtered_ideas[index.row()]
        return self._extract_role_data(idea, role)

    def _extract_role_data(self, idea: Idea, role: int) -> Any:
        if role == self.IdRole:
            return idea.id
        if role == self.TitleRole:
            return idea.title
        if role == self.ProblemRole:
            return idea.problem or ""
        if role == self.SolutionRole:
            return idea.solution or ""
        if role == self.TargetUserRole:
            return idea.target_user or ""
        if role == self.StatusRole:
            return idea.status
        if role == self.PriorityRole:
            return idea.priority
        if role == self.NotesRole:
            return idea.notes or ""
        if role == self.SourceLinkRole:
            return idea.source_link or ""
        if role == self.SortOrderRole:
            return idea.sort_order
        if role == self.ConvertedProjectIdRole:
            return idea.converted_project_id or 0
        return None

    def set_ideas(self, ideas: list[Idea]) -> None:
        self._all_ideas = list(ideas)
        self._apply_filters()

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._search_query = normalize_search_text(query.strip())
        self._apply_filters()

    @Slot(str)
    def setStatusFilter(self, status: str) -> None:
        self._status_filter = status
        self._apply_filters()

    def _apply_filters(self) -> None:
        self.beginResetModel()
        self._filtered_ideas = [
            i for i in self._all_ideas if self._matches_filters(i)
        ]
        self.endResetModel()
        self.countChanged.emit()

    def _matches_filters(self, idea: Idea) -> bool:
        if self._search_query:
            q = self._search_query
            in_title = q in normalize_search_text(idea.title)
            in_problem = q in normalize_search_text(idea.problem)
            in_solution = q in normalize_search_text(idea.solution)
            if not (in_title or in_problem or in_solution):
                return False
        if self._status_filter != "ALL" and idea.status != self._status_filter:
            return False
        return True
