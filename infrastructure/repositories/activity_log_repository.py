"""ActivityLog veri erişim katmanı."""
from __future__ import annotations

import json

from sqlalchemy import select

from domain.models.activity_log import ActivityLog
from infrastructure.repositories.base_repository import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLog]):
    model = ActivityLog

    def create(  # type: ignore[override] — log kaydı alanlardan kurulur, entity dışarıdan gelmez
        self,
        project_id: int,
        action: str,
        summary: str,
        entity_type: str,
        entity_id: int | None = None,
        metadata: dict | None = None,
    ) -> ActivityLog:
        log = ActivityLog(
            project_id=project_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            summary=summary,
            metadata_json=json.dumps(metadata, ensure_ascii=False) if metadata else None,
        )
        return super().create(log)

    def get_by_project(self, project_id: int, limit: int = 50) -> list[ActivityLog]:
        with self._db.session() as sess:
            stmt = (
                select(ActivityLog)
                .where(ActivityLog.project_id == project_id)
                .order_by(ActivityLog.created_at.desc())
                .limit(limit)
            )
            return list(sess.scalars(stmt).all())
