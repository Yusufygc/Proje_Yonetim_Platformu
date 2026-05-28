"""Startup database integrity check and backup rotation."""
from __future__ import annotations

import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class BackupManager:
    """Creates timestamped SQLite backups before runtime migrations."""

    def __init__(self, database_path: Path, backups_dir: Path, keep_last: int = 5) -> None:
        self._database_path = database_path
        self._backups_dir = backups_dir
        self._keep_last = keep_last

    def run_startup_backup(self) -> Path | None:
        """Validate and back up the DB if it already exists."""
        if not self._database_path.exists():
            logger.info("Database file does not exist yet; startup backup skipped.")
            return None

        self._assert_integrity()
        self._backups_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self._backups_dir / f"backup_{timestamp}.db"
        counter = 1
        while target.exists():
            target = self._backups_dir / f"backup_{timestamp}_{counter}.db"
            counter += 1
        shutil.copy2(self._database_path, target)
        self._rotate()
        logger.info("Startup database backup created: %s", target)
        return target

    def _assert_integrity(self) -> None:
        try:
            with sqlite3.connect(self._database_path) as conn:
                result = conn.execute("PRAGMA integrity_check").fetchone()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Database integrity check could not run: {exc}") from exc

        status = result[0] if result else "unknown"
        if status != "ok":
            raise RuntimeError(f"Database integrity check failed: {status}")

    def _rotate(self) -> None:
        backups = sorted(
            self._backups_dir.glob("backup_*.db"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for stale in backups[self._keep_last :]:
            stale.unlink(missing_ok=True)
            logger.info("Old database backup removed: %s", stale)
