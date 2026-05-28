"""Görev ve checklist öğesi veri erişim katmanı."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.models.checklist_item import ChecklistItem
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager


class TaskRepository:
    """Task ve ChecklistItem kayıtları üzerinde CRUD işlemlerini yönetir."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_all(self) -> list[Task]:
        with self._db.session() as sess:
            stmt = (
                select(Task)
                .options(selectinload(Task.checklist_items))
                .order_by(Task.project_id, Task.order_index, Task.id)
            )
            return list(sess.scalars(stmt).all())

    def get_by_project(self, project_id: int) -> list[Task]:
        with self._db.session() as sess:
            stmt = (
                select(Task)
                .options(selectinload(Task.checklist_items))
                .where(Task.project_id == project_id)
                .order_by(Task.parent_task_id.is_not(None), Task.parent_task_id, Task.order_index, Task.id)
            )
            return list(sess.scalars(stmt).all())

    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self._db.session() as sess:
            stmt = (
                select(Task)
                .options(selectinload(Task.checklist_items))
                .where(Task.id == task_id)
            )
            return sess.scalar(stmt)

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

    def update_many(self, tasks: list[Task]) -> list[Task]:
        with self._db.session() as sess:
            merged_tasks = [sess.merge(task) for task in tasks]
            sess.flush()
            for task in merged_tasks:
                sess.refresh(task)
                sess.expunge(task)
            return merged_tasks

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

    def get_task_for_checklist_item(self, item_id: int) -> Optional[Task]:
        with self._db.session() as sess:
            item = sess.get(ChecklistItem, item_id)
            if item is None:
                return None
            return sess.get(Task, item.task_id)

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

    def calculate_progress_percent(self, project_id: int) -> int:
        """
        Yaprak task'ların tamamlanma yüzdesini tek SQL sorgusuyla hesaplar.
        GROUP tipindeki ve alt task'ı olan (parent) task'lar hesaba katılmaz.
        Checklist içeren task'larda tamamlanan madde oranı skor olarak kullanılır.
        """
        from sqlalchemy import Float, case, cast, func, literal

        from domain.enums.task_status import TaskStatus
        from domain.enums.task_type import TaskType
        from domain.models.checklist_item import ChecklistItem

        with self._db.session() as sess:
            # Başka task'ların parent'ı olan task id'leri — bunlar yaprak değil
            parent_ids_subq = (
                select(Task.parent_task_id)
                .where(Task.project_id == project_id)
                .where(Task.parent_task_id.is_not(None))
            )

            ci_total_sub = (
                select(ChecklistItem.task_id, func.count().label("total"))
                .group_by(ChecklistItem.task_id)
                .subquery("ci_total")
            )
            ci_done_sub = (
                select(ChecklistItem.task_id, func.count().label("done"))
                .where(ChecklistItem.is_done.is_(True))
                .group_by(ChecklistItem.task_id)
                .subquery("ci_done")
            )

            # Her yaprak task için: DONE=1.0, checklist varsa oran, yoksa 0.0
            score_expr = case(
                (Task.status == TaskStatus.DONE.value, literal(1.0)),
                (
                    ci_total_sub.c.total > 0,
                    cast(func.coalesce(ci_done_sub.c.done, 0), Float)
                    / cast(ci_total_sub.c.total, Float),
                ),
                else_=literal(0.0),
            )

            stmt = (
                select(
                    func.count().label("total"),
                    func.sum(score_expr).label("score_sum"),
                )
                .outerjoin(ci_total_sub, ci_total_sub.c.task_id == Task.id)
                .outerjoin(ci_done_sub, ci_done_sub.c.task_id == Task.id)
                .where(Task.project_id == project_id)
                .where(Task.task_type != TaskType.GROUP.value)
                .where(Task.id.not_in(parent_ids_subq))
            )

            row = sess.execute(stmt).one()
            total: int = row.total
            score_sum: float | None = row.score_sum
            if not total or score_sum is None:
                return 0
            return round((score_sum / total) * 100)
