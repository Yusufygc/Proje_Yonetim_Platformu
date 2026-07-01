"""
Tüm repository'ler için ortak CRUD altyapısı.

create / get_by_id / update / delete kalıpları 12 repository'de birebir
tekrarlandığı için tek generic taban sınıfta toplanır (DRY). Entity'ler
session kapandıktan sonra da kullanılabilsin diye flush+refresh+expunge
ile detached olarak döndürülür (UI thread'e güvenli aktarım).
"""
from __future__ import annotations

from typing import ClassVar, Generic, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.db_manager import DatabaseManager

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Tek bir ORM modeli üzerinde standart CRUD işlemleri."""

    #: Alt sınıfın bağlı olduğu ORM model sınıfı.
    model: ClassVar[type]

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def _query_options(self) -> tuple:
        """select() sorgularına eklenecek loader seçenekleri (örn. selectinload)."""
        return ()

    @staticmethod
    def _detach(sess: Session, entity: T) -> T:
        """Entity'yi kalıcılaştırıp session'dan koparır; dışarıda güvenle taşınır."""
        sess.flush()
        sess.refresh(entity)
        sess.expunge(entity)
        return entity

    def create(self, entity: T) -> T:
        with self._db.session() as sess:
            sess.add(entity)
            return self._detach(sess, entity)

    def create_many(self, entities: list[T]) -> list[T]:
        with self._db.session() as sess:
            sess.add_all(entities)
            sess.flush()
            for entity in entities:
                sess.refresh(entity)
                sess.expunge(entity)
            return entities

    def get_by_id(self, entity_id: int) -> Optional[T]:
        with self._db.session() as sess:
            options = self._query_options()
            if not options:
                return sess.get(self.model, entity_id)
            stmt = select(self.model).options(*options).where(self.model.id == entity_id)
            return sess.scalar(stmt)

    def update(self, entity: T) -> T:
        with self._db.session() as sess:
            merged = sess.merge(entity)
            return self._detach(sess, merged)

    def update_many(self, entities: list[T]) -> list[T]:
        with self._db.session() as sess:
            merged_entities = [sess.merge(entity) for entity in entities]
            sess.flush()
            for entity in merged_entities:
                sess.refresh(entity)
                sess.expunge(entity)
            return merged_entities

    def delete(self, entity_id: int) -> None:
        with self._db.session() as sess:
            entity = sess.get(self.model, entity_id)
            if entity is not None:
                sess.delete(entity)

    def _apply_order(self, ordered_ids: list[int], order_field: str) -> None:
        """ID listesindeki sırayı 0'dan başlayarak order_field kolonuna yazar.

        Sürükle-bırak sonrası kalıcılaştırma için kullanılır (Not/Fikir/Proje
        listeleri); kolon adı modele göre değiştiğinden alt sınıf belirler.
        """
        if not ordered_ids:
            return
        with self._db.session() as sess:
            for index, entity_id in enumerate(ordered_ids):
                entity = sess.get(self.model, entity_id)
                if entity is not None:
                    setattr(entity, order_field, index)
            sess.flush()


class ProjectScopedRepository(BaseRepository[T]):
    """project_id kolonuna sahip modeller için ortak proje-bazlı sorgu."""

    def _project_order(self) -> tuple:
        """get_by_project sıralaması; alt sınıf kendi kolon(lar)ını döndürür."""
        return ()

    def get_by_project(self, project_id: int) -> list[T]:
        with self._db.session() as sess:
            stmt = select(self.model).where(self.model.project_id == project_id)
            options = self._query_options()
            if options:
                stmt = stmt.options(*options)
            order = self._project_order()
            if order:
                stmt = stmt.order_by(*order)
            return list(sess.scalars(stmt).all())
