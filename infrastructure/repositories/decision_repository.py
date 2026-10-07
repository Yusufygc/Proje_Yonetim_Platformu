from __future__ import annotations

from typing import Any

from domain.models.decision_record import DecisionRecord
from infrastructure.repositories.base_repository import ProjectScopedRepository


class DecisionRepository(ProjectScopedRepository[DecisionRecord]):
    """Proje Kararları (DecisionRecord) için veri erişim katmanı."""

    model = DecisionRecord

    def _project_order(self) -> tuple[Any, ...]:
        return (DecisionRecord.created_at.desc(),)
