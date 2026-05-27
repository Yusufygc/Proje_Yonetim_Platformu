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
from domain.enums.project_status import ProjectStatus
from domain.models.project import Project
from infrastructure.repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)

_MAX_TITLE_LEN = 255
_MAX_SHORT_DESC_LEN = 500
_OPTIONAL_FIELDS = ("short_description", "github_url", "demo_url", "project_type", "full_description", "problem_statement", "target_outcome")


class ProjectService:
    """Proje oluşturma, güncelleme ve silme iş kurallarını yönetir."""

    def __init__(self, repository: ProjectRepository) -> None:
        self._repo = repository

    def get_all_projects(self, include_archived: bool = False) -> list[Project]:
        return self._repo.get_all(include_archived=include_archived)

    def get_project(self, project_id: int) -> Project:
        project = self._repo.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        return project

    def create_project(self, title: str, **kwargs: Any) -> Project:
        self._validate_title(title)
        self._validate_optional_fields(kwargs)
        data: dict[str, Any] = {
            "title": title.strip(),
            "slug": self._build_unique_slug(title),
            "status": kwargs.get("status", ProjectStatus.PLANNED.value),
            "priority": kwargs.get("priority", Priority.MEDIUM.value),
        }
        for key in _OPTIONAL_FIELDS:
            if kwargs.get(key) is not None:
                data[key] = kwargs[key]
        project = Project(**data)
        created = self._repo.create(project)
        logger.info("Yeni proje oluşturuldu: id=%d title='%s'", created.id, created.title)
        return created

    def update_project(self, project_id: int, **kwargs: Any) -> Project:
        project = self.get_project(project_id)
        if "title" in kwargs:
            self._validate_title(kwargs["title"])
            kwargs["title"] = kwargs["title"].strip()
        self._validate_optional_fields(kwargs)
        for key, value in kwargs.items():
            setattr(project, key, value)
        updated = self._repo.update(project)
        logger.info("Proje güncellendi: id=%d", project_id)
        return updated

    def archive_project(self, project_id: int) -> None:
        self.get_project(project_id)
        self._repo.set_archived(project_id, archived=True)
        logger.info("Proje arşivlendi: id=%d", project_id)

    def delete_project(self, project_id: int) -> None:
        self.get_project(project_id)
        self._repo.delete(project_id)
        logger.info("Proje silindi: id=%d", project_id)

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
