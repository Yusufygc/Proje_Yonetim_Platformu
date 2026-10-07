"""QML Görevler (WBS) Görünümü için ViewModel Köprüsü."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication

from domain.models.task import Task
from presentation.viewmodels.qt_properties import variant_list_property, variant_map_property
from presentation.viewmodels.error_reporting import forward_errors_to_toast
from presentation.viewmodels.task_list_model import TaskListModel

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)

# Diyalogdaki "Otomatik" durum seçeneği; alt görevi olan görevler için kullanılır.
_AUTO_STATUS = "AUTO"


class TaskViewModel(QObject):
    """Görevler (WBS) modülünün QML kullanıcı arayüzü ile iş katmanı arasındaki köprüsü."""

    selectedProjectChanged = Signal(int)
    selectedTaskChanged = Signal()
    projectsChanged = Signal()
    dialogStateChanged = Signal()
    statsChanged = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._task_controller = container.task_controller
        self._project_controller = container.project_controller
        self._event_bus = container.event_bus

        self._task_model = TaskListModel(parent=self)
        self._projects: list[dict[str, Any]] = []
        self._selected_project_id: int = 0
        self._selected_task_id: int = 0
        self._selected_task_data: dict[str, Any] = {}

        # Dialog durumu
        self._is_dialog_open: bool = False
        self._dialog_mode: str = "create"  # "create" | "create_subtask" | "edit"
        self._dialog_task_id: int = 0
        self._dialog_parent_task_id: int = 0
        self._dialog_initial_data: dict[str, Any] = {}

        self._tasks_cache: list[Task] = []
        self._connect_signals()
        self._subscribe_events()
        self.loadProjects()

    def _connect_signals(self) -> None:
        forward_errors_to_toast(self._event_bus, self._task_controller)
        self._task_controller.tasks_loaded.connect(self._on_tasks_loaded)
        self._task_controller.task_created.connect(self._on_task_modified)
        self._task_controller.task_updated.connect(self._on_task_modified)
        self._task_controller.task_deleted.connect(self._on_task_deleted)
        self._project_controller.projects_loaded.connect(self._on_projects_loaded)

    def _subscribe_events(self) -> None:
        self._event_bus.subscribe("task.created", self._on_bus_task_changed)
        self._event_bus.subscribe("task.updated", self._on_bus_task_changed)
        self._event_bus.subscribe("task.deleted", self._on_bus_task_changed)
        self._event_bus.subscribe("project.created", self._on_bus_project_changed)
        self._event_bus.subscribe("project.deleted", self._on_bus_project_changed)

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(QObject, constant=True)
    def taskModel(self) -> TaskListModel:
        return self._task_model

    @variant_list_property(notify=projectsChanged)
    def projects(self) -> list[dict[str, Any]]:
        return self._projects

    @Property(int, notify=selectedProjectChanged)
    def selectedProjectId(self) -> int:
        return self._selected_project_id

    @Property(int, notify=selectedTaskChanged)
    def selectedTaskId(self) -> int:
        return self._selected_task_id

    @variant_map_property(notify=selectedTaskChanged)
    def selectedTask(self) -> dict[str, Any]:
        return self._selected_task_data

    @Property(bool, notify=dialogStateChanged)
    def isDialogOpen(self) -> bool:
        return self._is_dialog_open

    @Property(str, notify=dialogStateChanged)
    def dialogMode(self) -> str:
        return self._dialog_mode

    @Property(int, notify=dialogStateChanged)
    def dialogTaskId(self) -> int:
        return self._dialog_task_id

    @Property(int, notify=dialogStateChanged)
    def dialogParentTaskId(self) -> int:
        return self._dialog_parent_task_id

    @variant_map_property(notify=dialogStateChanged)
    def dialogInitialData(self) -> dict[str, Any]:
        return self._dialog_initial_data

    @Property(int, notify=statsChanged)
    def totalTasks(self) -> int:
        return len(self._tasks_cache)

    @Property(int, notify=statsChanged)
    def completedTasks(self) -> int:
        return sum(1 for t in self._tasks_cache if t.status == "DONE")

    @Property(int, notify=statsChanged)
    def inProgressTasks(self) -> int:
        return sum(1 for t in self._tasks_cache if t.status == "IN_PROGRESS")

    @Property(int, notify=statsChanged)
    def blockedTasks(self) -> int:
        return sum(1 for t in self._tasks_cache if t.status == "BLOCKED")

    # ── Controller & Event Callbacks ────────────────────────────────────────

    def _on_projects_loaded(self, projects: list[Any]) -> None:
        self._projects = [{"id": p.id, "title": p.title} for p in projects]
        self.projectsChanged.emit()

        if self._projects and self._selected_project_id == 0:
            self.selectProject(self._projects[0]["id"])
        elif not self._projects:
            self._selected_project_id = 0
            self.selectedProjectChanged.emit(0)
            self._tasks_cache = []
            self._task_model.set_tasks([])
            self.statsChanged.emit()

    def _on_tasks_loaded(self, project_id: int, tasks: list[Task]) -> None:
        if project_id != self._selected_project_id:
            return
        self._tasks_cache = list(tasks)
        self._task_model.set_tasks(tasks)
        self.statsChanged.emit()
        self._refresh_selected_task()

    def _on_task_modified(self, task: Any) -> None:
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_task_deleted(self, task_id: int) -> None:
        if self._selected_task_id == task_id:
            self._selected_task_id = 0
            self._refresh_selected_task()
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_bus_task_changed(self, **kwargs: Any) -> None:
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_bus_project_changed(self, **kwargs: Any) -> None:
        self.loadProjects()

    # ── Public Slots ────────────────────────────────────────────────────────

    @Slot()
    def loadProjects(self) -> None:
        self._project_controller.load_projects()

    @Slot(int)
    def selectProject(self, project_id: int) -> None:
        if self._selected_project_id == project_id:
            return
        self._selected_project_id = project_id
        self._task_model.clear_overrides()
        self.selectedProjectChanged.emit(project_id)
        if project_id != 0:
            self._task_controller.load_tasks(project_id)

    @Slot(int)
    def selectTask(self, task_id: int) -> None:
        self._selected_task_id = task_id
        self._refresh_selected_task()

    def _refresh_selected_task(self) -> None:
        t = next((x for x in self._tasks_cache if x.id == self._selected_task_id), None)
        if not t:
            self._selected_task_data = {}
        else:
            chk_list = [
                {"id": c.id, "text": c.text, "isDone": c.is_done}
                for c in (t.checklist_items or [])
            ]
            self._selected_task_data = {
                "id": t.id,
                "projectId": t.project_id,
                "parentId": t.parent_task_id or 0,
                "title": t.title,
                "description": t.description or "",
                "status": t.status,
                "priority": t.priority,
                "taskType": t.task_type,
                "dueDate": t.due_date.isoformat() if t.due_date else "",
                "checklist": chk_list,
            }
        self.selectedTaskChanged.emit()

    @Slot(int)
    def toggleTaskStatus(self, task_id: int) -> None:
        self._task_controller.toggle_status(task_id)

    @Slot(int, int)
    def toggleChecklistItem(self, item_id: int, task_id: int) -> None:
        self._task_controller.toggle_checklist_item(item_id, task_id)

    @Slot(int, str)
    def addChecklistItem(self, task_id: int, text: str) -> None:
        if text.strip():
            self._task_controller.add_checklist_item(task_id, text.strip())

    @Slot(int, int)
    def deleteChecklistItem(self, item_id: int, task_id: int) -> None:
        self._task_controller.delete_checklist_item(item_id, task_id)

    @Slot(str)
    def quickAddTask(self, title: str) -> None:
        t = title.strip()
        if not t or self._selected_project_id == 0:
            return
        parent_id = self._selected_task_id if self._selected_task_id != 0 else None
        self._task_controller.create_task(
            self._selected_project_id,
            t,
            parent_task_id=parent_id,
        )

    # ── Dialog Slots ────────────────────────────────────────────────────────

    @Slot(int)
    def openCreateDialog(self, parent_task_id: int = 0) -> None:
        self._dialog_mode = "create_subtask" if parent_task_id != 0 else "create"
        self._dialog_task_id = 0
        self._dialog_parent_task_id = parent_task_id
        self._dialog_initial_data = {
            "title": "",
            "description": "",
            "status": "TODO",
            "priority": "MEDIUM",
            "task_type": "TASK",
            "blocked_reason": "",
            "checklist": [],
        }
        self._is_dialog_open = True
        self.dialogStateChanged.emit()

    @Slot(int)
    def openEditDialog(self, task_id: int) -> None:
        t = next((x for x in self._tasks_cache if x.id == task_id), None)
        if not t:
            return
        self._dialog_mode = "edit"
        self._dialog_task_id = task_id
        self._dialog_parent_task_id = t.parent_task_id or 0
        chk_list = [
            {"id": c.id, "text": c.text, "isDone": c.is_done}
            for c in (t.checklist_items or [])
        ]
        self._dialog_initial_data = {
            "title": t.title,
            "description": t.description or "",
            "status": t.status,
            "priority": t.priority,
            "task_type": t.task_type,
            "blocked_reason": t.blocked_reason or "",
            "has_children": any(x.parent_task_id == task_id for x in self._tasks_cache),
            "checklist": chk_list,
        }
        self._is_dialog_open = True
        self.dialogStateChanged.emit()

    @Slot()
    def closeDialog(self) -> None:
        self._is_dialog_open = False
        self.dialogStateChanged.emit()

    @Slot("QVariantMap")
    def saveTask(self, data: dict[str, Any]) -> None:
        title = str(data.get("title", "")).strip()
        if not title:
            self._event_bus.publish("toast.show", message="Görev başlığı boş olamaz", type_="danger")  # l10n: data
            return

        kwargs = self._build_task_fields(data)
        if kwargs["status"] == _AUTO_STATUS:
            self._resolve_auto_status(kwargs)

        if self._dialog_mode == "edit" and self._dialog_task_id != 0:
            self._task_controller.update_task(self._dialog_task_id, title=title, **kwargs)
            self._event_bus.publish("toast.show", message="Görev güncellendi", type_="success")  # l10n: data
        else:
            parent_id = self._dialog_parent_task_id if self._dialog_parent_task_id != 0 else None
            created = self._task_controller.create_task(
                self._selected_project_id,
                title,
                parent_task_id=parent_id,
                **kwargs,
            )
            if created is None:
                # Hata toast'ı controller sinyalinden geldi; diyalog açık kalsın ki girilen veri kaybolmasın.
                return
            for item_text in data.get("checklist_items", []):
                if str(item_text).strip():
                    self._task_controller.add_checklist_item(created.id, str(item_text).strip())
            self._event_bus.publish("toast.show", message="Görev oluşturuldu", type_="success")  # l10n: data

        self.closeDialog()

    def _resolve_auto_status(self, kwargs: dict[str, Any]) -> None:
        """"Otomatik" seçimi: durum alt görevlerden türetilir, engelli/iptal ise önce kilit açılır."""
        task = next((x for x in self._tasks_cache if x.id == self._dialog_task_id), None)
        if task is not None and task.status in ("BLOCKED", "CANCELLED"):
            kwargs["status"] = "TODO"
            return
        kwargs.pop("status")

    def _build_task_fields(self, data: dict[str, Any]) -> dict[str, Any]:
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

    @Slot(int)
    def deleteTask(self, task_id: int) -> None:
        self._task_controller.delete_task(task_id)
        self._event_bus.publish("toast.show", message="Görev silindi", type_="info")  # l10n: data

    @Slot(int, int, int)
    def moveTask(self, task_id: int, new_parent_id: int, new_order_index: int) -> None:
        pid = new_parent_id if new_parent_id != 0 else None
        self._task_controller.move_task(task_id, pid, new_order_index)

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._task_model.setSearchQuery(query)

    @Slot(str)
    def setStatusFilter(self, status: str) -> None:
        self._task_model.setStatusFilter(status)

    @Slot(str)
    def setPriorityFilter(self, priority: str) -> None:
        self._task_model.setPriorityFilter(priority)

    @Slot(str)
    def setTypeFilter(self, task_type: str) -> None:
        self._task_model.setTypeFilter(task_type)

    # ── Kopyalama ve Çoğaltma İşlemleri ────────────────────────────────────

    @Slot(int)
    def copyTaskToClipboard(self, task_id: int) -> None:
        """Belirtilen görevi ve alt görevlerini metin (WBS) formatında panoya kopyalar."""
        t = next((x for x in self._tasks_cache if x.id == task_id), None)
        if not t:
            return

        lines = self._collect_task_copy_lines(task_id)
        if lines:
            text = "\n".join(lines)
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(text)
            self._event_bus.publish(
                "toast.show",
                message="Görev panoya kopyalandı",  # l10n: data
                type_="success",
            )

    def _collect_task_copy_lines(self, root_task_id: int) -> list[str]:
        """Görevi ve alt görevlerini derinliğe göre girintili toplar."""
        lines: list[str] = []
        tasks_by_parent: dict[int | None, list[Task]] = {}
        by_id: dict[int, Task] = {}
        for item in self._tasks_cache:
            by_id[item.id] = item
            tasks_by_parent.setdefault(item.parent_task_id, []).append(item)

        root_task = by_id.get(root_task_id)
        if not root_task:
            return lines

        stack: list[tuple[Task, int]] = [(root_task, 0)]
        while stack:
            cur, depth = stack.pop()
            indent = "  " * depth
            lines.append(f"{indent}[{cur.status}] {cur.title}")
            for c in (cur.checklist_items or []):
                chk_mark = "[x]" if c.is_done else "[ ]"
                lines.append(f"{indent}  {chk_mark} {c.text}")
            children = tasks_by_parent.get(cur.id, [])
            for child in reversed(children):
                stack.append((child, depth + 1))

        return lines

    @Slot(int)
    def duplicateTask(self, task_id: int) -> None:
        """Görevi aynı proje ve üst görev altına yeni bir kopya olarak çoğaltır."""
        t = next((x for x in self._tasks_cache if x.id == task_id), None)
        if not t:
            return

        new_title = f"{t.title} (Kopya)"  # l10n: data
        created = self._task_controller.create_task(
            t.project_id,
            new_title,
            parent_task_id=t.parent_task_id,
            description=t.description or "",
            status="TODO",
            priority=t.priority,
            task_type=t.task_type,
        )
        if created and t.checklist_items:
            for item in t.checklist_items:
                if item.text.strip():
                    self._task_controller.add_checklist_item(created.id, item.text.strip())

        self._event_bus.publish(
            "toast.show",
            message="Görev çoğaltıldı",  # l10n: data
            type_="success",
        )

