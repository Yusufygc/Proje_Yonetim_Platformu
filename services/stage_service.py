"""
Proje aşaması iş kuralları.
Varsayılan aşama oluşturma, tamamlama ve aktivasyon burada yönetilir.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from core.exceptions.stage_exceptions import StageNotFoundError, StageValidationError
from domain.enums.stage_status import StageStatus
from domain.models.project_stage import ProjectStage
from infrastructure.repositories.stage_repository import StageRepository

logger = logging.getLogger(__name__)

# İlk aşama ACTIVE, geri kalanlar PENDING olarak başlar
DEFAULT_STAGES: list[dict] = [
    {"name": "Planlama", "description": "Proje hedefleri ve kapsam belirleme", "color": "#6366F1"},
    {"name": "Tasarım", "description": "Mimari ve UI/UX tasarımı", "color": "#8B5CF6"},
    {"name": "Geliştirme", "description": "Kodlama ve implementasyon", "color": "#22C55E"},
    {"name": "Test", "description": "Test ve kalite güvencesi", "color": "#F59E0B"},
    {"name": "Yayınlama", "description": "Deployment ve yayına alma", "color": "#EF4444"},
]


class StageService:
    """Proje aşaması oluşturma, tamamlama ve aktivasyon iş kurallarını yönetir."""

    def __init__(self, repository: StageRepository) -> None:
        self._repo = repository

    def get_stages(self, project_id: int) -> list[ProjectStage]:
        return self._repo.get_by_project(project_id)

    def get_stage(self, stage_id: int) -> ProjectStage:
        stage = self._repo.get_by_id(stage_id)
        if stage is None:
            raise StageNotFoundError(stage_id)
        return stage

    def create_default_stages(self, project_id: int) -> list[ProjectStage]:
        """Yeni proje için varsayılan aşamaları oluşturur; ilk aşama aktif başlar."""
        stages = []
        for i, template in enumerate(DEFAULT_STAGES):
            status = StageStatus.ACTIVE.value if i == 0 else StageStatus.PENDING.value
            stages.append(
                ProjectStage(
                    project_id=project_id,
                    name=template["name"],
                    description=template["description"],
                    color=template["color"],
                    order_index=i,
                    status=status,
                )
            )
        created = self._repo.create_many(stages)
        logger.info("Proje %d için %d varsayılan aşama oluşturuldu.", project_id, len(created))
        return created

    def complete_stage(self, stage_id: int) -> ProjectStage:
        """Aktif aşamayı tamamlar; yalnızca ACTIVE durumdaki aşama tamamlanabilir."""
        stage = self.get_stage(stage_id)
        if stage.status != StageStatus.ACTIVE.value:
            raise StageValidationError("Yalnızca aktif aşama tamamlanabilir.")
        stage.status = StageStatus.COMPLETED.value
        stage.completed_at = datetime.now(timezone.utc)
        updated = self._repo.update(stage)
        logger.info("Aşama tamamlandı: id=%d name='%s'", stage_id, stage.name)
        return updated

    def activate_stage(self, stage_id: int) -> ProjectStage:
        """Bekleyen aşamayı aktif eder; aynı projede zaten aktif aşama varsa hata verir."""
        stage = self.get_stage(stage_id)
        if stage.status != StageStatus.PENDING.value:
            raise StageValidationError("Yalnızca bekleyen aşama aktif edilebilir.")
        existing = self._repo.get_by_project(stage.project_id)
        if any(s.status == StageStatus.ACTIVE.value for s in existing):
            raise StageValidationError("Projenin zaten aktif bir aşaması var.")
        stage.status = StageStatus.ACTIVE.value
        updated = self._repo.update(stage)
        logger.info("Aşama aktif edildi: id=%d name='%s'", stage_id, stage.name)
        return updated
