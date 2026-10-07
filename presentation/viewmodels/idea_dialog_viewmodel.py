"""QML fikir oluşturma/düzenleme diyaloğu ViewModel'i (IdeaDialogViewModel)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.di_container import DIContainer
from domain.models.idea import Idea
from presentation.viewmodels.idea_viewmodel import IdeaViewModel
from presentation.viewmodels.qt_properties import variant_map_property

logger = logging.getLogger(__name__)


def idea_form_data(idea: Idea | None) -> dict[str, Any]:
    """Diyalog formunun başlangıç değerleri; `None` boş (yeni fikir) form demektir."""
    if idea is None:
        return {
            "title": "", "problem": "", "solution": "", "target_user": "",
            "status": "RAW", "priority": "MEDIUM", "notes": "", "source_link": "",
        }
    return {
        "title": idea.title,
        "problem": idea.problem or "",
        "solution": idea.solution or "",
        "target_user": idea.target_user or "",
        "status": idea.status,
        "priority": idea.priority,
        "notes": idea.notes or "",
        "source_link": idea.source_link or "",
    }


class IdeaDialogViewModel(QObject):
    """Fikir diyaloğunun durumunu ve kaydetme akışını yönetir.

    Fikir önbelleği `IdeaViewModel`'de yaşar; bu sınıf yalnızca diyalog açıkken
    form verisini hazırlar ve kaydeder.
    """

    dialogStateChanged = Signal()

    def __init__(self, container: DIContainer, idea_viewmodel: IdeaViewModel, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._idea_vm = idea_viewmodel
        self._controller = container.idea_controller
        self._event_bus = container.event_bus

        self._is_open: bool = False
        self._mode: str = "create"  # "create" | "edit"
        self._idea_id: int = 0
        self._initial_data: dict[str, Any] = {}

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(bool, notify=dialogStateChanged)
    def isDialogOpen(self) -> bool:
        return self._is_open

    @Property(str, notify=dialogStateChanged)
    def dialogMode(self) -> str:
        return self._mode

    @Property(int, notify=dialogStateChanged)
    def dialogIdeaId(self) -> int:
        return self._idea_id

    @variant_map_property(notify=dialogStateChanged)
    def dialogInitialData(self) -> dict[str, Any]:
        return self._initial_data

    # ── Slots ───────────────────────────────────────────────────────────────

    @Slot()
    def openCreateDialog(self) -> None:
        self._mode = "create"
        self._idea_id = 0
        self._initial_data = idea_form_data(None)
        self._set_open(True)

    @Slot(int)
    def openEditDialog(self, idea_id: int) -> None:
        idea = self._idea_vm.cached_idea(idea_id)
        if idea is None:
            return
        self._mode = "edit"
        self._idea_id = idea_id
        self._initial_data = idea_form_data(idea)
        self._set_open(True)

    @Slot()
    def closeDialog(self) -> None:
        self._set_open(False)

    @Slot("QVariantMap")
    def saveIdea(self, data: dict[str, Any]) -> None:
        title = str(data.get("title", "")).strip()
        if not title:
            self._event_bus.publish("toast.show", message="Fikir başlığı boş olamaz", type_="danger")  # l10n: data
            return

        fields = {
            key: str(data.get(key, default))
            for key, default in (
                ("problem", ""), ("solution", ""), ("target_user", ""), ("status", "RAW"),
                ("priority", "MEDIUM"), ("notes", ""), ("source_link", ""),
            )
        }
        if self._mode == "edit" and self._idea_id != 0:
            self._controller.update_idea(self._idea_id, title=title, **fields)
            self._event_bus.publish("toast.show", message="Fikir güncellendi", type_="success")  # l10n: data
        else:
            self._controller.create_idea(title=title, **fields)
            self._event_bus.publish("toast.show", message="Fikir oluşturuldu", type_="success")  # l10n: data
        self.closeDialog()

    # ── Yardımcılar ─────────────────────────────────────────────────────────

    def _set_open(self, is_open: bool) -> None:
        self._is_open = is_open
        self.dialogStateChanged.emit()
