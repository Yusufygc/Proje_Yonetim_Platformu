"""
DI kayıt sınıfları (registry).

DIContainer tek başına 40+ factory metodu barındırıyordu (god object);
katman başına bir registry'ye bölündü. Her registry kendi katmanının
nesnelerini @cached_property ile tembel (lazy) üretir — yeni modül
eklemek yalnızca ilgili registry'yi büyütür (Open/Closed).
"""
from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.analytics_controller import AnalyticsController
    from controllers.dashboard_controller import DashboardController
    from controllers.memo_controller import MemoController
    from infrastructure.repositories.memo_repository import MemoRepository
    from services.memo_service import MemoService
    from controllers.decision_controller import DecisionController
    from controllers.idea_controller import IdeaController
    from controllers.note_controller import NoteController
    from controllers.project_controller import ProjectController
    from controllers.resource_controller import ResourceController
    from controllers.search_controller import SearchController
    from controllers.settings_controller import SettingsController
    from controllers.stage_controller import StageController
    from controllers.task_controller import TaskController
    from core.events.event_bus import EventBus
    from infrastructure.database.db_manager import DatabaseManager
    from infrastructure.repositories.activity_log_repository import ActivityLogRepository
    from infrastructure.repositories.attachment_repository import AttachmentRepository
    from infrastructure.repositories.decision_repository import DecisionRepository
    from infrastructure.repositories.idea_repository import IdeaRepository
    from infrastructure.repositories.note_repository import NoteRepository
    from infrastructure.repositories.project_idea_repository import ProjectIdeaRepository
    from infrastructure.repositories.project_repository import ProjectRepository
    from infrastructure.repositories.project_tag_repository import ProjectTagRepository
    from infrastructure.repositories.resource_repository import ResourceRepository
    from infrastructure.repositories.stage_repository import StageRepository
    from infrastructure.repositories.task_repository import TaskRepository
    from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository
    from services.dashboard_service import DashboardService
    from services.decision_service import DecisionService
    from services.export_service import ExportService
    from services.idea_service import IdeaService
    from services.note_service import NoteService
    from services.project_service import ProjectService
    from services.resource_service import ResourceService
    from services.search_service import SearchService
    from services.stage_service import StageService
    from services.analytics_service import AnalyticsService
    from services.task_service import TaskService
    from services.speech.speech_to_text_service import SpeechToTextService


