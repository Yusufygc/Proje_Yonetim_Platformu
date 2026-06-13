from domain.models.decision_record import DecisionRecord
from infrastructure.repositories.base_repository import ProjectScopedRepository


class DecisionRepository(ProjectScopedRepository[DecisionRecord]):
    """Proje Kararları (DecisionRecord) için veri erişim katmanı."""

    model = DecisionRecord

    def _project_order(self) -> tuple:
        return (DecisionRecord.created_at.desc(),)
