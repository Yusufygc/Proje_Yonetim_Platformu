from __future__ import annotations

import logging
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.managers.backup_manager import BackupManager
from core.managers.log_manager import install_global_exception_hook, setup_logging
from core.managers.secret_manager import SecretManager
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


def test_secret_manager_uses_keyring(monkeypatch):
    store: dict[tuple[str, str], str] = {}

    class FakeKeyring:
        @staticmethod
        def set_password(service, key, value):
            store[(service, key)] = value

        @staticmethod
        def get_password(service, key):
            return store.get((service, key))

        @staticmethod
        def delete_password(service, key):
            store.pop((service, key), None)

    monkeypatch.setitem(sys.modules, "keyring", FakeKeyring)
    manager = SecretManager(service_name="test-service")

    manager.set_secret("token", "abc")
    assert manager.get_secret("token") == "abc"
    manager.delete_secret("token")
    assert manager.get_secret("token") is None


def test_memory_migration_stamps_alembic_head(test_db):
    with test_db.engine.connect() as conn:
        version = conn.exec_driver_sql("SELECT version_num FROM alembic_version").scalar_one()
    assert version == HEAD_REVISION
