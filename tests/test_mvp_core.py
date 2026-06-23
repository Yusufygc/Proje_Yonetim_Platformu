from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from sqlalchemy import inspect, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.exceptions.task_exceptions import TaskHierarchyError
from domain.enums.idea_status import IdeaStatus
from domain.enums.stage_status import StageStatus
from domain.enums.task_status import TaskStatus
from domain.enums.task_type import TaskType
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.idea_repository import IdeaRepository
from infrastructure.repositories.project_idea_repository import ProjectIdeaRepository
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.project_tag_repository import ProjectTagRepository
from infrastructure.repositories.stage_repository import StageRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository
from services.export_service import ExportService
from services.idea_service import IdeaService
from services.project_service import ProjectService
from services.stage_service import StageService
from services.task_service import TaskService


@pytest.fixture()
def service_stack():
    DatabaseManager._instance = None
    db = DatabaseManager.instance("sqlite:///:memory:")
    db.run_migrations()
    activity_repo = ActivityLogRepository(db)
    task_repo = TaskRepository(db)
    project_repo = ProjectRepository(db)
    stage_service = StageService(
        StageRepository(db),
        WorkflowStageRepository(db),
        activity_repo,
        project_repository=project_repo,
    )
    project_service = ProjectService(
        project_repo,
        stage_service,
        activity_repo,
        ProjectTagRepository(db),
        task_repo,
    )
    task_service = TaskService(task_repo, project_service, activity_repo)
    idea_service = IdeaService(
        IdeaRepository(db),
        project_service,
        ProjectIdeaRepository(db),
        activity_repo,
    )
    return {
        "db": db,
        "activity_repo": activity_repo,
        "project_service": project_service,
        "stage_service": stage_service,
        "task_service": task_service,
        "idea_service": idea_service,
    }


def test_project_creation_creates_workflow_stages_and_activity(service_stack):
    project = service_stack["project_service"].create_project("MVP")

    stages = service_stack["stage_service"].get_stages(project.id)
    logs = service_stack["activity_repo"].get_by_project(project.id)

    assert len(stages) == 8
    assert stages[0].status == StageStatus.ACTIVE.value
    assert any(log.action == "PROJECT_CREATED" for log in logs)
    assert any(log.action == "STAGES_CREATED" for log in logs)


def test_idea_conversion_keeps_link_and_project_history(service_stack):
    idea = service_stack["idea_service"].create_idea(
        "Arama iyileştirme",
        problem="Fikirler kayboluyor",
        solution="Global arama",
    )

    project_id = service_stack["idea_service"].convert_idea_to_project(
        idea.id,
        {"title": "Arama Projesi"},
    )

    converted = service_stack["idea_service"].get_idea(idea.id)
    logs = service_stack["activity_repo"].get_by_project(project_id)

    assert converted.status == IdeaStatus.CONVERTED.value
    assert converted.converted_project_id == project_id
    assert any(log.action == "IDEA_CONVERTED" for log in logs)


def test_stage_completion_activates_next_stage(service_stack):
    project = service_stack["project_service"].create_project("Aşama Testi")
    first = service_stack["stage_service"].get_stages(project.id)[0]

    service_stack["stage_service"].complete_stage(first.id)
    stages = service_stack["stage_service"].get_stages(project.id)

    assert stages[0].status == StageStatus.DONE.value
    assert stages[0].completed_at is not None
    assert stages[1].status == StageStatus.ACTIVE.value


def test_task_done_sets_completed_at_and_updates_project_progress(service_stack):
    project = service_stack["project_service"].create_project("Görev Testi")
    task = service_stack["task_service"].create_task(project.id, "İlk görev")

    service_stack["task_service"].update_task(task.id, status=TaskStatus.DONE.value)
    updated = service_stack["task_service"].get_task(task.id)
    project = service_stack["project_service"].get_project(project.id)

    assert updated.completed_at is not None
    assert project.progress_percent == 100


def test_checklist_completion_contributes_to_project_progress(service_stack):
    project = service_stack["project_service"].create_project("Checklist Testi")
    task = service_stack["task_service"].create_task(project.id, "Kontrollü görev")
    first = service_stack["task_service"].add_checklist_item(task.id, "Bir")
    service_stack["task_service"].add_checklist_item(task.id, "İki")

    service_stack["task_service"].toggle_checklist_item(first.id)
    project = service_stack["project_service"].get_project(project.id)

    assert project.progress_percent == 50


def test_export_uses_existing_idea_fields(service_stack, tmp_path):
    service_stack["idea_service"].create_idea(
        "Export fikri",
        problem="Sorun",
        solution="Çözüm",
        notes="Not",
    )
    target = tmp_path / "export.json"

    ExportService(service_stack["db"]).export_to_json(str(target))

    payload = json.loads(target.read_text(encoding="utf-8"))
    idea = payload["ideas"][0]
    assert idea["problem"] == "Sorun"
    assert idea["solution"] == "Çözüm"
    assert idea["notes"] == "Not"
    assert "description" not in idea


