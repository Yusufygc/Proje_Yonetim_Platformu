from __future__ import annotations

import logging
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.managers.backup_manager import BackupManager
from core.managers.log_manager import install_global_exception_hook, setup_logging
from core.workers.worker import Worker
from infrastructure.database.alembic_runner import HEAD_REVISION


def test_setup_logging_is_idempotent(tmp_path):
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    root.handlers.clear()
    try:
        log_file = tmp_path / "app.log"
        setup_logging(log_file, 1024, 1)
        setup_logging(log_file, 1024, 1)

        marked_handlers = [
            handler
            for handler in root.handlers
            if getattr(handler, "_proje_takip_file_handler", False)
            or getattr(handler, "_proje_takip_console_handler", False)
        ]
        assert len(marked_handlers) == 2
    finally:
        root.handlers.clear()
        root.handlers.extend(original_handlers)


def test_global_exception_hook_logs_and_uses_dialog(monkeypatch, caplog):
    calls: list[tuple[str, str]] = []

    class FakeApplication:
        @staticmethod
        def instance():
            return object()

    class FakeMessageBox:
        @staticmethod
        def critical(parent, title, message):
            calls.append((title, message))

    monkeypatch.setitem(
        sys.modules,
        "PySide6.QtWidgets",
        type("QtWidgets", (), {"QApplication": FakeApplication, "QMessageBox": FakeMessageBox}),
    )
    install_global_exception_hook(show_dialog=True)

    with caplog.at_level(logging.CRITICAL, logger="global_exception_hook"):
        sys.excepthook(RuntimeError, RuntimeError("boom"), None)

    assert any("Unhandled exception" in record.message for record in caplog.records)
    assert calls and calls[0][0] == "Beklenmeyen Hata"


def test_worker_logs_exception(caplog):
    def fail():
        raise RuntimeError("worker boom")

    worker = Worker(fail)
    errors: list[str] = []
    worker.signals.error.connect(errors.append)

    with caplog.at_level(logging.ERROR, logger="core.workers.worker"):
        worker.run()

    assert errors == ["worker boom"]
    assert any("Worker failed" in record.message for record in caplog.records)


def test_startup_backup_creates_file_and_rotates(tmp_path):
    db_path = tmp_path / "app.db"
    backups_dir = tmp_path / ".backups"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE sample(id INTEGER PRIMARY KEY)")

    manager = BackupManager(db_path, backups_dir, keep_last=2)
    first = manager.run_startup_backup()
    second = manager.run_startup_backup()
    third = manager.run_startup_backup()

    assert first is not None
    assert second is not None
    assert third is not None
    backups = sorted(backups_dir.glob("backup_*.db"))
    assert len(backups) <= 2


def test_startup_backup_when_data_only_in_wal_should_include_it(tmp_path):
    db_path = tmp_path / "app.db"
    live = sqlite3.connect(db_path)
    live.execute("PRAGMA journal_mode=WAL")
    live.execute("PRAGMA wal_autocheckpoint=0")
    live.execute("CREATE TABLE sample(id INTEGER PRIMARY KEY, label TEXT)")
    live.execute("INSERT INTO sample(label) VALUES ('wal-only')")
    live.commit()

    backup = BackupManager(db_path, tmp_path / ".backups").run_startup_backup()

    assert backup is not None
    with sqlite3.connect(backup) as restored:
        assert restored.execute("SELECT label FROM sample").fetchall() == [("wal-only",)]
    live.close()


def test_memory_migration_stamps_alembic_head(test_db):
    with test_db.engine.connect() as conn:
        version = conn.exec_driver_sql("SELECT version_num FROM alembic_version").scalar_one()
    assert version == HEAD_REVISION


def test_data_paths_when_running_tests_should_not_point_to_real_user_data() -> None:
    from app import config

    real_dirs = (
        Path(os.environ.get("LOCALAPPDATA", str(Path.home()))).resolve() / "ProjeTakip",
        Path.home().resolve() / ".proje_takip",
    )
    for path in (config.DATA_DIR, config.LOG_FILE, config.MEMO_IMAGES_DIR, config.BACKUPS_DIR):
        resolved = Path(path).resolve()
        assert not any(resolved == real or real in resolved.parents for real in real_dirs)
