"""
Pytest fixture'ları — RAM üzerinde çalışan test veritabanı ve DI container.
Her test bağımsız, temiz bir veritabanıyla başlar.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Test çalışmasında proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.database.db_manager import DatabaseManager


@pytest.fixture(scope="function")
def test_db() -> DatabaseManager:
    """
    Her test fonksiyonu için ayrı, bellek-içi SQLite veritabanı döndürür.
    Test sonunda otomatik temizlenir.
    """
    # Singleton state'i sıfırla
    DatabaseManager._instance = None

    db = DatabaseManager.instance("sqlite:///:memory:")
    db.create_all_tables()
    return db
