"""Attachment veri erişim katmanı."""
from __future__ import annotations

from domain.models.attachment import Attachment
from infrastructure.repositories.base_repository import ProjectScopedRepository


class AttachmentRepository(ProjectScopedRepository[Attachment]):
    model = Attachment

    def _project_order(self) -> tuple:
        return (Attachment.display_order, Attachment.created_at.desc())
