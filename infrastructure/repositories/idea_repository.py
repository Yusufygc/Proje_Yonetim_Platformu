from typing import Sequence

from sqlalchemy import select

from domain.models.idea import Idea
from infrastructure.repositories.base_repository import BaseRepository


class IdeaRepository(BaseRepository[Idea]):
    """Fikirler tablosuna veri erişim katmanı."""

    model = Idea

    def get_all(self, include_converted: bool = False) -> Sequence[Idea]:
        with self._db.session() as sess:
            stmt = select(Idea).order_by(Idea.created_at.desc())
            if not include_converted:
                stmt = stmt.where(Idea.converted_project_id.is_(None))
            return sess.scalars(stmt).all()
