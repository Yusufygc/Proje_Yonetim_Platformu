"""QML için Proje Listeleme ve Filtreleme Modeli (QAbstractListModel)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal, Slot

from domain.models.project import Project

logger = logging.getLogger(__name__)


class ProjectListModel(QAbstractListModel):
    """Projelerin QML ListView içinde filtrelenebilir ve sıralanabilir olarak sunulmasını sağlar."""

    IdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = Qt.ItemDataRole.UserRole + 2
    DescriptionRole = Qt.ItemDataRole.UserRole + 3
    StatusRole = Qt.ItemDataRole.UserRole + 4
    PriorityRole = Qt.ItemDataRole.UserRole + 5
    HealthRole = Qt.ItemDataRole.UserRole + 6
    ProgressRole = Qt.ItemDataRole.UserRole + 7
    ProjectTypeRole = Qt.ItemDataRole.UserRole + 8
    TargetDateRole = Qt.ItemDataRole.UserRole + 9
    GithubRepoRole = Qt.ItemDataRole.UserRole + 10
    LocalPathRole = Qt.ItemDataRole.UserRole + 11
    IsArchivedRole = Qt.ItemDataRole.UserRole + 12

    countChanged = Signal()

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent=parent)
        self._all_projects: list[Project] = []
        self._filtered_projects: list[Project] = []
        self._search_query: str = ""
        self._status_filter: str = "ALL"

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.IdRole: QByteArray(b"projectId"),
            self.TitleRole: QByteArray(b"title"),
            self.DescriptionRole: QByteArray(b"description"),
            self.StatusRole: QByteArray(b"status"),
            self.PriorityRole: QByteArray(b"priority"),
            self.HealthRole: QByteArray(b"health"),
            self.ProgressRole: QByteArray(b"progress"),
            self.ProjectTypeRole: QByteArray(b"projectType"),
            self.TargetDateRole: QByteArray(b"targetDate"),
            self.GithubRepoRole: QByteArray(b"githubRepo"),
            self.LocalPathRole: QByteArray(b"localPath"),
            self.IsArchivedRole: QByteArray(b"isArchived"),
        }

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._filtered_projects)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._filtered_projects)):
            return None

        project = self._filtered_projects[index.row()]
        return self._get_field_by_role(project, role)

    def _get_field_by_role(self, project: Project, role: int) -> Any:
        if role == self.IdRole:
            return project.id
        if role == self.TitleRole:
            return project.title
        if role == self.DescriptionRole:
            return project.short_description or ""
        if role == self.StatusRole:
            return str(project.status.value if hasattr(project.status, "value") else project.status)
        if role == self.PriorityRole:
            return str(project.priority.value if hasattr(project.priority, "value") else project.priority)
        if role == self.HealthRole:
            return str(project.health.value if hasattr(project.health, "value") else project.health)
        if role == self.ProgressRole:
            return int(project.progress_percent or 0)
        if role == self.ProjectTypeRole:
            return project.project_type or ""
        if role == self.TargetDateRole:
            return project.start_date.strftime("%d.%m.%Y") if project.start_date else ""
        if role == self.GithubRepoRole:
            return project.github_url or ""
        if role == self.LocalPathRole:
            return project.docs_url or ""
        if role == self.IsArchivedRole:
            return bool(project.is_archived)
        return None

    def set_projects(self, projects: list[Project]) -> None:
        """Yeni proje listesini atar ve filtreyi uygular."""
        self._all_projects = list(projects)
        self._apply_filter()

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._search_query = query.strip().lower()
        self._apply_filter()

    @Slot(str)
    def setStatusFilter(self, status: str) -> None:
        self._status_filter = status
        self._apply_filter()

    def _apply_filter(self) -> None:
        self.beginResetModel()
        filtered: list[Project] = []
        for p in self._all_projects:
            if not self._matches_filter(p):
                continue
            filtered.append(p)
        self._filtered_projects = filtered
        self.endResetModel()
        self.countChanged.emit()

    def _matches_filter(self, project: Project) -> bool:
        if self._status_filter != "ALL":
            p_status = str(project.status.value if hasattr(project.status, "value") else project.status)
            if p_status != self._status_filter:
                return False
        if not self._search_query:
            return True
        title = (project.title or "").lower()
        desc = (project.short_description or "").lower()
        p_type = (project.project_type or "").lower()
        return self._search_query in title or self._search_query in desc or self._search_query in p_type
