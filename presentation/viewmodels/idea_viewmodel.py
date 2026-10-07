"""QML Fikir Havuzu Görünümü için ViewModel Köprüsü."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from domain.models.idea import Idea
from presentation.viewmodels.qt_properties import variant_map_property
from presentation.viewmodels.error_reporting import forward_errors_to_toast
from presentation.viewmodels.idea_list_model import IdeaListModel

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)


class IdeaViewModel(QObject):
    """Fikir Havuzu modülünün QML kullanıcı arayüzü ile iş katmanı arasındaki köprüsü."""

    selectedIdeaChanged = Signal()
    dialogStateChanged = Signal()
    statsChanged = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._controller = container.idea_controller
        self._event_bus = container.event_bus

        self._idea_model = IdeaListModel(parent=self)
        self._selected_idea_id: int = 0
        self._selected_idea_data: dict[str, Any] = {}

        # Dialog state
        self._is_dialog_open: bool = False
        self._dialog_mode: str = "create"  # "create" | "edit"
        self._dialog_idea_id: int = 0
        self._dialog_initial_data: dict[str, Any] = {}

        self._ideas_cache: list[Idea] = []
        self._connect_signals()
        self._subscribe_events()
        self.loadIdeas()

    def _connect_signals(self) -> None:
        forward_errors_to_toast(self._event_bus, self._controller)
        self._controller.ideas_loaded.connect(self._on_ideas_loaded)
        self._controller.idea_created.connect(self._on_idea_modified)
        self._controller.idea_updated.connect(self._on_idea_modified)
        self._controller.idea_deleted.connect(self._on_idea_deleted)
        self._controller.idea_converted.connect(self._on_idea_converted)

    def _subscribe_events(self) -> None:
        self._event_bus.subscribe("idea.created", self._on_bus_idea_changed)
        self._event_bus.subscribe("idea.updated", self._on_bus_idea_changed)
        self._event_bus.subscribe("idea.deleted", self._on_bus_idea_changed)
        self._event_bus.subscribe("idea.converted", self._on_bus_idea_changed)

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(QObject, constant=True)
    def ideaModel(self) -> IdeaListModel:
        return self._idea_model

    @Property(int, notify=selectedIdeaChanged)
    def selectedIdeaId(self) -> int:
        return self._selected_idea_id

    @variant_map_property(notify=selectedIdeaChanged)
    def selectedIdea(self) -> dict[str, Any]:
        return self._selected_idea_data

    @Property(bool, notify=dialogStateChanged)
    def isDialogOpen(self) -> bool:
        return self._is_dialog_open

    @Property(str, notify=dialogStateChanged)
    def dialogMode(self) -> str:
        return self._dialog_mode

    @Property(int, notify=dialogStateChanged)
    def dialogIdeaId(self) -> int:
        return self._dialog_idea_id

    @variant_map_property(notify=dialogStateChanged)
    def dialogInitialData(self) -> dict[str, Any]:
        return self._dialog_initial_data

    @Property(int, notify=statsChanged)
    def totalIdeas(self) -> int:
        return len(self._ideas_cache)

    # ── Controller & Event Callbacks ────────────────────────────────────────

    def _on_ideas_loaded(self, ideas: list[Idea]) -> None:
        self._ideas_cache = list(ideas)
        self._idea_model.set_ideas(ideas)
        self.statsChanged.emit()

        if self._selected_idea_id == 0 and ideas:
            self.selectIdea(ideas[0].id)
        else:
            self._refresh_selected_idea()

    def _on_idea_modified(self, idea: Any) -> None:
        self.loadIdeas()

    def _on_idea_deleted(self, idea_id: int) -> None:
        if self._selected_idea_id == idea_id:
            self._selected_idea_id = 0
            self._refresh_selected_idea()
        self.loadIdeas()

    def _on_idea_converted(self, idea_id: int, project_id: int) -> None:
        self.loadIdeas()
        self._event_bus.publish("toast.show", message="Fikir projeye dönüştürüldü", type_="success")  # l10n: data

    def _on_bus_idea_changed(self, **kwargs: Any) -> None:
        self.loadIdeas()

    # ── Public Slots ────────────────────────────────────────────────────────

    @Slot()
    def loadIdeas(self) -> None:
        self._controller.load_ideas(include_converted=True)

    @Slot(int)
    def selectIdea(self, idea_id: int) -> None:
        self._selected_idea_id = idea_id
        self._refresh_selected_idea()

    def _refresh_selected_idea(self) -> None:
        idea = next((x for x in self._ideas_cache if x.id == self._selected_idea_id), None)
        if not idea:
            self._selected_idea_data = {}
        else:
            self._selected_idea_data = {
                "id": idea.id,
                "title": idea.title,
                "problem": idea.problem or "",
                "solution": idea.solution or "",
                "targetUser": idea.target_user or "",
                "status": idea.status,
                "priority": idea.priority,
                "notes": idea.notes or "",
                "sourceLink": idea.source_link or "",
                "convertedProjectId": idea.converted_project_id or 0,
            }
        self.selectedIdeaChanged.emit()

    # ── Dialog Slots ────────────────────────────────────────────────────────

    @Slot()
    def openCreateDialog(self) -> None:
        self._dialog_mode = "create"
        self._dialog_idea_id = 0
        self._dialog_initial_data = {
            "title": "",
            "problem": "",
            "solution": "",
            "target_user": "",
            "status": "RAW",
            "priority": "MEDIUM",
            "notes": "",
            "source_link": "",
        }
        self._is_dialog_open = True
        self.dialogStateChanged.emit()

    @Slot(int)
    def openEditDialog(self, idea_id: int) -> None:
        idea = next((x for x in self._ideas_cache if x.id == idea_id), None)
        if not idea:
            return
        self._dialog_mode = "edit"
        self._dialog_idea_id = idea_id
        self._dialog_initial_data = {
            "title": idea.title,
            "problem": idea.problem or "",
            "solution": idea.solution or "",
            "target_user": idea.target_user or "",
            "status": idea.status,
            "priority": idea.priority,
            "notes": idea.notes or "",
            "source_link": idea.source_link or "",
        }
        self._is_dialog_open = True
        self.dialogStateChanged.emit()

    @Slot()
    def closeDialog(self) -> None:
        self._is_dialog_open = False
        self.dialogStateChanged.emit()

    @Slot("QVariantMap")
    def saveIdea(self, data: dict[str, Any]) -> None:
        title = str(data.get("title", "")).strip()
        if not title:
            self._event_bus.publish("toast.show", message="Fikir başlığı boş olamaz", type_="danger")  # l10n: data
            return

        kwargs = {
            "problem": str(data.get("problem", "")),
            "solution": str(data.get("solution", "")),
            "target_user": str(data.get("target_user", "")),
            "status": str(data.get("status", "RAW")),
            "priority": str(data.get("priority", "MEDIUM")),
            "notes": str(data.get("notes", "")),
            "source_link": str(data.get("source_link", "")),
        }

        if self._dialog_mode == "edit" and self._dialog_idea_id != 0:
            self._controller.update_idea(self._dialog_idea_id, title=title, **kwargs)
            self._event_bus.publish("toast.show", message="Fikir güncellendi", type_="success")  # l10n: data
        else:
            self._controller.create_idea(title=title, **kwargs)
            self._event_bus.publish("toast.show", message="Fikir oluşturuldu", type_="success")  # l10n: data

        self.closeDialog()
        self.loadIdeas()

    @Slot(int)
    def deleteIdea(self, idea_id: int) -> None:
        self._controller.delete_idea(idea_id)
        self._event_bus.publish("toast.show", message="Fikir silindi", type_="info")  # l10n: data
        self.loadIdeas()

    @Slot(int)
    def convertToProject(self, idea_id: int) -> None:
        self._controller.convert_to_project(idea_id)

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._idea_model.setSearchQuery(query)

    @Slot(str)
    def setStatusFilter(self, status: str) -> None:
        self._idea_model.setStatusFilter(status)
