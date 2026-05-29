"""
Bağımlılıkların merkezi Dependency Injection konteyneri.

bootstrap() yalnızca infrastructure'ı (log, DB, tema, font) başlatır.
Repository, service ve controller'lar @cached_property üzerinden tembel
(lazy) olarak ilk erişimde oluşturulur; sonraki çağrılarda cache'den döner.
"""
from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING

import config
from core.events.event_bus import EventBus
from core.managers.backup_manager import BackupManager
from core.managers.font_manager import FontManager
from core.managers.icon_manager import IconManager
from core.managers.log_manager import install_global_exception_hook, setup_logging
from core.managers.preference_manager import PreferenceManager
from core.managers.secret_manager import SecretManager
from core.managers.string_manager import StringManager
from core.managers.theme_manager import ThemeManager
from infrastructure.database.db_manager import DatabaseManager

if TYPE_CHECKING:
    from controllers.dashboard_controller import DashboardController
    from controllers.decision_controller import DecisionController
    from controllers.idea_controller import IdeaController
    from controllers.note_controller import NoteController
    from controllers.project_controller import ProjectController
    from controllers.resource_controller import ResourceController
    from controllers.search_controller import SearchController
    from controllers.settings_controller import SettingsController
    from controllers.stage_controller import StageController
    from controllers.task_controller import TaskController
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
    from services.task_service import TaskService

logger = logging.getLogger(__name__)


