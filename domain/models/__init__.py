"""ORM model imports.

Importing this package registers every model with SQLAlchemy metadata before
table creation or migrations run.
"""

from domain.models.activity_log import ActivityLog
from domain.models.memo import Memo
from domain.models.attachment import Attachment
from domain.models.checklist_item import ChecklistItem
from domain.models.decision_record import DecisionRecord
from domain.models.idea import Idea
from domain.models.note import Note
from domain.models.project import Project
from domain.models.project_idea import ProjectIdea
from domain.models.project_stage import ProjectStage
from domain.models.project_tag import ProjectTag
from domain.models.resource import Resource
from domain.models.setting import Setting
from domain.models.task import Task
from domain.models.workflow_stage import WorkflowStage

__all__ = [
    "ActivityLog",
    "Attachment",
    "Memo",
    "ChecklistItem",
    "DecisionRecord",
    "Idea",
    "Note",
    "Project",
    "ProjectIdea",
    "ProjectStage",
    "ProjectTag",
    "Resource",
    "Setting",
    "Task",
    "WorkflowStage",
]
