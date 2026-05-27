from typing import Optional, Sequence

from sqlalchemy import select

from domain.models.note import Note
from infrastructure.database.db_manager import DatabaseManager


class NoteRepository:
    """Proje Notları (Note) için veri erişim katmanı."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, note: Note) -> Note:
        with self._db.session() as sess:
            sess.add(note)
            sess.commit()
            sess.refresh(note)
            return note

    def get_by_id(self, note_id: int) -> Optional[Note]:
        with self._db.session() as sess:
            return sess.get(Note, note_id)

    def get_by_project(self, project_id: int) -> Sequence[Note]:
        with self._db.session() as sess:
            stmt = select(Note).where(Note.project_id == project_id).order_by(Note.created_at.desc())
            return sess.scalars(stmt).all()

    def update(self, note: Note) -> Note:
        with self._db.session() as sess:
            merged = sess.merge(note)
            sess.commit()
            sess.refresh(merged)
            return merged

    def delete(self, note_id: int) -> None:
        with self._db.session() as sess:
            note = sess.get(Note, note_id)
            if note:
                sess.delete(note)
                sess.commit()
