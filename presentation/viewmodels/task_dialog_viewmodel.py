"""QML görev oluşturma/düzenleme diyaloğu ViewModel'i (TaskDialogViewModel)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.di_container import DIContainer
from domain.models.task import Task
from presentation.viewmodels.qt_properties import variant_map_property
from presentation.viewmodels.task_viewmodel import TaskViewModel

logger = logging.getLogger(__name__)

# Diyalogdaki "Otomatik" durum seçeneği; alt görevi olan görevler için kullanılır.
_AUTO_STATUS = "AUTO"
_MANUAL_PARENT_STATUSES = ("BLOCKED", "CANCELLED", "DONE")


def checklist_payload(task: Task) -> list[dict[str, Any]]:
    return [{"id": c.id, "text": c.text, "isDone": c.is_done} for c in (task.checklist_items or [])]


class TaskDialogViewModel(QObject):
    """Görev diyaloğunun durumunu ve kaydetme akışını yönetir.

    Seçili proje ve görev önbelleği `TaskViewModel`'de yaşar; bu sınıf yalnızca diyalog
    açıkken form verisini hazırlar ve kaydeder.
    """

    dialogStateChanged = Signal()

    def __init__(self, container: DIContainer, task_viewmodel: TaskViewModel, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._task_vm = task_viewmodel
        self._task_controller = container.task_controller
        self._event_bus = container.event_bus

        self._is_open: bool = False
        self._mode: str = "create"  # "create" | "create_subtask" | "edit"
        self._task_id: int = 0
        self._parent_task_id: int = 0
        self._initial_data: dict[str, Any] = {}

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(bool, notify=dialogStateChanged)
    def isDialogOpen(self) -> bool:
        return self._is_open

    @Property(str, notify=dialogStateChanged)
    def dialogMode(self) -> str:
        return self._mode

    @Property(int, notify=dialogStateChanged)
    def dialogTaskId(self) -> int:
        return self._task_id

    @variant_map_property(notify=dialogStateChanged)
    def dialogInitialData(self) -> dict[str, Any]:
        return self._initial_data

    # ── Slots ───────────────────────────────────────────────────────────────

    @Slot(int)
    def openCreateDialog(self, parent_task_id: int = 0) -> None:
        self._mode = "create_subtask" if parent_task_id != 0 else "create"
        self._task_id = 0
        self._parent_task_id = parent_task_id
        self._initial_data = {
            "title": "",
            "description": "",
            "status": "TODO",
            "priority": "MEDIUM",
            "task_type": "TASK",
            "blocked_reason": "",
            "checklist": [],
        }
        self._set_open(True)

    @Slot(int)
    def openEditDialog(self, task_id: int) -> None:
        task = self._task_controller.get_task_sync(task_id) or self._cached_task(task_id)
        if task is None:
            return
        self._mode = "edit"
        self._task_id = task_id
        self._parent_task_id = task.parent_task_id or 0
        self._initial_data = {
            "title": task.title,
            "description": task.description or "",
            "status": task.status,
            "priority": task.priority,
            "task_type": task.task_type,
            "blocked_reason": task.blocked_reason or "",
            "has_children": any(x.parent_task_id == task_id for x in self._task_vm.cached_tasks()),
            "checklist": checklist_payload(task),
        }
        self._set_open(True)

    @Slot()
    def closeDialog(self) -> None:
        self._set_open(False)

    @Slot("QVariantMap")
    def saveTask(self, data: dict[str, Any]) -> None:
        title = str(data.get("title", "")).strip()
        if not title:
            self._event_bus.publish("toast.show", message="Görev başlığı boş olamaz", type_="danger")  # l10n: data
            return

        fields = self._build_task_fields(data)
        if fields["status"] == _AUTO_STATUS:
            self._resolve_auto_status(fields)

        has_checklist = "checklist_items" in data
        checklist_items = data.get("checklist_items", [])
        if hasattr(checklist_items, "toVariant"):
            checklist_items = checklist_items.toVariant()

        if self._mode == "edit" and self._task_id != 0:
            self._update_existing(title, fields, list(checklist_items) if has_checklist else None)
        elif not self._create_new(title, fields, list(checklist_items or [])):
            return
        self.closeDialog()

    # ── Yardımcılar ─────────────────────────────────────────────────────────

    def _set_open(self, is_open: bool) -> None:
        self._is_open = is_open
        self.dialogStateChanged.emit()

    def _cached_task(self, task_id: int) -> Task | None:
        return next((x for x in self._task_vm.cached_tasks() if x.id == task_id), None)

    def _update_existing(
        self,
        title: str,
        fields: dict[str, Any],
        checklist_items: list[Any] | None = None,
    ) -> None:
        self._task_controller.update_task(self._task_id, title=title, **fields)
        if checklist_items is not None:
            self._sync_checklist_items(self._task_id, checklist_items)
        self._event_bus.publish("toast.show", message="Görev güncellendi", type_="success")  # l10n: data

    def _create_new(self, title: str, fields: dict[str, Any], checklist_items: list[Any]) -> bool:
        """Görevi ve checklist maddelerini oluşturur; başarısızsa False döner (diyalog açık kalır)."""
        parent_id = self._parent_task_id if self._parent_task_id != 0 else None
        created = self._task_controller.create_task(
            self._task_vm.current_project_id(), title, parent_task_id=parent_id, **fields
        )
        if created is None:
            # Hata toast'ı controller sinyalinden geldi; girilen veri kaybolmasın diye diyalog açık kalır.
            return False
        for entry in checklist_items:
            text, is_done = self._parse_checklist_entry(entry)
            if text:
                item = self._task_controller.add_checklist_item(created.id, text)
                if item is not None and is_done:
                    self._task_controller.toggle_checklist_item(item.id, created.id)
        self._event_bus.publish("toast.show", message="Görev oluşturuldu", type_="success")  # l10n: data
        return True

    def _sync_checklist_items(self, task_id: int, raw_items: list[Any]) -> None:
        """Düzenleme sırasında eklenen, silinen veya durumu değişen checklist maddelerini eşitler."""
        task = self._task_controller.get_task_sync(task_id) or self._cached_task(task_id)
        existing = list(task.checklist_items or []) if task is not None else []
        existing_by_id = {c.id: c for c in existing}
        kept_ids: set[int] = set()

        for entry in raw_items:
            raw = entry.toVariant() if hasattr(entry, "toVariant") else entry
            if isinstance(raw, dict):
                self._apply_dict_checklist_entry(task_id, raw, existing_by_id, kept_ids)
                continue
            text = str(raw).strip()
            if not text:
                continue
            match = next((c for c in existing if c.text == text and c.id not in kept_ids), None)
            if match is not None:
                kept_ids.add(match.id)
            else:
                self._task_controller.add_checklist_item(task_id, text)

        for item in existing:
            if item.id not in kept_ids:
                self._task_controller.delete_checklist_item(item.id, task_id)

    def _apply_dict_checklist_entry(
        self,
        task_id: int,
        entry: dict[str, Any],
        existing_by_id: dict[int, Any],
        kept_ids: set[int],
    ) -> None:
        item_id = int(entry.get("id") or 0)
        text = str(entry.get("text", "")).strip()
        is_done = bool(entry.get("isDone", False))
        if item_id > 0 and item_id in existing_by_id:
            kept_ids.add(item_id)
            if bool(existing_by_id[item_id].is_done) != is_done:
                self._task_controller.toggle_checklist_item(item_id, task_id)
        elif text:
            created = self._task_controller.add_checklist_item(task_id, text)
            if created is not None and is_done:
                self._task_controller.toggle_checklist_item(created.id, task_id)

    @staticmethod
    def _parse_checklist_entry(entry: Any) -> tuple[str, bool]:
        raw = entry.toVariant() if hasattr(entry, "toVariant") else entry
        if isinstance(raw, dict):
            return str(raw.get("text", "")).strip(), bool(raw.get("isDone", False))
        return str(raw).strip(), False

    def _resolve_auto_status(self, fields: dict[str, Any]) -> None:
        """Otomatik seçimi: durum alt görevlerden türetilir, engelli/iptal ise önce kilit açılır."""
        task = self._cached_task(self._task_id)
        if task is not None and task.status in _MANUAL_PARENT_STATUSES:
            fields["status"] = "TODO"
            return
        fields.pop("status")

    @staticmethod
    def _build_task_fields(data: dict[str, Any]) -> dict[str, Any]:
        """Form verisini servis alanlarına çevirir."""
        status = str(data.get("status", "TODO"))
        blocked_reason = str(data.get("blocked_reason", "")).strip()
        return {
            "description": str(data.get("description", "")),
            "status": status,
            "priority": str(data.get("priority", "MEDIUM")),
            "task_type": str(data.get("task_type", "TASK")),
            # Engel nedeni yalnızca "Engellendi" durumunda anlamlı; durum değişince eski neden kalmasın.
            "blocked_reason": blocked_reason if status == "BLOCKED" and blocked_reason else None,
        }