def test_old_database_migration_adds_parent_task_id_column():
    DatabaseManager._instance = None
    db = DatabaseManager.instance("sqlite:///:memory:")
    with db.engine.begin() as conn:
        conn.execute(text("CREATE TABLE schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"))
        conn.execute(text("INSERT INTO schema_migrations(version) VALUES ('001_create_metadata_tables')"))
        conn.execute(text("INSERT INTO schema_migrations(version) VALUES ('002_add_mvp_columns')"))
        conn.execute(text("INSERT INTO schema_migrations(version) VALUES ('003_normalize_enums_and_seed_workflow')"))
        conn.execute(text("CREATE TABLE tasks (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, title TEXT NOT NULL)"))

    db.run_migrations()
    columns = {column["name"] for column in inspect(db.engine).get_columns("tasks")}

    assert "parent_task_id" in columns


def test_task_hierarchy_validates_parent_project_and_cycles(service_stack):
    first = service_stack["project_service"].create_project("Birinci")
    second = service_stack["project_service"].create_project("İkinci")
    parent = service_stack["task_service"].create_task(first.id, "Modül", task_type=TaskType.GROUP.value)
    child = service_stack["task_service"].create_task(first.id, "Alt görev", parent_task_id=parent.id)
    other_project_task = service_stack["task_service"].create_task(second.id, "Başka proje")

    with pytest.raises(TaskHierarchyError):
        service_stack["task_service"].create_task(first.id, "Yanlış parent", parent_task_id=other_project_task.id)

    with pytest.raises(TaskHierarchyError):
        service_stack["task_service"].move_task(parent.id, child.id, 0)


def test_hierarchy_rollup_sets_parent_status_and_project_progress(service_stack):
    project = service_stack["project_service"].create_project("WBS")
    parent = service_stack["task_service"].create_task(project.id, "Ekran", task_type=TaskType.GROUP.value)
    child = service_stack["task_service"].create_task(project.id, "Buton", parent_task_id=parent.id)

    service_stack["task_service"].update_task(child.id, status=TaskStatus.DONE.value)
    updated_parent = service_stack["task_service"].get_task(parent.id)
    updated_project = service_stack["project_service"].get_project(project.id)

    assert updated_parent.status == TaskStatus.DONE.value
    assert updated_project.progress_percent == 100

    service_stack["task_service"].update_task(child.id, status=TaskStatus.TODO.value)
    reopened_parent = service_stack["task_service"].get_task(parent.id)
    reopened_project = service_stack["project_service"].get_project(project.id)

    assert reopened_parent.status == TaskStatus.TODO.value
    assert reopened_project.progress_percent == 0


def test_descendant_count_and_parent_delete_cascade(service_stack):
    project = service_stack["project_service"].create_project("Silme")
    parent = service_stack["task_service"].create_task(project.id, "Üst", task_type=TaskType.GROUP.value)
    child = service_stack["task_service"].create_task(project.id, "Alt", parent_task_id=parent.id)
    service_stack["task_service"].create_task(project.id, "Alt alt", parent_task_id=child.id)

    assert service_stack["task_service"].get_descendant_count(parent.id) == 2

    service_stack["task_service"].delete_task(parent.id)

    assert service_stack["task_service"].get_tasks(project.id) == []


def test_project_repository_pagination(service_stack):
    for index in range(5):
        service_stack["project_service"].create_project(f"Sayfa {index}")

    page = service_stack["project_service"].get_all_projects(limit=2, offset=1)

    assert len(page) == 2


def test_performance_index_migration_is_idempotent(service_stack):
    db = service_stack["db"]

    db.run_migrations()
    db.run_migrations()

    index_names = {
        index["name"]
        for table_name in ("tasks", "projects", "ideas")
        for index in inspect(db.engine).get_indexes(table_name)
    }
    assert "idx_tasks_status" in index_names
    assert "idx_tasks_priority" in index_names
    assert "idx_tasks_task_type" in index_names
    assert "idx_projects_status" in index_names
    assert "idx_projects_is_archived" in index_names
    assert "idx_ideas_status" in index_names


def test_project_auto_completed_when_all_stages_completed(service_stack):
    project = service_stack["project_service"].create_project("Otomatik Tamamlama Testi")
    stages = service_stack["stage_service"].get_stages(project.id)
    assert len(stages) > 0

    # Tüm aşamaları sırasıyla tamamla
    for _ in range(len(stages)):
        current_stages = service_stack["stage_service"].get_stages(project.id)
        active_stage = next(s for s in current_stages if s.status == "ACTIVE")
        service_stack["stage_service"].complete_stage(active_stage.id)

    # Tüm aşamaların DONE olduğunu doğrula
    updated_stages = service_stack["stage_service"].get_stages(project.id)
    assert all(s.status == "DONE" for s in updated_stages)

    # Projenin otomatik olarak COMPLETED olduğunu doğrula
    updated_project = service_stack["project_service"].get_project(project.id)
    assert updated_project.status == "COMPLETED"
