"""MemoRepository — memos tablosu için veri erişim katmanı."""
from __future__ import annotations

from sqlalchemy import select

from domain.models.memo import Memo
from infrastructure.repositories.base_repository import BaseRepository


class MemoRepository(BaseRepository[Memo]):
    model = Memo

    def get_all(self) -> list[Memo]:
        with self._db.session() as sess:
            stmt = select(Memo).order_by(Memo.sort_order, Memo.id)
            entities = list(sess.scalars(stmt).all())
            for e in entities:
                sess.expunge(e)
            return entities

    def reorder(self, ordered_ids: list[int]) -> None:
        self._apply_order(ordered_ids, "sort_order")
