"""Görev ve checklist öğesi veri erişim katmanı."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from domain.models.checklist_item import ChecklistItem
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager


class TaskRepository:
    """Task ve ChecklistItem kayıtları üzerinde CRUD işlemlerini yönetir."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_all(self) -> list[Task]:
        with self._db.session() as sess:
            stmt = select(Task).order_by(Task.project_id, Task.order_index, Task.id)
            return list(sess.scalars(stmt).all())

    def get_by_project(self, project_id: int) -> list[Task]:
        with self._db.session() as sess:
            stmt = (
                select(Task)
                .where(Task.project_id == project_id)
                .order_by(Task.order_index, Task.id)
            )
            return list(sess.scalars(stmt).all())

    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self._db.session() as sess:
            return sess.get(Task, task_id)

    def create(self, task: Task) -> Task:
        with self._db.session() as sess:
            sess.add(task)
            sess.flush()
            sess.refresh(task)
            sess.expunge(task)
            return task

    def update(self, task: Task) -> Task:
        with self._db.session() as sess:
            merged = sess.merge(task)
            sess.flush()
            sess.refresh(merged)
            sess.expunge(merged)
            return merged

    def delete(self, task_id: int) -> None:
        with self._db.session() as sess:
            task = sess.get(Task, task_id)
            if task:
                sess.delete(task)

    def add_checklist_item(self, item: ChecklistItem) -> ChecklistItem:
        with self._db.session() as sess:
            sess.add(item)
            sess.flush()
            sess.refresh(item)
            sess.expunge(item)
            return item

    def get_checklist_item(self, item_id: int) -> Optional[ChecklistItem]:
        with self._db.session() as sess:
            return sess.get(ChecklistItem, item_id)

    def update_checklist_item(self, item: ChecklistItem) -> ChecklistItem:
        with self._db.session() as sess:
            merged = sess.merge(item)
            sess.flush()
            sess.refresh(merged)
            sess.expunge(merged)
            return merged

    def delete_checklist_item(self, item_id: int) -> None:
        with self._db.session() as sess:
            item = sess.get(ChecklistItem, item_id)
            if item:
                sess.delete(item)
