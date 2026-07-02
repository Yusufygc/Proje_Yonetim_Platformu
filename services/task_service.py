"""Task business rules, checklist handling, and WBS hierarchy updates."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from core.exceptions.task_exceptions import (
    TaskHierarchyError,
    TaskNotFoundError,
    TaskValidationError,
)
from domain.enums.task_status import TaskStatus
from domain.enums.task_type import TaskType
from domain.models.checklist_item import ChecklistItem
from domain.models.task import Task
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.task_repository import TaskRepository
from services.project_service import ProjectService

logger = logging.getLogger(__name__)


class TaskService:
    """Manage task CRUD, checklist updates, and hierarchical WBS side effects."""

    def __init__(
        self,
        repository: TaskRepository,
        project_service: ProjectService | None = None,
        activity_log_repository: ActivityLogRepository | None = None,
    ) -> None:
        self._repo = repository
        self._project_service = project_service
        self._activity_logs = activity_log_repository

    def get_all_tasks(self) -> list[Task]:
        return self._repo.get_all()

    def get_tasks(self, project_id: int) -> list[Task]:
        return self._repo.get_by_project(project_id)

    def get_task(self, task_id: int) -> Task:
        task = self._repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(self, project_id: int, title: str, **kwargs: object) -> Task:
        if not str(title).strip():
            raise TaskValidationError("Gorev basligi bos olamaz.")
        parent_task_id = kwargs.get("parent_task_id")
        if parent_task_id is not None:
            self._validate_parent(project_id, int(parent_task_id))
        if "order_index" not in kwargs:
            parent_id = int(parent_task_id) if parent_task_id is not None else None
            kwargs["order_index"] = self._repo.first_order_index(project_id, parent_id)
        task = Task(project_id=project_id, title=str(title).strip(), **kwargs)
        created = self._repo.create(task)
        self._log(project_id, "TASK_CREATED", f"{created.title} gorevi olusturuldu.", "task", created.id)
        self.recalculate_hierarchy(project_id)
        logger.info("Gorev olusturuldu: id=%d title='%s'", created.id, created.title)
        return created

    def update_task(self, task_id: int, **kwargs: object) -> Task:
        task = self.get_task(task_id)
        old_status = task.status
        if "parent_task_id" in kwargs and kwargs["parent_task_id"] is not None:
            self._validate_parent(task.project_id, int(kwargs["parent_task_id"]), task_id=task_id)
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        self._apply_status_side_effects(task, old_status)
        updated = self._repo.update(task)
        self._log(
            updated.project_id,
            "TASK_UPDATED",
            f"{updated.title} gorevi guncellendi.",
            "task",
            updated.id,
            {"previous_status": old_status, "new_status": updated.status},
        )
        self.recalculate_hierarchy(updated.project_id)
        logger.info("Gorev guncellendi: id=%d", task_id)
        return updated

    def toggle_status(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        old_status = task.status
        task.status = TaskStatus.TODO.value if task.status == TaskStatus.DONE.value else TaskStatus.DONE.value
        self._apply_status_side_effects(task, old_status=old_status)
        updated = self._repo.update(task)
        self._log(
            updated.project_id,
            "TASK_COMPLETED" if updated.status == TaskStatus.DONE.value else "TASK_REOPENED",
            f"{updated.title} gorevi durumu {updated.status} oldu.",
            "task",
            updated.id,
        )
        self.recalculate_hierarchy(updated.project_id)
        logger.info("Gorev durumu degistirildi: id=%d status=%s", task_id, task.status)
        return updated

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        project_id = task.project_id
        self._repo.delete(task_id)
        self.recalculate_hierarchy(project_id)
        logger.info("Gorev silindi: id=%d", task_id)

    def move_task(self, task_id: int, new_parent_task_id: int | None, new_order_index: int) -> Task:
        task = self.get_task(task_id)
        if new_parent_task_id is not None:
            self._validate_parent(task.project_id, new_parent_task_id, task_id=task_id)
        task.parent_task_id = new_parent_task_id
        task.order_index = max(0, int(new_order_index))
        updated = self._repo.update(task)
        self._log(
            updated.project_id,
            "TASK_MOVED",
            f"{updated.title} gorevi tasindi.",
            "task",
            updated.id,
            {"parent_task_id": new_parent_task_id, "order_index": updated.order_index},
        )
        self.recalculate_hierarchy(updated.project_id)
        return updated

    def get_descendant_count(self, task_id: int) -> int:
        task = self.get_task(task_id)
        children = self._children_by_parent(self._repo.get_by_project(task.project_id))
        return len(self._descendant_ids(task_id, children))

    def recalculate_hierarchy(self, project_id: int) -> None:
        tasks = self._repo.get_by_project(project_id)
        if not tasks:
            self._recalculate_project(project_id)
            return

        children = self._children_by_parent(tasks)
        by_id = {task.id: task for task in tasks}
        changed: list[Task] = []
        for task in sorted(tasks, key=lambda item: self._depth(item, by_id), reverse=True):
            child_tasks = children.get(task.id, [])
            if not child_tasks or task.status in {TaskStatus.BLOCKED.value, TaskStatus.CANCELLED.value}:
                continue
            old_status = task.status
            if all(child.status == TaskStatus.DONE.value for child in child_tasks):
                task.status = TaskStatus.DONE.value
            elif any(self._task_score(child, children) > 0 for child in child_tasks):
                task.status = TaskStatus.IN_PROGRESS.value
            else:
                task.status = TaskStatus.TODO.value
            self._apply_status_side_effects(task, old_status)
            if task.status != old_status:
                changed.append(task)

        if changed:
            self._repo.update_many(changed)
        self._recalculate_project(project_id)

    def add_checklist_item(self, task_id: int, text: str, order_index: int = 0) -> ChecklistItem:
        self.get_task(task_id)
        if not text.strip():
            raise TaskValidationError("Checklist ogesi metni bos olamaz.")
        item = ChecklistItem(task_id=task_id, text=text.strip(), order_index=order_index)
        created = self._repo.add_checklist_item(item)
        task = self.get_task(task_id)
        self._log(task.project_id, "CHECKLIST_ITEM_CREATED", f"{task.title} gorevine checklist maddesi eklendi.", "task", task.id)
        self.recalculate_hierarchy(task.project_id)
        return created

    def toggle_checklist_item(self, item_id: int) -> ChecklistItem:
        item = self._repo.get_checklist_item(item_id)
        if item is None:
            raise TaskValidationError(f"Checklist ogesi bulunamadi (id={item_id})")
        item.is_done = not item.is_done
        item.completed_at = datetime.now(timezone.utc) if item.is_done else None
        updated = self._repo.update_checklist_item(item)
        task = self._repo.get_task_for_checklist_item(item_id)
        if task:
            self._log(task.project_id, "CHECKLIST_ITEM_TOGGLED", f"{task.title} checklist maddesi guncellendi.", "task", task.id)
            self.recalculate_hierarchy(task.project_id)
        return updated

    def delete_checklist_item(self, item_id: int) -> None:
        task = self._repo.get_task_for_checklist_item(item_id)
        self._repo.delete_checklist_item(item_id)
        if task:
            self.recalculate_hierarchy(task.project_id)

    def _apply_status_side_effects(self, task: Task, old_status: str | None) -> None:
        if task.status == TaskStatus.DONE.value and old_status != TaskStatus.DONE.value:
            task.completed_at = datetime.now(timezone.utc)
            # Tamamlanan gorev kardes grubunun sonuna alinir (WBS listesinde en alta iner).
            task.order_index = self._repo.next_order_index(task.project_id, task.parent_task_id)
        elif task.status != TaskStatus.DONE.value:
            task.completed_at = None
        if task.status != TaskStatus.BLOCKED.value:
            task.blocked_reason = None

    def _validate_parent(self, project_id: int, parent_task_id: int, task_id: int | None = None) -> None:
        if task_id is not None and parent_task_id == task_id:
            raise TaskHierarchyError("Gorev kendi alt gorevi olamaz.")
        parent = self.get_task(parent_task_id)
        if parent.project_id != project_id:
            raise TaskHierarchyError("Alt gorev yalnizca ayni proje icindeki bir goreve baglanabilir.")
        if task_id is not None:
            children = self._children_by_parent(self._repo.get_by_project(project_id))
            if parent_task_id in self._descendant_ids(task_id, children):
                raise TaskHierarchyError("Gorev kendi alt soyuna tasinamaz.")

    def _children_by_parent(self, tasks: list[Task]) -> dict[int, list[Task]]:
        children: dict[int, list[Task]] = {}
        for task in tasks:
            if task.parent_task_id is not None:
                children.setdefault(task.parent_task_id, []).append(task)
        return children

    def _descendant_ids(self, task_id: int, children: dict[int, list[Task]]) -> set[int]:
        result: set[int] = set()
        for child in children.get(task_id, []):
            result.add(child.id)
            result.update(self._descendant_ids(child.id, children))
        return result

    def _depth(self, task: Task, by_id: dict[int, Task]) -> int:
        depth = 0
        current = task
        seen: set[int] = set()
        while current.parent_task_id is not None and current.parent_task_id in by_id:
            if current.id in seen:
                break
            seen.add(current.id)
            depth += 1
            current = by_id[current.parent_task_id]
        return depth

    def _task_score(self, task: Task, children: dict[int, list[Task]]) -> float:
        child_tasks = children.get(task.id, [])
        if child_tasks:
            scores = [self._task_score(child, children) for child in child_tasks]
            return sum(scores) / len(scores) if scores else 0.0
        if task.task_type == TaskType.GROUP.value:
            return 0.0
        if task.status == TaskStatus.DONE.value:
            return 1.0
        if task.checklist_items:
            done_items = len([item for item in task.checklist_items if item.is_done])
            return done_items / len(task.checklist_items)
        return 0.0

    def _log(
        self,
        project_id: int,
        action: str,
        summary: str,
        entity_type: str,
        entity_id: int | None = None,
        metadata: dict | None = None,
    ) -> None:
        if self._activity_logs is not None:
            try:
                self._activity_logs.create(project_id, action, summary, entity_type, entity_id, metadata)
            except Exception as exc:  # noqa: BLE001
                # FK ihlali (silinmiş proje) gibi loglama hataları asıl işlemi durdurmamalı
                logger.warning("Aktivite logu yazılamadı (project_id=%s): %s", project_id, exc)

    def _recalculate_project(self, project_id: int) -> None:
        if self._project_service is not None:
            self._project_service.recalculate_progress(project_id)
