"""Analitik genel bakış verileri: ısı haritası, durum dağılımı, açılan/biten akışı, ortalama süre ve hafta etiketi."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

import pytest

from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.project_tag_repository import ProjectTagRepository
from infrastructure.repositories.stage_repository import StageRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository
from services import analytics_overview
from services.analytics_service import AnalyticsService, _fmt_weekly
from services.project_service import ProjectService
from services.stage_service import StageService
from services.task_service import TaskService


@pytest.fixture()
def stack() -> dict[str, Any]:
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
        "project": projects.create_project(title="Analitik"),
        "other": projects.create_project(title="Diğer"),
        "tasks": TaskService(task_repo, projects, activity),
    }


def _finish(stack: dict[str, Any], task_id: int, created: datetime, completed: datetime) -> None:
    """Görevi bitmiş yapar ve oluşturulma/tamamlanma zamanlarını elle ayarlar."""
    stack["tasks"].update_task(task_id, status="DONE")
    with stack["db"].session() as sess:
        task = sess.get(Task, task_id)
        task.created_at = created
        task.completed_at = completed


def _utc(day: date, hour: int = 12) -> datetime:
    return datetime(day.year, day.month, day.day, hour, tzinfo=timezone.utc)


def test_fmt_weekly_when_week_key_should_show_number_and_hafta() -> None:
    assert _fmt_weekly("2026-W40") == "40.Hafta"
    assert _fmt_weekly("2026-W05") == "5.Hafta"


def test_status_distribution_when_tasks_in_various_states_should_count_each(stack: dict[str, Any]) -> None:
    a = stack["tasks"].create_task(stack["project"].id, "A")
    stack["tasks"].create_task(stack["project"].id, "B")
    stack["tasks"].create_task(stack["other"].id, "C")
    stack["tasks"].update_task(a.id, status="IN_PROGRESS")

    with stack["db"].session() as sess:
        everything = analytics_overview.status_distribution(sess, None)
        only_project = analytics_overview.status_distribution(sess, stack["project"].id)

    assert everything == {"TODO": 2, "IN_PROGRESS": 1}
    assert only_project == {"TODO": 1, "IN_PROGRESS": 1}


def test_activity_heatmap_when_tasks_done_should_fill_cells_and_flag_future(stack: dict[str, Any]) -> None:
    today = datetime.now(timezone.utc).date()
    for index in range(2):
        task = stack["tasks"].create_task(stack["project"].id, f"Bugün {index}")
        _finish(stack, task.id, _utc(today) - timedelta(days=1), _utc(today))

    with stack["db"].session() as sess:
        heatmap = analytics_overview.activity_heatmap(sess, None, today)

    cells = heatmap["cells"]
    today_cell = next(c for c in cells if c["date"] == today.isoformat())
    assert len(cells) == 84
    assert today_cell["count"] == 2
    assert today_cell["row"] == today.weekday()
    assert today_cell["col"] == 11
    assert heatmap["max"] == 2
    assert all(c["future"] for c in cells if c["date"] > today.isoformat())


def test_avg_completion_days_when_tasks_took_two_and_four_days_should_return_three(stack: dict[str, Any]) -> None:
    today = datetime.now(timezone.utc).date()
    for days in (2, 4):
        task = stack["tasks"].create_task(stack["project"].id, f"{days} gün")
        _finish(stack, task.id, _utc(today) - timedelta(days=days), _utc(today))
    start = _utc(today) - timedelta(days=7)
    end = _utc(today) + timedelta(days=1)

    with stack["db"].session() as sess:
        average = analytics_overview.avg_completion_days(sess, start, end, None)
        empty = analytics_overview.avg_completion_days(sess, start, end, stack["other"].id)

    assert average == 3.0
    assert empty == 0.0


def test_get_analytics_when_tasks_created_and_done_should_report_flow_and_new_kpi(stack: dict[str, Any]) -> None:
    today = datetime.now(timezone.utc).date()
    done = stack["tasks"].create_task(stack["project"].id, "Biten")
    stack["tasks"].create_task(stack["project"].id, "Açık")
    _finish(stack, done.id, _utc(today) - timedelta(days=1), _utc(today))

    analytics = AnalyticsService(stack["db"]).get_analytics("daily", None)

    label, created, completed = analytics["flow_series"][-1]
    assert label == f"{today.day} {['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'][today.month - 1]}"
    assert completed == 1
    assert created >= 1
    assert analytics["kpis"]["avg_completion_days"] == 1.0
    assert "on_time_rate" not in analytics["kpis"]
    assert analytics["status_distribution"]["DONE"] == 1
    assert len(analytics["heatmap"]["cells"]) == 84
