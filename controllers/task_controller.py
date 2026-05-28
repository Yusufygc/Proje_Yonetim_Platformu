"""
Görev ekranı için PySide6 sinyal/slot köprüsü.
Görev CRUD ve durum değiştirme işlemlerini sinyal tabanlı olarak yönetir.
"""
from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal

from core.events.event_bus import EventBus
from core.exceptions.base_exception import AppBaseException
from core.workers.worker import Worker
from domain.dtos.forms import TaskCreateDTO, TaskUpdateDTO
from domain.models.task import Task
from services.task_service import TaskService

logger = logging.getLogger(__name__)


class TaskController(QObject):
    """Görev işlemlerini sinyal tabanlı olarak yönetir."""

    tasks_loaded = Signal(list)
    all_tasks_loaded = Signal(list)
    task_created = Signal(object)
    task_updated = Signal(object)
    task_deleted = Signal(int)
    error_occurred = Signal(str)

    def __init__(
        self,
        service: TaskService,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._service = service

    def load_tasks(self, project_id: int) -> None:
        def _fetch() -> list[Task]:
            return self._service.get_tasks(project_id)
            
        def _on_error(err: str) -> None:
            logger.error("Görevler yüklenemedi: %s", err)
            self.error_occurred.emit(str(err))
            
        worker = Worker(_fetch)
        worker.signals.result.connect(self.tasks_loaded.emit)
        worker.signals.error.connect(_on_error)
        worker.start()

    def load_all_tasks(self) -> None:
        def _fetch() -> list[Task]:
            return self._service.get_all_tasks()
            
        def _on_error(err: str) -> None:
            logger.error("Tüm görevler yüklenemedi: %s", err)
            self.error_occurred.emit(str(err))
            
        worker = Worker(_fetch)
        worker.signals.result.connect(self.all_tasks_loaded.emit)
        worker.signals.error.connect(_on_error)
        worker.start()

    def create_task(self, project_id: int, title: str, **kwargs: object) -> None:
        try:
            dto = TaskCreateDTO(project_id=project_id, title=title, values=dict(kwargs))
            task = self._service.create_task(dto.project_id, dto.title, **dto.values)
            self.task_created.emit(task)
            EventBus.instance().publish("task.created", task_id=task.id, project_id=task.project_id, task=task)
        except (AppBaseException, ValueError) as exc:
            logger.error("Görev oluşturulamadı: %s", exc)
            self.error_occurred.emit(str(exc))

    def update_task(self, task_id: int, **kwargs: object) -> None:
        try:
            dto = TaskUpdateDTO(values=dict(kwargs))
            task = self._service.update_task(task_id, **dto.values)
            self.task_updated.emit(task)
            event_name = "task.completed" if task.status == "DONE" else "task.updated"
            EventBus.instance().publish(event_name, task_id=task.id, project_id=task.project_id, task=task)
        except (AppBaseException, ValueError) as exc:
            logger.error("Görev güncellenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def toggle_status(self, task_id: int) -> None:
        try:
            task = self._service.toggle_status(task_id)
            self.task_updated.emit(task)
            event_name = "task.completed" if task.status == "DONE" else "task.reopened"
            EventBus.instance().publish(event_name, task_id=task.id, project_id=task.project_id, task=task)
        except AppBaseException as exc:
            logger.error("Görev durumu değiştirilemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def delete_task(self, task_id: int) -> None:
        try:
            self._service.delete_task(task_id)
            self.task_deleted.emit(task_id)
            EventBus.instance().publish("task.deleted", task_id=task_id)
        except AppBaseException as exc:
            logger.error("Görev silinemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def add_checklist_item(self, task_id: int, text: str) -> None:
        try:
            self._service.add_checklist_item(task_id, text)
            self.task_updated.emit(self.get_task_sync(task_id))
        except AppBaseException as exc:
            logger.error("Checklist öğesi eklenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def move_task(self, task_id: int, new_parent_task_id: int | None, new_order_index: int) -> None:
        try:
            task = self._service.move_task(task_id, new_parent_task_id, new_order_index)
            self.task_updated.emit(task)
            EventBus.instance().publish("task.moved", task_id=task.id, project_id=task.project_id, task=task)
        except AppBaseException as exc:
            logger.error("Görev taşınamadı: %s", exc)
            self.error_occurred.emit(str(exc))

    def get_descendant_count(self, task_id: int) -> int:
        try:
            return self._service.get_descendant_count(task_id)
        except AppBaseException as exc:
            logger.error("Alt görev sayısı alınamadı: %s", exc)
            self.error_occurred.emit(str(exc))
            return 0

    def recalculate_hierarchy(self, project_id: int) -> None:
        try:
            self._service.recalculate_hierarchy(project_id)
        except AppBaseException as exc:
            logger.error("Görev hiyerarşisi güncellenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def toggle_checklist_item(self, item_id: int, task_id: int) -> None:
        try:
            self._service.toggle_checklist_item(item_id)
            self.task_updated.emit(self.get_task_sync(task_id))
        except AppBaseException as exc:
            logger.error("Checklist öğesi değiştirilemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def delete_checklist_item(self, item_id: int, task_id: int) -> None:
        try:
            self._service.delete_checklist_item(item_id)
            self.task_updated.emit(self.get_task_sync(task_id))
        except AppBaseException as exc:
            logger.error("Checklist öğesi silinemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def get_task_sync(self, task_id: int) -> Optional[Task]:
        try:
            return self._service.get_task(task_id)
        except AppBaseException:
            return None
