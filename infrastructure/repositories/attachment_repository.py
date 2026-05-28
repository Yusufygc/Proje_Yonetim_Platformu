"""Attachment veri erişim katmanı."""
from __future__ import annotations

from sqlalchemy import select

from domain.models.attachment import Attachment
from infrastructure.database.db_manager import DatabaseManager


class AttachmentRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, attachment: Attachment) -> Attachment:
        with self._db.session() as sess:
            sess.add(attachment)
            sess.flush()
            sess.refresh(attachment)
            sess.expunge(attachment)
            return attachment

    def get_by_project(self, project_id: int) -> list[Attachment]:
        with self._db.session() as sess:
            stmt = (
                select(Attachment)
                .where(Attachment.project_id == project_id)
                .order_by(Attachment.display_order, Attachment.created_at.desc())
            )
            return list(sess.scalars(stmt).all())

    def delete(self, attachment_id: int) -> None:
        with self._db.session() as sess:
            item = sess.get(Attachment, attachment_id)
            if item:
                sess.delete(item)
