"""Alembic based runtime migration orchestration."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app import config
from infrastructure.database.migration_runner import run_migrations as run_legacy_migrations

logger = logging.getLogger(__name__)

HEAD_REVISION = "0004_create_memos_table"

if TYPE_CHECKING:
    from alembic.config import Config


def run_alembic_migrations(engine: Engine, database_url: str) -> None:
    """Run Alembic migrations, bridging existing schema_migrations databases once."""
    if _is_memory_database(database_url):
        logger.info("In-memory SQLite detected; using legacy metadata runner for tests.")
        run_legacy_migrations(engine)
        _stamp_head_on_engine(engine)
        return

    try:
        from alembic import command
        from alembic.config import Config
    except ImportError:
        logger.warning("Alembic is not installed; falling back to legacy migration runner.")
        run_legacy_migrations(engine)
        _stamp_head_on_engine(engine)
        return

    cfg = _build_alembic_config(database_url)
    inspector = inspect(engine)
    has_alembic = inspector.has_table("alembic_version")
    has_legacy = inspector.has_table("schema_migrations")

    if has_legacy and not has_alembic:
        logger.info("Legacy schema_migrations database detected; validating before Alembic stamp.")
        run_legacy_migrations(engine)
        _assert_integrity(engine)
        command.stamp(cfg, "head")
        return

    command.upgrade(cfg, "head")


def _build_alembic_config(database_url: str) -> "Config":
    from alembic.config import Config

    ini_path = config.APP_DIR / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(config.ALEMBIC_MIGRATIONS_DIR))
    cfg.set_main_option("sqlalchemy.url", database_url)
    return cfg


def _is_memory_database(database_url: str) -> bool:
    return database_url.startswith("sqlite:///:memory:") or database_url == "sqlite://"


def _assert_integrity(engine: Engine) -> None:
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA integrity_check")).scalar_one()
    if result != "ok":
        raise RuntimeError(f"SQLite integrity_check failed: {result}")


def _stamp_head_on_engine(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
                """
            )
        )
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(
            text("INSERT INTO alembic_version(version_num) VALUES (:version)"),
            {"version": HEAD_REVISION},
        )
