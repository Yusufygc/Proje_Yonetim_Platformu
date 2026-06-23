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
from domain.enums.project_status import ProjectStatus
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.stage_repository import StageRepository
from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository

logger = logging.getLogger(__name__)

# İlk aşama ACTIVE, geri kalanlar NOT_STARTED olarak başlar
DEFAULT_STAGES: list[dict] = [
    {"name": "Fikir", "description": "Fikir ve ihtiyaç netleştirme", "color": "#6366F1"},
    {"name": "Analiz", "description": "Kapsam, problem ve çözüm analizi", "color": "#0EA5E9"},
    {"name": "Tasarım", "description": "Mimari ve UI/UX tasarımı", "color": "#8B5CF6"},
    {"name": "Geliştirme", "description": "Kodlama ve implementasyon", "color": "#22C55E"},
    {"name": "Test", "description": "Test ve kalite güvencesi", "color": "#F59E0B"},
    {"name": "Yayın", "description": "Yayına alma ve paketleme", "color": "#EF4444"},
    {"name": "Bakım", "description": "İyileştirme ve takip", "color": "#14B8A6"},
    {"name": "Tamamlandı", "description": "Proje kapanışı", "color": "#64748B"},
]


class StageService:
    """Proje aşaması oluşturma, tamamlama ve aktivasyon iş kurallarını yönetir."""

    def __init__(
        self,
        repository: StageRepository,
        workflow_repository: WorkflowStageRepository | None = None,
        activity_log_repository: ActivityLogRepository | None = None,
        project_repository: ProjectRepository | None = None,
    ) -> None:
        self._repo = repository
        self._workflow_repo = workflow_repository
        self._activity_logs = activity_log_repository
        self._project_repo = project_repository

    def get_stages(self, project_id: int) -> list[ProjectStage]:
        return self._repo.get_by_project(project_id)

    def get_stage(self, stage_id: int) -> ProjectStage:
        stage = self._repo.get_by_id(stage_id)
        if stage is None:
            raise StageNotFoundError(stage_id)
        return stage

    def create_default_stages(self, project_id: int) -> list[ProjectStage]:
        """Yeni proje için varsayılan aşamaları oluşturur; ilk aşama aktif başlar."""
        existing = self._repo.get_by_project(project_id)
        if existing:
            return existing

        templates = DEFAULT_STAGES
        if self._workflow_repo is not None:
            workflow_stages = self._workflow_repo.get_defaults()
            if workflow_stages:
                templates = [
                    {
                        "name": stage.name,
                        "description": stage.description,
                        "color": DEFAULT_STAGES[i % len(DEFAULT_STAGES)]["color"],
                    }
                    for i, stage in enumerate(workflow_stages)
                ]

        stages = []
        for i, template in enumerate(templates):
            status = StageStatus.ACTIVE.value if i == 0 else StageStatus.NOT_STARTED.value
            stages.append(
                ProjectStage(
                    project_id=project_id,
                    name=template["name"],
                    description=template["description"],
                    color=template["color"],
                    order_index=i,
                    status=status,
                    started_at=datetime.now(timezone.utc) if i == 0 else None,
                )
            )
        created = self._repo.create_many(stages)
        if self._activity_logs is not None:
            self._activity_logs.create(
                project_id=project_id,
                action="STAGES_CREATED",
                summary="Varsayılan süreç aşamaları oluşturuldu.",
                entity_type="project",
                entity_id=project_id,
            )
        logger.info("Proje %d için %d varsayılan aşama oluşturuldu.", project_id, len(created))
        return created

    def complete_stage(self, stage_id: int) -> ProjectStage:
        """Aktif aşamayı tamamlar; yalnızca ACTIVE durumdaki aşama tamamlanabilir."""
        stage = self.get_stage(stage_id)
        if stage.status != StageStatus.ACTIVE.value:
            raise StageValidationError("Yalnızca aktif aşama tamamlanabilir.")
        stage.status = StageStatus.DONE.value
        stage.completed_at = datetime.now(timezone.utc)
        updated = self._repo.update(stage)
        self._activate_next_stage(updated)
        self._check_and_complete_project(updated.project_id)
        if self._activity_logs is not None:
            self._activity_logs.create(
                project_id=updated.project_id,
                action="STAGE_COMPLETED",
                summary=f"{updated.name} aşaması tamamlandı.",
                entity_type="stage",
                entity_id=updated.id,
            )
        logger.info("Aşama tamamlandı: id=%d name='%s'", stage_id, stage.name)
        return updated

    def activate_stage(self, stage_id: int) -> ProjectStage:
        """Bekleyen aşamayı aktif eder; aynı projede zaten aktif aşama varsa hata verir."""
        stage = self.get_stage(stage_id)
        if stage.status != StageStatus.NOT_STARTED.value:
            raise StageValidationError("Yalnızca bekleyen aşama aktif edilebilir.")
        existing = self._repo.get_by_project(stage.project_id)
        if any(s.status == StageStatus.ACTIVE.value for s in existing):
            raise StageValidationError("Projenin zaten aktif bir aşaması var.")
        stage.status = StageStatus.ACTIVE.value
        stage.started_at = datetime.now(timezone.utc)
        updated = self._repo.update(stage)
        if self._activity_logs is not None:
            self._activity_logs.create(
                project_id=updated.project_id,
                action="STAGE_ACTIVATED",
                summary=f"{updated.name} aşaması aktif edildi.",
                entity_type="stage",
                entity_id=updated.id,
            )
        logger.info("Aşama aktif edildi: id=%d name='%s'", stage_id, stage.name)
        return updated

    def _activate_next_stage(self, completed_stage: ProjectStage) -> None:
        stages = self._repo.get_by_project(completed_stage.project_id)
        for stage in stages:
            if stage.order_index > completed_stage.order_index and stage.status == StageStatus.NOT_STARTED.value:
                stage.status = StageStatus.ACTIVE.value
                stage.started_at = datetime.now(timezone.utc)
                self._repo.update(stage)
                if self._activity_logs is not None:
                    self._activity_logs.create(
                        project_id=stage.project_id,
                        action="STAGE_ACTIVATED",
                        summary=f"{stage.name} aşaması otomatik aktif edildi.",
                        entity_type="stage",
                        entity_id=stage.id,
                    )
                break

    def _check_and_complete_project(self, project_id: int) -> None:
        """Eğer projenin tüm aşamaları DONE veya SKIPPED ise projeyi otomatik olarak COMPLETED yapar."""
        if self._project_repo is None:
            return
        stages = self._repo.get_by_project(project_id)
        if not stages:
            return
        all_completed = all(
            s.status in {StageStatus.DONE.value, StageStatus.SKIPPED.value}
            for s in stages
        )
        if all_completed:
            project = self._project_repo.get_by_id(project_id)
            if project is not None and project.status != ProjectStatus.COMPLETED.value:
                project.status = ProjectStatus.COMPLETED.value
                self._project_repo.update(project)
                if self._activity_logs is not None:
                    self._activity_logs.create(
                        project_id=project_id,
                        action="PROJECT_COMPLETED",
                        summary="Tüm süreç aşamaları tamamlandığı için proje otomatik olarak tamamlandı durumuna getirildi.",
                        entity_type="project",
                        entity_id=project_id,
                    )
                logger.info("Tüm aşamaları tamamlanan proje otomatik tamamlandı olarak işaretlendi: id=%d", project_id)
