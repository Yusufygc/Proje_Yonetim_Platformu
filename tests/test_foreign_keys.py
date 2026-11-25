"""SQLite foreign_keys ayarı bağlantı bazındadır; havuzdaki her bağlantıda açık olmalı.

Bellek-içi veritabanı tek bağlantı kullandığı için bu testler geçici dosya veritabanıyla çalışır.
"""
from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import text

from domain.models.idea import Idea
from domain.models.note import Note
from domain.models.project import Project
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.repositories.base_repository import BaseRepository
from infrastructure.repositories.project_repository import ProjectRepository


@pytest.fixture
def file_db(tmp_path: Path) -> Generator[DatabaseManager, None, None]:
    db = DatabaseManager(f"sqlite:///{tmp_path / 'fk.db'}")
    db.run_migrations()
    yield db
    db.engine.dispose()


def _seed_project(db: DatabaseManager) -> int:
    with db.session() as sess:
        project = Project(title="Proje", slug="proje")
        sess.add(project)
        sess.flush()
        return project.id


def test_connect_when_pool_opens_several_connections_should_enable_foreign_keys_on_each(
    file_db: DatabaseManager,
) -> None:
    connections = [file_db.engine.connect() for _ in range(3)]
    try:
        values = [conn.execute(text("PRAGMA foreign_keys")).scalar_one() for conn in connections]
    finally:
        for conn in connections:
            conn.close()

    assert values == [1, 1, 1]


def test_delete_when_using_additional_connection_should_apply_ondelete_rules(
    file_db: DatabaseManager,
) -> None:
    project_id = _seed_project(file_db)
    with file_db.session() as sess:
        idea = Idea(title="Fikir", converted_project_id=project_id)
        sess.add(idea)
        sess.flush()
        idea_id = idea.id

    # İlk bağlantı meşgul tutulur; silme işlemi havuzun yeni açtığı bağlantıya düşer.
    held = file_db.engine.connect()
    try:
        ProjectRepository(file_db).delete(project_id)
    finally:
        held.close()

    with file_db.session() as sess:
        assert sess.get(Idea, idea_id).converted_project_id is None


def test_update_and_delete_when_legacy_orphans_exist_should_still_succeed(
    file_db: DatabaseManager,
) -> None:
    """Ayar kapalıyken oluşmuş yetim referanslar sonraki yazma işlemlerini engellememeli."""
    project_id = _seed_project(file_db)
    with file_db.engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        conn.exec_driver_sql(
            "INSERT INTO notes(project_id, note_type, title, body, task_id, sort_order) "
            "VALUES (?, 'GENERAL', 'n', 'b', 999, 0)",
            (project_id,),
        )
        conn.exec_driver_sql(
            "INSERT INTO ideas(title, status, priority, converted_project_id, sort_order) "
            "VALUES ('f', 'RAW', 'MEDIUM', 999, 0)"
        )
        conn.commit()
        conn.invalidate()  # ayarı kapatılmış bağlantı havuza dönmemeli

    class NoteRepo(BaseRepository[Note]):
        model = Note

    class IdeaRepo(BaseRepository[Idea]):
        model = Idea

    for repo in (NoteRepo(file_db), IdeaRepo(file_db)):
        entity = repo.get_by_id(1)
        entity.title = "yeni"
        repo.update(entity)
    IdeaRepo(file_db).delete(1)
    ProjectRepository(file_db).delete(project_id)

    with file_db.session() as sess:
        assert sess.get(Note, 1) is None
        assert sess.get(Idea, 1) is None


def test_run_migrations_when_alembic_rebuilds_parent_table_should_keep_child_rows(
    file_db: DatabaseManager,
) -> None:
    """0003 projects tablosunu yeniden kurar; FK açık olsaydı DROP TABLE alt kayıtları silerdi."""
    project_id = _seed_project(file_db)
    with file_db.session() as sess:
        sess.add(Task(project_id=project_id, title="Görev"))
    with file_db.engine.begin() as conn:
        conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN demo_url VARCHAR(500)")
        conn.exec_driver_sql("UPDATE alembic_version SET version_num = '0002_drop_idea_score_fields'")

    file_db.run_migrations()

    with file_db.engine.connect() as conn:
        columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(projects)")]
        task_count = conn.exec_driver_sql("SELECT COUNT(*) FROM tasks").scalar_one()
    assert "demo_url" not in columns
    assert task_count == 1