class DIContainer:
    """
    Singleton bağımlılık konteyneri.

    bootstrap() ile infrastructure hazırlanır; repository, service ve
    controller'lar ilk property erişiminde oluşturulur (lazy singleton cache).
    """

    _instance: DIContainer | None = None

    def __init__(self) -> None:
        self._initialized = False
        # Infrastructure referansları bootstrap() tarafından doldurulur.
        self._db: DatabaseManager | None = None
        self._prefs: PreferenceManager | None = None
        self._secrets: SecretManager | None = None
        self._theme: ThemeManager | None = None
        self._fonts: FontManager | None = None
        self._icons: IconManager | None = None
        self._strings: StringManager | None = None
        self._event_bus: EventBus | None = None

    @classmethod
    def instance(cls) -> DIContainer:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def bootstrap(self) -> None:
        """
        Yalnızca infrastructure katmanını başlatır.
        Çağrı sırası önemlidir: log → veri dizinleri → DB → tercihler → tema → fontlar.
        """
        if self._initialized:
            return

        config.ensure_data_dirs()
        setup_logging(config.LOG_FILE, config.LOG_MAX_BYTES, config.LOG_BACKUP_COUNT)
        install_global_exception_hook(show_dialog=True)

        logger.info("%s v%s başlatılıyor...", config.APP_NAME, config.APP_VERSION)

        BackupManager(config.DATABASE_PATH, config.BACKUPS_DIR).run_startup_backup()

        self._db = DatabaseManager.instance(str(config.DATABASE_URL))
        self._db.run_migrations()

        self._prefs = PreferenceManager.instance()
        self._secrets = SecretManager.instance()
        self._theme = ThemeManager.instance(config.THEMES_DIR, config.STYLES_DIR)
        saved_theme = self._prefs.load_theme()
        if saved_theme != self._theme.current_theme:
            self._theme.switch_theme(saved_theme)

        self._fonts = FontManager.instance(config.FONTS_DIR)
        self._icons = IconManager.instance(config.RESOURCES_DIR / "icons")
        self._strings = StringManager.instance(config.RESOURCES_DIR / "locales")
        self._event_bus = EventBus.instance()

        self._initialized = True
        logger.info("DI Container başarıyla kuruldu.")

    # ── Infrastructure (bootstrap() tarafından eager başlatılır) ─────────────

    @property
    def db(self) -> DatabaseManager:
        assert self._db is not None, "bootstrap() henüz çağrılmadı"
        return self._db

    @property
    def theme(self) -> ThemeManager:
        assert self._theme is not None, "bootstrap() henüz çağrılmadı"
        return self._theme

    @property
    def fonts(self) -> FontManager:
        assert self._fonts is not None, "bootstrap() henüz çağrılmadı"
        return self._fonts

    @property
    def prefs(self) -> PreferenceManager:
        assert self._prefs is not None, "bootstrap() henüz çağrılmadı"
        return self._prefs

    @property
    def secrets(self) -> SecretManager:
        assert self._secrets is not None, "bootstrap() henüz çağrılmadı"
        return self._secrets

    @property
    def event_bus(self) -> EventBus:
        assert self._event_bus is not None, "bootstrap() henüz çağrılmadı"
        return self._event_bus

    # ── Repositories (lazy) ──────────────────────────────────────────────────

    @cached_property
    def _activity_log_repo(self) -> ActivityLogRepository:
        from infrastructure.repositories.activity_log_repository import ActivityLogRepository
        return ActivityLogRepository(db=self.db)

    @cached_property
    def _workflow_stage_repo(self) -> WorkflowStageRepository:
        from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository
        return WorkflowStageRepository(db=self.db)

    @cached_property
    def _project_tag_repo(self) -> ProjectTagRepository:
        from infrastructure.repositories.project_tag_repository import ProjectTagRepository
        return ProjectTagRepository(db=self.db)

    @cached_property
    def _project_idea_repo(self) -> ProjectIdeaRepository:
        from infrastructure.repositories.project_idea_repository import ProjectIdeaRepository
        return ProjectIdeaRepository(db=self.db)

    @cached_property
    def _attachment_repo(self) -> AttachmentRepository:
        from infrastructure.repositories.attachment_repository import AttachmentRepository
        return AttachmentRepository(db=self.db)

    @cached_property
    def _stage_repo(self) -> StageRepository:
        from infrastructure.repositories.stage_repository import StageRepository
        return StageRepository(db=self.db)

    @cached_property
    def _task_repo(self) -> TaskRepository:
        from infrastructure.repositories.task_repository import TaskRepository
        return TaskRepository(db=self.db)

    @cached_property
    def _project_repo(self) -> ProjectRepository:
        from infrastructure.repositories.project_repository import ProjectRepository
        return ProjectRepository(db=self.db)

    @cached_property
    def _idea_repo(self) -> IdeaRepository:
        from infrastructure.repositories.idea_repository import IdeaRepository
        return IdeaRepository(db=self.db)

    @cached_property
    def _decision_repo(self) -> DecisionRepository:
        from infrastructure.repositories.decision_repository import DecisionRepository
        return DecisionRepository(db=self.db)

    @cached_property
    def _note_repo(self) -> NoteRepository:
        from infrastructure.repositories.note_repository import NoteRepository
        return NoteRepository(db=self.db)

    @cached_property
    def _resource_repo(self) -> ResourceRepository:
        from infrastructure.repositories.resource_repository import ResourceRepository
        return ResourceRepository(db=self.db)

    # ── Services (lazy) ──────────────────────────────────────────────────────

    @cached_property
    def _stage_service(self) -> StageService:
        from services.stage_service import StageService
        return StageService(
            repository=self._stage_repo,
            workflow_repository=self._workflow_stage_repo,
            activity_log_repository=self._activity_log_repo,
        )

    @cached_property
    def _project_service(self) -> ProjectService:
        from services.project_service import ProjectService
        return ProjectService(
            repository=self._project_repo,
            stage_service=self._stage_service,
            activity_log_repository=self._activity_log_repo,
            tag_repository=self._project_tag_repo,
            task_repository=self._task_repo,
            attachment_repository=self._attachment_repo,
        )

    @cached_property
    def _task_service(self) -> TaskService:
        from services.task_service import TaskService
        return TaskService(
            repository=self._task_repo,
            project_service=self._project_service,
            activity_log_repository=self._activity_log_repo,
        )

    @cached_property
    def _idea_service(self) -> IdeaService:
        from services.idea_service import IdeaService
        return IdeaService(
            repository=self._idea_repo,
            project_service=self._project_service,
            project_idea_repository=self._project_idea_repo,
            activity_log_repository=self._activity_log_repo,
        )

    @cached_property
    def _decision_service(self) -> DecisionService:
        from services.decision_service import DecisionService
        return DecisionService(repository=self._decision_repo)

    @cached_property
    def _note_service(self) -> NoteService:
        from services.note_service import NoteService
        return NoteService(repository=self._note_repo)

    @cached_property
    def _resource_service(self) -> ResourceService:
        from services.resource_service import ResourceService
        return ResourceService(repository=self._resource_repo)

    @cached_property
    def _dashboard_service(self) -> DashboardService:
        from services.dashboard_service import DashboardService
        return DashboardService(db=self.db)

    @cached_property
    def _search_service(self) -> SearchService:
        from services.search_service import SearchService
        return SearchService(db=self.db)

    @cached_property
    def _export_service(self) -> ExportService:
        from services.export_service import ExportService
        return ExportService(db=self.db)

    # ── Controllers (lazy, public) ────────────────────────────────────────────

    @cached_property
    def project_controller(self) -> ProjectController:
        from controllers.project_controller import ProjectController
        return ProjectController(
            service=self._project_service,
            event_bus=self.event_bus,
        )

    @cached_property
    def stage_controller(self) -> StageController:
        from controllers.stage_controller import StageController
        # StageController proje oluşturma olayına abone olur;
        # event_bus üzerinden bağlantı kurar, oluşturulma sırası esnektir.
        return StageController(
            service=self._stage_service,
            event_bus=self.event_bus,
        )

    @cached_property
    def task_controller(self) -> TaskController:
        from controllers.task_controller import TaskController
        return TaskController(service=self._task_service)

    @cached_property
    def idea_controller(self) -> IdeaController:
        from controllers.idea_controller import IdeaController
        return IdeaController(service=self._idea_service, event_bus=self.event_bus)

    @cached_property
    def decision_controller(self) -> DecisionController:
        from controllers.decision_controller import DecisionController
        return DecisionController(service=self._decision_service)

    @cached_property
    def note_controller(self) -> NoteController:
        from controllers.note_controller import NoteController
        return NoteController(service=self._note_service)

    @cached_property
    def resource_controller(self) -> ResourceController:
        from controllers.resource_controller import ResourceController
        return ResourceController(service=self._resource_service)

    @cached_property
    def dashboard_controller(self) -> DashboardController:
        from controllers.dashboard_controller import DashboardController
        return DashboardController(
            service=self._dashboard_service,
            event_bus=self.event_bus,
        )

    @cached_property
    def search_controller(self) -> SearchController:
        from controllers.search_controller import SearchController
        return SearchController(service=self._search_service)

    @cached_property
    def settings_controller(self) -> SettingsController:
        from controllers.settings_controller import SettingsController
        return SettingsController(service=self._export_service)

    # No public repository accessors - UI should use controllers


class OnboardingService:
    """
    İlk açılış deneyimini yönetir.

    DI Container'dan ayrılmıştır; onboarding iş mantığı bootstrap sürecine
    ait değil, uygulama başlangıç akışına aittir. main.py tarafından
    bootstrap()'tan hemen sonra çağrılır.
    """

    def __init__(self, container: DIContainer) -> None:
        self._container = container

    def run_if_needed(self) -> None:
        """Hiç proje yoksa kullanıcıya yol gösterecek örnek bir proje oluşturur."""
        try:
            if not self._container._project_service.get_all_projects():
                self._container._project_service.create_project(
                    "Hoş Geldiniz 🎉",
                    short_description="Proje Takip Platformuna hoş geldiniz. Bu örnek bir projedir.",
                )
        except Exception as exc:
            logger.warning("Onboarding örnek projesi oluşturulamadı: %s", exc)