class RepositoryRegistry:
    """Veri erişim katmanı fabrikaları."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    @cached_property
    def activity_log(self) -> ActivityLogRepository:
        from infrastructure.repositories.activity_log_repository import ActivityLogRepository
        return ActivityLogRepository(db=self._db)

    @cached_property
    def workflow_stage(self) -> WorkflowStageRepository:
        from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository
        return WorkflowStageRepository(db=self._db)

    @cached_property
    def project_tag(self) -> ProjectTagRepository:
        from infrastructure.repositories.project_tag_repository import ProjectTagRepository
        return ProjectTagRepository(db=self._db)

    @cached_property
    def project_idea(self) -> ProjectIdeaRepository:
        from infrastructure.repositories.project_idea_repository import ProjectIdeaRepository
        return ProjectIdeaRepository(db=self._db)

    @cached_property
    def attachment(self) -> AttachmentRepository:
        from infrastructure.repositories.attachment_repository import AttachmentRepository
        return AttachmentRepository(db=self._db)

    @cached_property
    def stage(self) -> StageRepository:
        from infrastructure.repositories.stage_repository import StageRepository
        return StageRepository(db=self._db)

    @cached_property
    def task(self) -> TaskRepository:
        from infrastructure.repositories.task_repository import TaskRepository
        return TaskRepository(db=self._db)

    @cached_property
    def project(self) -> ProjectRepository:
        from infrastructure.repositories.project_repository import ProjectRepository
        return ProjectRepository(db=self._db)

    @cached_property
    def idea(self) -> IdeaRepository:
        from infrastructure.repositories.idea_repository import IdeaRepository
        return IdeaRepository(db=self._db)

    @cached_property
    def decision(self) -> DecisionRepository:
        from infrastructure.repositories.decision_repository import DecisionRepository
        return DecisionRepository(db=self._db)

    @cached_property
    def note(self) -> NoteRepository:
        from infrastructure.repositories.note_repository import NoteRepository
        return NoteRepository(db=self._db)

    @cached_property
    def resource(self) -> ResourceRepository:
        from infrastructure.repositories.resource_repository import ResourceRepository
        return ResourceRepository(db=self._db)

    @cached_property
    def memo(self) -> MemoRepository:
        from infrastructure.repositories.memo_repository import MemoRepository
        return MemoRepository(db=self._db)


class ServiceRegistry:
    """İş kuralı katmanı fabrikaları; repository registry üzerinden beslenir."""

    def __init__(self, repos: RepositoryRegistry, db: DatabaseManager) -> None:
        self._repos = repos
        self._db = db

    @cached_property
    def stage(self) -> StageService:
        from services.stage_service import StageService
        return StageService(
            repository=self._repos.stage,
            workflow_repository=self._repos.workflow_stage,
            activity_log_repository=self._repos.activity_log,
            project_repository=self._repos.project,
        )

    @cached_property
    def project(self) -> ProjectService:
        from services.project_service import ProjectService
        return ProjectService(
            repository=self._repos.project,
            stage_service=self.stage,
            activity_log_repository=self._repos.activity_log,
            tag_repository=self._repos.project_tag,
            task_repository=self._repos.task,
            attachment_repository=self._repos.attachment,
        )

    @cached_property
    def task(self) -> TaskService:
        from services.task_service import TaskService
        return TaskService(
            repository=self._repos.task,
            project_service=self.project,
            activity_log_repository=self._repos.activity_log,
        )

    @cached_property
    def idea(self) -> IdeaService:
        from services.idea_service import IdeaService
        return IdeaService(
            repository=self._repos.idea,
            project_service=self.project,
            project_idea_repository=self._repos.project_idea,
            activity_log_repository=self._repos.activity_log,
        )

    @cached_property
    def decision(self) -> DecisionService:
        from services.decision_service import DecisionService
        return DecisionService(repository=self._repos.decision)

    @cached_property
    def note(self) -> NoteService:
        from services.note_service import NoteService
        return NoteService(repository=self._repos.note)

    @cached_property
    def resource(self) -> ResourceService:
        from services.resource_service import ResourceService
        return ResourceService(repository=self._repos.resource)

    @cached_property
    def dashboard(self) -> DashboardService:
        from services.dashboard_service import DashboardService
        return DashboardService(db=self._db)

    @cached_property
    def search(self) -> SearchService:
        from services.search_service import SearchService
        return SearchService(db=self._db)

    @cached_property
    def export(self) -> ExportService:
        from services.export_service import ExportService
        return ExportService(db=self._db)

    @cached_property
    def memo(self) -> MemoService:
        from services.memo_service import MemoService
        return MemoService(repository=self._repos.memo)

    @cached_property
    def analytics(self) -> AnalyticsService:
        from services.analytics_service import AnalyticsService
        return AnalyticsService(db=self._db)

    @cached_property
    def speech_to_text(self) -> SpeechToTextService:
        from services.speech.speech_to_text_service import SpeechToTextService
        from app.config import VOSK_TR_MODEL_DIR
        return SpeechToTextService(model_dir=VOSK_TR_MODEL_DIR)


class ControllerRegistry:
    """Sinyal köprüsü katmanı fabrikaları; service registry üzerinden beslenir."""

    def __init__(self, services: ServiceRegistry, event_bus: EventBus) -> None:
        self._services = services
        self._event_bus = event_bus

    @cached_property
    def project_controller(self) -> ProjectController:
        from controllers.project_controller import ProjectController
        return ProjectController(service=self._services.project, event_bus=self._event_bus)

    @cached_property
    def stage_controller(self) -> StageController:
        from controllers.stage_controller import StageController
        # StageController proje oluşturma olayına abone olur;
        # event_bus üzerinden bağlantı kurar, oluşturulma sırası esnektir.
        return StageController(service=self._services.stage, event_bus=self._event_bus)

    @cached_property
    def task_controller(self) -> TaskController:
        from controllers.task_controller import TaskController
        return TaskController(service=self._services.task)

    @cached_property
    def idea_controller(self) -> IdeaController:
        from controllers.idea_controller import IdeaController
        return IdeaController(service=self._services.idea, event_bus=self._event_bus)

    @cached_property
    def decision_controller(self) -> DecisionController:
        from controllers.decision_controller import DecisionController
        return DecisionController(service=self._services.decision)

    @cached_property
    def note_controller(self) -> NoteController:
        from controllers.note_controller import NoteController
        return NoteController(service=self._services.note)

    @cached_property
    def resource_controller(self) -> ResourceController:
        from controllers.resource_controller import ResourceController
        return ResourceController(service=self._services.resource)

    @cached_property
    def dashboard_controller(self) -> DashboardController:
        from controllers.dashboard_controller import DashboardController
        return DashboardController(service=self._services.dashboard, event_bus=self._event_bus)

    @cached_property
    def search_controller(self) -> SearchController:
        from controllers.search_controller import SearchController
        return SearchController(service=self._services.search)

    @cached_property
    def settings_controller(self) -> SettingsController:
        from controllers.settings_controller import SettingsController
        return SettingsController(service=self._services.export)

    @cached_property
    def memo_controller(self) -> MemoController:
        from controllers.memo_controller import MemoController
        return MemoController(service=self._services.memo)

    @cached_property
    def analytics_controller(self) -> AnalyticsController:
        from controllers.analytics_controller import AnalyticsController
        return AnalyticsController(
            service=self._services.analytics,
            event_bus=self._event_bus,
        )
