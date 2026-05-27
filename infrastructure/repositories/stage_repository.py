"""Proje aşaması veri erişim katmanı."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from domain.models.project_stage import ProjectStage
from infrastructure.database.db_manager import DatabaseManager


class StageRepository:
    """ProjectStage kayıtları üzerinde CRUD işlemlerini yönetir."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_by_project(self, project_id: int) -> list[ProjectStage]:
        with self._db.session() as sess:
            stmt = (
                select(ProjectStage)
                .where(ProjectStage.project_id == project_id)
                .order_by(ProjectStage.order_index)
            )
            return list(sess.scalars(stmt).all())

    def get_by_id(self, stage_id: int) -> Optional[ProjectStage]:
        with self._db.session() as sess:
            return sess.get(ProjectStage, stage_id)

    def create_many(self, stages: list[ProjectStage]) -> list[ProjectStage]:
        with self._db.session() as sess:
            for stage in stages:
                sess.add(stage)
            sess.flush()
            for stage in stages:
                sess.refresh(stage)
                sess.expunge(stage)
            return stages

    def update(self, stage: ProjectStage) -> ProjectStage:
        with self._db.session() as sess:
            merged = sess.merge(stage)
            sess.flush()
            sess.refresh(merged)
            sess.expunge(merged)
            return merged
