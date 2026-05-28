from typing import Optional, Sequence

from sqlalchemy import select

from domain.models.resource import Resource
from infrastructure.database.db_manager import DatabaseManager


class ResourceRepository:
    """Proje Kaynakları (Resource) için veri erişim katmanı."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create(self, resource: Resource) -> Resource:
        with self._db.session() as sess:
            sess.add(resource)
            sess.flush()
            sess.refresh(resource)
            sess.expunge(resource)
            return resource

    def get_by_id(self, resource_id: int) -> Optional[Resource]:
        with self._db.session() as sess:
            return sess.get(Resource, resource_id)

    def get_by_project(self, project_id: int) -> Sequence[Resource]:
        with self._db.session() as sess:
            stmt = select(Resource).where(Resource.project_id == project_id).order_by(Resource.created_at.desc())
            return sess.scalars(stmt).all()

    def update(self, resource: Resource) -> Resource:
        with self._db.session() as sess:
            merged = sess.merge(resource)
            sess.flush()
            sess.refresh(merged)
            sess.expunge(merged)
            return merged

    def delete(self, resource_id: int) -> None:
        with self._db.session() as sess:
            resource = sess.get(Resource, resource_id)
            if resource:
                sess.delete(resource)
