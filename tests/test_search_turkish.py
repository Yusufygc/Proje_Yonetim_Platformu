from __future__ import annotations

import pytest

from core.text_normalization import escape_like, normalize_search_text
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.project_tag_repository import ProjectTagRepository
from infrastructure.repositories.stage_repository import StageRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository
from services.project_service import ProjectService
from services.search_service import SearchService
from services.stage_service import StageService


@pytest.fixture()
def search_stack():
    DatabaseManager._instance = None
    db = DatabaseManager.instance("sqlite:///:memory:")
    db.run_migrations()
    activity = ActivityLogRepository(db)
    project_repo = ProjectRepository(db)
    stage_service = StageService(
        StageRepository(db), WorkflowStageRepository(db), activity, project_repository=project_repo
    )
    projects = ProjectService(project_repo, stage_service, activity, ProjectTagRepository(db), TaskRepository(db))
    return projects, SearchService(db)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("İSTANBUL", "istanbul"), ("ISPARTA", "isparta"), ("ışık", "işik"), ("ŞİŞLİ", "şişli"), (None, "")],
)
def test_normalize_search_text_when_turkish_letters_should_fold_case_and_dotted_i(raw, expected):
    assert normalize_search_text(raw) == expected


def test_escape_like_when_wildcards_present_should_escape_them():
    assert escape_like("100%_a\\b") == "100\\%\\_a\\\\b"


def test_search_all_when_query_uses_other_turkish_case_should_find_project(search_stack):
    projects, search = search_stack
    projects.create_project(title="Şişli Mağaza Projesi")
    projects.create_project(title="İzmir Ofis")

    assert [p["title"] for p in search.search_all("ŞİŞLİ")["projects"]] == ["Şişli Mağaza Projesi"]
    assert [p["title"] for p in search.search_all("izmir")["projects"]] == ["İzmir Ofis"]


def test_search_all_when_query_contains_like_wildcard_should_match_literally(search_stack):
    projects, search = search_stack
    projects.create_project(title="Yüzde 100% Hedef")
    projects.create_project(title="Yüzde 1000 Hedef")

    titles = [p["title"] for p in search.search_all("100%")["projects"]]

    assert titles == ["Yüzde 100% Hedef"]


def test_search_all_when_query_too_short_should_return_empty_groups(search_stack):
    _projects, search = search_stack

    assert search.search_all("a") == {"projects": [], "tasks": [], "ideas": []}
