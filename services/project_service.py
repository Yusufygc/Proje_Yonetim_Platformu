"""
Proje iş kurallarını uygulayan servis katmanı.
Repository ile UI arasındaki köprü; validasyon ve slug üretimi burada yapılır.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from core.exceptions.project_exceptions import ProjectNotFoundError, ProjectValidationError
from domain.enums.priority import Priority
from domain.enums.project_health import ProjectHealth
from domain.enums.project_status import ProjectStatus
from domain.models.activity_log import ActivityLog
from domain.models.attachment import Attachment
from domain.models.project import Project
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.attachment_repository import AttachmentRepository
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.project_tag_repository import ProjectTagRepository
from infrastructure.repositories.task_repository import TaskRepository
from services.stage_service import StageService

logger = logging.getLogger(__name__)

_MAX_TITLE_LEN = 255
_MAX_SHORT_DESC_LEN = 500
_OPTIONAL_FIELDS = (
    "short_description",
    "full_description",
    "problem_statement",
    "target_outcome",
    "project_type",
    "status",
    "priority",
    "health",
    "progress_percent",
    "manual_progress_percent",
    "github_url",
    "demo_url",
    "docs_url",
    "start_date",
    "target_end_date",
    "completed_at",
    "is_featured",
    "is_archived",
    "display_order",
)


class ProjectService:
    """Proje oluşturma, güncelleme ve silme iş kurallarını yönetir."""

    def __init__(
        self,
        repository: ProjectRepository,
        stage_service: StageService | None = None,
        activity_log_repository: ActivityLogRepository | None = None,
        tag_repository: ProjectTagRepository | None = None,
        task_repository: TaskRepository | None = None,
        attachment_repository: AttachmentRepository | None = None,
    ) -> None:
        self._repo = repository
        self._stage_service = stage_service
        self._activity_logs = activity_log_repository
        self._tag_repo = tag_repository
        self._task_repo = task_repository
        self._attachment_repo = attachment_repository

    def get_all_projects(
        self,
        include_archived: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Project]:
        return self._repo.get_all(include_archived=include_archived, limit=limit, offset=offset)

    def get_project(self, project_id: int) -> Project:
        project = self._repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        return project

    def get_activity_logs(self, project_id: int) -> list[ActivityLog]:
        if self._activity_logs is None:
            return []
        return self._activity_logs.get_by_project(project_id)

    def get_attachments(self, project_id: int) -> list[Attachment]:
        if self._attachment_repo is None:
            return []
        return self._attachment_repo.get_by_project(project_id)

    def create_attachment(self, attachment: Attachment) -> Attachment:
        if self._attachment_repo is None:
            raise RuntimeError("Attachment repository not configured")
        return self._attachment_repo.create(attachment)

    def create_project(self, title: str, **kwargs: Any) -> Project:
        self._validate_title(title)
        self._validate_optional_fields(kwargs)
        status = kwargs.get("status", ProjectStatus.PLANNED.value)
        health = kwargs.get("health", ProjectHealth.UNKNOWN.value)
        if status == ProjectStatus.BLOCKED.value:
            health = ProjectHealth.BLOCKED.value
            kwargs["health"] = health
        data: dict[str, Any] = {
            "title": title.strip(),
            "slug": self._build_unique_slug(title),
            "status": status,
            "priority": kwargs.get("priority", Priority.MEDIUM.value),
            "health": health,
        }
        tags = list(kwargs.pop("tags", []) or [])
        for key in _OPTIONAL_FIELDS:
            if kwargs.get(key) is not None:
                data[key] = kwargs[key]
        project = Project(**data)
        created = self._repo.create(project)
        try:
            if self._stage_service is not None:
                self._stage_service.create_default_stages(created.id)
            if self._tag_repo is not None and tags:
                self._tag_repo.replace_for_project(created.id, tags)
            if self._activity_logs is not None:
                self._activity_logs.create(
                    project_id=created.id,
                    action="PROJECT_CREATED",
                    summary=f"{created.title} projesi oluşturuldu.",
                    entity_type="project",
                    entity_id=created.id,
                )
        except Exception as exc:
            # Proje zaten kaydedildi; ek kurulum hatası oluşsa da signal'in emitlenmesini engelleme
            logger.warning(
                "Proje '%s' (id=%d) oluşturuldu ancak ek kurulum tamamlanamadı: %s",
                created.title, created.id, exc,
            )
        logger.info("Yeni proje oluşturuldu: id=%d title='%s'", created.id, created.title)
        return created

    def update_project(self, project_id: int, **kwargs: Any) -> Project:
        project = self.get_project(project_id)
        tags = kwargs.pop("tags", None)
        if "title" in kwargs:
            self._validate_title(kwargs["title"])
            kwargs["title"] = kwargs["title"].strip()
        self._validate_optional_fields(kwargs)
        if kwargs.get("status") == ProjectStatus.BLOCKED.value:
            kwargs["health"] = ProjectHealth.BLOCKED.value
        for key, value in kwargs.items():
            setattr(project, key, value)
        updated = self._repo.update(project)
        if self._tag_repo is not None and tags is not None:
            self._tag_repo.replace_for_project(project_id, list(tags))
        if self._activity_logs is not None:
            self._activity_logs.create(
                project_id=project_id,
                action="PROJECT_UPDATED",
                summary=f"{updated.title} projesi güncellendi.",
                entity_type="project",
                entity_id=project_id,
            )
        logger.info("Proje güncellendi: id=%d", project_id)
        return updated

    def archive_project(self, project_id: int) -> None:
        self.get_project(project_id)
        self._repo.set_archived(project_id, archived=True)
        if self._activity_logs is not None:
            self._activity_logs.create(
                project_id=project_id,
                action="PROJECT_ARCHIVED",
                summary="Proje arşivlendi.",
                entity_type="project",
                entity_id=project_id,
            )
        logger.info("Proje arşivlendi: id=%d", project_id)

    def restore_archived_project(self, project_id: int) -> None:
        self.get_project(project_id)
        self._repo.set_archived(project_id, archived=False)
        if self._activity_logs is not None:
            self._activity_logs.create(
                project_id=project_id,
                action="PROJECT_RESTORED",
                summary="Proje arsivden geri alindi.",
                entity_type="project",
                entity_id=project_id,
            )
        logger.info("Proje arsivden geri alindi: id=%d", project_id)

    def delete_project(self, project_id: int) -> None:
        self.get_project(project_id)
        self._repo.delete(project_id)
        logger.info("Proje silindi: id=%d", project_id)

    def recalculate_progress(self, project_id: int) -> Project:
        """Görev tamamlanma oranından proje ilerlemesini günceller."""
        project = self.get_project(project_id)
        if project.manual_progress_percent is not None:
            project.progress_percent = project.manual_progress_percent
            return self._repo.update(project)
        if self._task_repo is None:
            return project
        project.progress_percent = self._task_repo.calculate_progress_percent(project_id)
        return self._repo.update(project)

    def _validate_title(self, title: str) -> None:
        if not title or not title.strip():
            raise ProjectValidationError("Proje başlığı boş olamaz.")
        if len(title.strip()) > _MAX_TITLE_LEN:
            raise ProjectValidationError(f"Proje başlığı {_MAX_TITLE_LEN} karakteri aşamaz.")

    def _validate_optional_fields(self, data: dict[str, Any]) -> None:
        short_desc = data.get("short_description")
        if short_desc and len(short_desc) > _MAX_SHORT_DESC_LEN:
            raise ProjectValidationError(f"Kısa açıklama {_MAX_SHORT_DESC_LEN} karakteri aşamaz.")

    def _build_unique_slug(self, title: str) -> str:
        slug = title.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        return slug.strip("-")
