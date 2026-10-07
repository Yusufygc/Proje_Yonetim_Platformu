"""Karar, kaynak ve pano servisleri ile ilgili controller hata yollarının testleri."""
from __future__ import annotations

import pytest

from controllers.decision_controller import DecisionController
from controllers.note_controller import NoteController
from controllers.resource_controller import ResourceController
from domain.enums.decision_status import DecisionStatus
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.decision_repository import DecisionRepository
from infrastructure.repositories.note_repository import NoteRepository
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.project_tag_repository import ProjectTagRepository
from infrastructure.repositories.resource_repository import ResourceRepository
from infrastructure.repositories.stage_repository import StageRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository
from services.dashboard_service import DashboardService
from services.decision_service import DecisionService
from services.note_service import NoteService
from services.project_service import ProjectService
from services.resource_service import ResourceService
from services.stage_service import StageService
from services.task_service import TaskService


@pytest.fixture()
def stack():
    DatabaseManager._instance = None
    db = DatabaseManager.instance("sqlite:///:memory:")
    db.run_migrations()
    activity = ActivityLogRepository(db)
    project_repo = ProjectRepository(db)
    task_repo = TaskRepository(db)
    stages = StageService(StageRepository(db), WorkflowStageRepository(db), activity, project_repository=project_repo)
    projects = ProjectService(project_repo, stages, activity, ProjectTagRepository(db), task_repo)
    return {
        "db": db,
        "project": projects.create_project(title="Alt öğe projesi"),
        "projects": projects,
        "tasks": TaskService(task_repo, projects, activity),
        "decisions": DecisionService(DecisionRepository(db)),
        "resources": ResourceService(ResourceRepository(db)),
        "notes": NoteService(NoteRepository(db)),
    }


def test_create_decision_when_decision_text_blank_should_raise_value_error(stack):
    with pytest.raises(ValueError):
        stack["decisions"].create_decision(stack["project"].id, "Başlık", "   ")


def test_delete_decision_when_called_should_cancel_instead_of_removing(stack):
    decision = stack["decisions"].create_decision(stack["project"].id, "Mimari", "Katmanlı yapı")

    stack["decisions"].delete_decision(decision.id)

    kept = stack["decisions"].get_project_decisions(stack["project"].id)
    assert [d.status for d in kept] == [DecisionStatus.CANCELLED.value]


def test_supersede_decision_when_replaced_should_link_new_decision(stack):
    old = stack["decisions"].create_decision(stack["project"].id, "Eski", "A")
    new = stack["decisions"].create_decision(stack["project"].id, "Yeni", "B")

    stack["decisions"].supersede_decision(old.id, new.id)

    updated = stack["decisions"].get_decision(old.id)
    assert updated.status == DecisionStatus.SUPERSEDED.value
    assert updated.superseded_by_decision_id == new.id


def test_create_resource_when_title_blank_should_use_url_as_title(stack):
    resource = stack["resources"].create_resource(stack["project"].id, "  ", " https://example.com ")

    assert resource.title == "https://example.com"
    assert resource.url == "https://example.com"


def test_update_resource_when_url_blank_should_raise_value_error(stack):
    resource = stack["resources"].create_resource(stack["project"].id, "Doküman", "https://example.com")

    with pytest.raises(ValueError):
        stack["resources"].update_resource(resource.id, url="  ")


def test_get_dashboard_stats_when_data_exists_should_count_and_list_entries(stack):
    stack["tasks"].create_task(stack["project"].id, "Acil", priority="CRITICAL")
    stack["tasks"].create_task(stack["project"].id, "Sıradan", priority="LOW")

    stats = DashboardService(stack["db"]).get_dashboard_stats()

    assert stats["total_tasks"] == 2
    assert stats["open_tasks"] == 2
    assert [t["title"] for t in stats["high_priority_tasks"]] == ["Acil"]


def test_note_controller_when_body_blank_should_emit_error_instead_of_creating(stack):
    controller = NoteController(stack["notes"])
    errors: list[str] = []
    created: list[object] = []
    controller.error_occurred.connect(errors.append)
    controller.note_created.connect(created.append)

    controller.create_note(stack["project"].id, "Başlık", "  ")

    assert len(errors) == 1
    assert created == []


def test_decision_controller_when_title_blank_should_emit_error(stack):
    controller = DecisionController(stack["decisions"])
    errors: list[str] = []
    controller.error_occurred.connect(errors.append)

    controller.create_decision(stack["project"].id, "", "Karar")

    assert len(errors) == 1


def test_resource_controller_when_url_blank_should_emit_error(stack):
    controller = ResourceController(stack["resources"])
    errors: list[str] = []
    controller.error_occurred.connect(errors.append)

    controller.create_resource(stack["project"].id, "Ad", "")

    assert len(errors) == 1
