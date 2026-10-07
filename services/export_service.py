"""
Export Service - Uygulama verilerinin JSON olarak dışa aktarılması.
"""
import json
import logging
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from domain.models.activity_log import ActivityLog
from domain.models.attachment import Attachment
from domain.models.checklist_item import ChecklistItem
from domain.models.decision_record import DecisionRecord
from domain.models.idea import Idea
from domain.models.memo import Memo
from domain.models.note import Note
from domain.models.project import Project
from domain.models.project_idea import ProjectIdea
from domain.models.project_stage import ProjectStage
from domain.models.project_tag import ProjectTag
from domain.models.resource import Resource
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

EXPORT_FORMAT_VERSION = 2

# Proje altında listelenen tablolar: JSON anahtarı -> model. Yeni tablo eklemek tek satırdır.
_PROJECT_CHILDREN: dict[str, type] = {
    "stages": ProjectStage,
    "tasks": Task,
    "decisions": DecisionRecord,
    "notes": Note,
    "resources": Resource,
    "attachments": Attachment,
    "tags": ProjectTag,
    "activity_logs": ActivityLog,
}


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _row_to_dict(row: Any) -> dict[str, Any]:
    """Modelin tüm kolonlarını yazar; yeni eklenen kolonlar da kendiliğinden dışa aktarılır."""
    columns = inspect(type(row)).mapper.column_attrs
    return {column.key: _to_jsonable(getattr(row, column.key)) for column in columns}


def _all_rows(sess: Session, model: type) -> list[dict[str, Any]]:
    return [_row_to_dict(row) for row in sess.scalars(select(model))]


def _group_by(rows: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return grouped


def _attach_checklists(tasks: list[dict[str, Any]], checklist_rows: list[dict[str, Any]]) -> None:
    by_task = _group_by(checklist_rows, "task_id")
    for task in tasks:
        task["checklist_items"] = by_task.get(task["id"], [])


def _build_projects(sess: Session) -> list[dict[str, Any]]:
    children = {name: _group_by(_all_rows(sess, model), "project_id") for name, model in _PROJECT_CHILDREN.items()}
    checklists = _all_rows(sess, ChecklistItem)
    projects = _all_rows(sess, Project)
    for project in projects:
        for name, grouped in children.items():
            project[name] = grouped.get(project["id"], [])
        _attach_checklists(project["tasks"], checklists)
    return projects


class ExportService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def export_to_json(self, target_path: str) -> None:
        """Tüm tabloları (projeler ve alt kayıtları, fikirler, memolar) JSON olarak yazar."""
        with self._db.session() as sess:
            export_data = {
                "format_version": EXPORT_FORMAT_VERSION,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "projects": _build_projects(sess),
                "ideas": _all_rows(sess, Idea),
                "project_ideas": _all_rows(sess, ProjectIdea),
                "memos": _all_rows(sess, Memo),
            }

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        logger.info("JSON export completed: %s", Path(target_path))
