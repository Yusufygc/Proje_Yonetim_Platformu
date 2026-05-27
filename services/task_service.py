"""
Görev iş kuralları.
Görev oluşturma, durum değiştirme ve checklist yönetimi burada yönetilir.
"""
from __future__ import annotations

import logging

from core.exceptions.task_exceptions import TaskNotFoundError, TaskValidationError
from domain.enums.task_status import TaskStatus
from domain.models.checklist_item import ChecklistItem
from domain.models.task import Task
from infrastructure.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


class TaskService:
    """Görev oluşturma, güncelleme, silme ve checklist iş kurallarını yönetir."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repo = repository

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
            raise TaskValidationError("Görev başlığı boş olamaz.")
        task = Task(project_id=project_id, title=str(title).strip(), **kwargs)
        created = self._repo.create(task)
        logger.info("Görev oluşturuldu: id=%d title='%s'", created.id, created.title)
        return created

    def update_task(self, task_id: int, **kwargs: object) -> Task:
        task = self.get_task(task_id)
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        updated = self._repo.update(task)
        logger.info("Görev güncellendi: id=%d", task_id)
        return updated

    def toggle_status(self, task_id: int) -> Task:
        """Görev DONE ise TODO'ya, değilse DONE'a geçirir."""
        task = self.get_task(task_id)
        new_status = (
            TaskStatus.TODO.value
            if task.status == TaskStatus.DONE.value
            else TaskStatus.DONE.value
        )
        task.status = new_status
        updated = self._repo.update(task)
        logger.info("Görev durumu değiştirildi: id=%d status=%s", task_id, new_status)
        return updated

    def delete_task(self, task_id: int) -> None:
        self.get_task(task_id)
        self._repo.delete(task_id)
        logger.info("Görev silindi: id=%d", task_id)

    def add_checklist_item(self, task_id: int, text: str, order_index: int = 0) -> ChecklistItem:
        self.get_task(task_id)
        if not text.strip():
            raise TaskValidationError("Checklist öğesi metni boş olamaz.")
        item = ChecklistItem(task_id=task_id, text=text.strip(), order_index=order_index)
        return self._repo.add_checklist_item(item)

    def toggle_checklist_item(self, item_id: int) -> ChecklistItem:
        item = self._repo.get_checklist_item(item_id)
        if item is None:
            raise TaskValidationError(f"Checklist öğesi bulunamadı (id={item_id})")
        item.is_done = not item.is_done
        return self._repo.update_checklist_item(item)

    def delete_checklist_item(self, item_id: int) -> None:
        self._repo.delete_checklist_item(item_id)
