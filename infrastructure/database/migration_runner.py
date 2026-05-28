"""Minimal idempotent migration runner for the local SQLite database."""
from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from infrastructure.database.base_model import Base

logger = logging.getLogger(__name__)

Migration = Callable[[Engine], None]

DEFAULT_WORKFLOW_STAGES = [
    ("Fikir", "Fikir ve ihtiyaç netleştirme", 0),
    ("Analiz", "Kapsam, problem ve çözüm analizi", 1),
    ("Tasarım", "Mimari ve UI/UX tasarımı", 2),
    ("Geliştirme", "Kodlama ve implementasyon", 3),
    ("Test", "Test ve kalite güvencesi", 4),
    ("Yayın", "Yayına alma ve paketleme", 5),
    ("Bakım", "İyileştirme ve takip", 6),
    ("Tamamlandı", "Proje kapanışı", 7),
]


def run_migrations(engine: Engine) -> None:
    """Run all known migrations once; every migration is still idempotent."""
    _import_models()
    _ensure_migration_table(engine)
    migrations: list[tuple[str, Migration]] = [
        ("001_create_metadata_tables", _create_metadata_tables),
        ("002_add_mvp_columns", _add_mvp_columns),
        ("003_normalize_enums_and_seed_workflow", _normalize_enums_and_seed_workflow),
        ("004_add_task_hierarchy_columns", _add_task_hierarchy_columns),
        ("005_add_performance_indexes", _add_performance_indexes),
    ]
    for migration_id, migration in migrations:
        if _is_applied(engine, migration_id):
            continue
        logger.info("Migration çalışıyor: %s", migration_id)
        migration(engine)
        _mark_applied(engine, migration_id)


def _import_models() -> None:
    import domain.models  # noqa: F401


def _ensure_migration_table(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )


def _is_applied(engine: Engine, migration_id: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM schema_migrations WHERE version = :version"),
            {"version": migration_id},
        ).first()
        return result is not None


def _mark_applied(engine: Engine, migration_id: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("INSERT OR IGNORE INTO schema_migrations(version) VALUES (:version)"),
            {"version": migration_id},
        )


def _create_metadata_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def _add_mvp_columns(engine: Engine) -> None:
    _create_metadata_tables(engine)
    _add_column(engine, "projects", "health", "VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN'")
    _add_column(engine, "projects", "manual_progress_percent", "INTEGER")
    _add_column(engine, "project_stages", "started_at", "DATETIME")
    _add_column(engine, "project_stages", "acceptance_criteria", "TEXT")
    _add_column(engine, "tasks", "estimated_minutes", "INTEGER")
    _add_column(engine, "tasks", "spent_minutes", "INTEGER")
    _add_column(engine, "tasks", "completed_at", "DATETIME")
    _add_column(engine, "tasks", "blocked_reason", "TEXT")
    _add_column(engine, "checklist_items", "completed_at", "DATETIME")
    _add_column(engine, "decision_records", "superseded_by_decision_id", "INTEGER")


def _normalize_enums_and_seed_workflow(engine: Engine) -> None:
    _update_value(engine, "ideas", "status", "DRAFT", "RAW")
    _update_value(engine, "ideas", "status", "POSTPONED", "DEFERRED")
    _update_value(engine, "project_stages", "status", "PENDING", "NOT_STARTED")
    _update_value(engine, "project_stages", "status", "COMPLETED", "DONE")
    _update_value(engine, "decision_records", "status", "CHANGED", "SUPERSEDED")
    _update_value(engine, "decision_records", "status", "CANCELED", "CANCELLED")
    _seed_workflow_stages(engine)


def _add_task_hierarchy_columns(engine: Engine) -> None:
    _add_column(engine, "tasks", "parent_task_id", "INTEGER")
    _create_index(engine, "idx_tasks_parent_task_id", "tasks", "parent_task_id")


def _add_performance_indexes(engine: Engine) -> None:
    _create_index(engine, "idx_tasks_status", "tasks", "status")
    _create_index(engine, "idx_tasks_priority", "tasks", "priority")
    _create_index(engine, "idx_tasks_task_type", "tasks", "task_type")
    _create_index(engine, "idx_projects_status", "projects", "status")
    _create_index(engine, "idx_projects_is_archived", "projects", "is_archived")
    _create_index(engine, "idx_ideas_status", "ideas", "status")


def _add_column(engine: Engine, table_name: str, column_name: str, column_sql: str) -> None:
    if not inspect(engine).has_table(table_name):
        return
    columns = {col["name"] for col in inspect(engine).get_columns(table_name)}
    if column_name in columns:
        return
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"))


def _create_index(engine: Engine, index_name: str, table_name: str, column_name: str) -> None:
    if not inspect(engine).has_table(table_name):
        return
    columns = {col["name"] for col in inspect(engine).get_columns(table_name)}
    if column_name not in columns:
        return
    with engine.begin() as conn:
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"))


def _update_value(engine: Engine, table_name: str, column_name: str, old: str, new: str) -> None:
    if not inspect(engine).has_table(table_name):
        return
    with engine.begin() as conn:
        conn.execute(
            text(f"UPDATE {table_name} SET {column_name} = :new WHERE {column_name} = :old"),
            {"old": old, "new": new},
        )


def _seed_workflow_stages(engine: Engine) -> None:
    if not inspect(engine).has_table("workflow_stages"):
        return
    with engine.begin() as conn:
        existing = conn.execute(text("SELECT COUNT(*) FROM workflow_stages")).scalar_one()
        if existing:
            return
        for name, description, display_order in DEFAULT_WORKFLOW_STAGES:
            conn.execute(
                text(
                    """
                    INSERT INTO workflow_stages(name, description, display_order, is_default)
                    VALUES (:name, :description, :display_order, 1)
                    """
                ),
                {
                    "name": name,
                    "description": description,
                    "display_order": display_order,
                },
            )
