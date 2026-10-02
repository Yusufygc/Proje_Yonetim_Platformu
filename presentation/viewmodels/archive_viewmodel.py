"""QML Arşiv Ekranı ViewModel'i (ArchiveViewModel)."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from domain.models.project import Project
from presentation.utils.i18n import tr

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)

_STATUS_LABELS = {
    "PLANNED": ("status_planned", "Planlandı"),  # l10n: data
    "DEVELOPMENT": ("status_development", "Geliştirme"),  # l10n: data
    "TEST": ("status_test", "Test"),
    "COMPLETED": ("status_completed", "Tamamlandı"),  # l10n: data
    "ON_HOLD": ("status_on_hold", "Beklemede"),
    "CANCELLED": ("status_cancelled", "İptal Edildi"),  # l10n: data
}


class ArchiveViewModel(QObject):
    """Arşivlenmiş projelerin listelenmesi, geri yüklenmesi ve silinmesi için köprü."""

    archivedProjectsChanged = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._controller = container.project_controller
        self._event_bus = container.event_bus

        self._archived_projects: list[dict[str, Any]] = []
        self._is_loading: bool = False

        self._connect_signals()
        self.loadArchivedProjects()

    def _connect_signals(self) -> None:
        self._controller.archived_projects_loaded.connect(self._on_projects_loaded)
        self._controller.project_restored.connect(self._on_project_changed)
        self._controller.project_deleted.connect(self._on_project_changed)
        self._controller.error_occurred.connect(self._on_error)

    @Slot()
    def loadArchivedProjects(self) -> None:
        self._is_loading = True
        self._controller.load_archived_projects()

    @Slot(int)
    def restoreProject(self, project_id: int) -> None:
        self._controller.restore_archived_project(project_id)
        if self._event_bus:
            self._event_bus.publish(
                "toast.show",
                message=tr("archive_restored_toast", "Proje arşivden başarıyla çıkarıldı."),
                type_="success",
            )

    @Slot(int)
    def deleteProject(self, project_id: int) -> None:
        self._controller.delete_project(project_id)
        if self._event_bus:
            self._event_bus.publish(
                "toast.show",
                message=tr("archive_deleted_toast", "Proje kalıcı olarak silindi."),
                type_="info",
            )

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        self._is_loading = False
        items = []
        for p in projects:
            status_val = p.status.value if hasattr(p.status, "value") else str(p.status)
            key, default = _STATUS_LABELS.get(status_val, (status_val, status_val))
            status_label = tr(key, default)
            items.append({
                "id": p.id,
                "title": p.title,
                "status": status_val,
                "statusLabel": status_label,
                "shortDescription": p.short_description or "",
            })
        self._archived_projects = items
        self.archivedProjectsChanged.emit()

    def _on_project_changed(self, _id: int) -> None:
        self.loadArchivedProjects()

    def _on_error(self, message: str) -> None:
        self._is_loading = False
        if self._event_bus:
            self._event_bus.publish("toast.show", message=message, type_="error")

    # ── Properties ──────────────────────────────────────────────────────────

    @Property("QVariantList", notify=archivedProjectsChanged)
    def archivedProjects(self) -> list[dict[str, Any]]:
        return self._archived_projects

    @Property(int, notify=archivedProjectsChanged)
    def count(self) -> int:
        return len(self._archived_projects)

    @Property(bool, notify=archivedProjectsChanged)
    def isLoading(self) -> bool:
        return self._is_loading
