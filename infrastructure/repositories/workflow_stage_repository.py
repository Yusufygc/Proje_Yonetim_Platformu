"""WorkflowStage şablon veri erişim katmanı."""
from __future__ import annotations

from sqlalchemy import select

from domain.models.workflow_stage import WorkflowStage
from infrastructure.repositories.base_repository import BaseRepository


class WorkflowStageRepository(BaseRepository[WorkflowStage]):
    model = WorkflowStage

    def get_defaults(self) -> list[WorkflowStage]:
        with self._db.session() as sess:
            stmt = (
                select(WorkflowStage)
                .where(WorkflowStage.is_default.is_(True))
                .order_by(WorkflowStage.display_order)
            )
            return list(sess.scalars(stmt).all())
