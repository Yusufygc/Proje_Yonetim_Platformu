from typing import Optional, Sequence

from sqlalchemy import select

from domain.models.decision_record import DecisionRecord
from infrastructure.database.db_manager import DatabaseManager


class DecisionRepository:
    """Proje Kararları (DecisionRecord) için veri erişim katmanı."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, decision: DecisionRecord) -> DecisionRecord:
        with self._db.session() as sess:
            sess.add(decision)
            sess.flush()
            sess.refresh(decision)
            sess.expunge(decision)
            return decision

    def get_by_id(self, decision_id: int) -> Optional[DecisionRecord]:
        with self._db.session() as sess:
            return sess.get(DecisionRecord, decision_id)

    def get_by_project(self, project_id: int) -> Sequence[DecisionRecord]:
        with self._db.session() as sess:
            stmt = select(DecisionRecord).where(DecisionRecord.project_id == project_id).order_by(DecisionRecord.created_at.desc())
            return sess.scalars(stmt).all()

    def update(self, decision: DecisionRecord) -> DecisionRecord:
        with self._db.session() as sess:
            merged = sess.merge(decision)
            sess.flush()
            sess.refresh(merged)
            sess.expunge(merged)
            return merged

    def delete(self, decision_id: int) -> None:
        with self._db.session() as sess:
            decision = sess.get(DecisionRecord, decision_id)
            if decision:
                sess.delete(decision)
