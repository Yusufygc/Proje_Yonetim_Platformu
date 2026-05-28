"""
Uygulama genelinde tek bir DB bağlantısı ve scoped_session yöneten Singleton.
SQLAlchemy 2.0 style kullanılır; ham SQL yasaktır (RULES.md gereği).
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from core.exceptions.base_exception import DatabaseConnectionError
from infrastructure.database.alembic_runner import run_alembic_migrations

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLAlchemy engine ve session fabrikasını merkezi olarak yöneten Singleton.
    """

    _instance: DatabaseManager | None = None

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: Engine = create_engine(
            database_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
        self._scoped_session = scoped_session(self._session_factory)
        self._enable_wal_mode()

    @classmethod
    def instance(cls, database_url: str | None = None) -> "DatabaseManager":
        if cls._instance is None:
            if database_url is None:
                raise RuntimeError("DatabaseManager ilk çağrıda database_url gerektirir.")
            cls._instance = cls(database_url)
        return cls._instance

    def _enable_wal_mode(self) -> None:
        """Eşzamanlı okuma performansı için SQLite WAL modunu etkinleştirir."""
        with self._engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()

    def create_all_tables(self) -> None:
        """Geriye dönük ad: migration runner'ı çalıştırır."""
        self.run_migrations()

    def run_migrations(self) -> None:
        """Tüm idempotent migration'ları çalıştırır."""
        try:
            run_alembic_migrations(self._engine, self._database_url)
        except Exception as exc:
            raise DatabaseConnectionError(f"Veritabani migration baslatilamadi: {exc}") from exc
        logger.info("Veritabanı migration'ları doğrulandı.")

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Transaction-aware session context manager.
        Hata durumunda otomatik rollback yapar.
        """
        sess: Session = self._scoped_session()
        try:
            yield sess
            sess.commit()
        except Exception:
            sess.rollback()
            raise
        finally:
            self._scoped_session.remove()

    @property
    def engine(self) -> Engine:
        return self._engine
