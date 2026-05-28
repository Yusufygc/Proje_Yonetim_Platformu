from typing import Optional, Sequence

from sqlalchemy import select

from domain.models.idea import Idea
from infrastructure.database.db_manager import DatabaseManager


class IdeaRepository:
    """Fikirler tablosuna veri erişim katmanı."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, idea: Idea) -> Idea:
        with self._db.session() as sess:
            sess.add(idea)
            sess.flush()
            sess.refresh(idea)
            sess.expunge(idea)
            return idea

    def get_by_id(self, idea_id: int) -> Optional[Idea]:
        with self._db.session() as sess:
            return sess.get(Idea, idea_id)

    def get_all(self, include_converted: bool = False) -> Sequence[Idea]:
        with self._db.session() as sess:
            stmt = select(Idea).order_by(Idea.created_at.desc())
            if not include_converted:
                stmt = stmt.where(Idea.converted_project_id.is_(None))
            return sess.scalars(stmt).all()

    def update(self, idea: Idea) -> Idea:
        with self._db.session() as sess:
            merged = sess.merge(idea)
            sess.flush()
            sess.refresh(merged)
            sess.expunge(merged)
            return merged

    def delete(self, idea_id: int) -> None:
        with self._db.session() as sess:
            idea = sess.get(Idea, idea_id)
            if idea:
                sess.delete(idea)
