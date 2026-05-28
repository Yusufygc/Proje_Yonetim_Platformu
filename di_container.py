"""
Bağımlılıkların (servislerin, yöneticilerin, repository'lerin) birbirine bağlandığı
merkezi Dependency Injection konteyneri.
Sınıflar arası bağımlılıkları hardcode etmekten kaçınmak için tüm wiring buradan yapılır.
"""
from __future__ import annotations

import logging
from pathlib import Path

import config
from controllers.project_controller import ProjectController
from controllers.stage_controller import StageController
from core.events.event_bus import EventBus
from core.managers.backup_manager import BackupManager
from core.managers.font_manager import FontManager
from core.managers.icon_manager import IconManager
from core.managers.string_manager import StringManager
from core.managers.log_manager import install_global_exception_hook, setup_logging
from core.managers.preference_manager import PreferenceManager
from core.managers.secret_manager import SecretManager
from core.managers.theme_manager import ThemeManager
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.stage_repository import StageRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.idea_repository import IdeaRepository
from infrastructure.repositories.decision_repository import DecisionRepository
from infrastructure.repositories.note_repository import NoteRepository
from infrastructure.repositories.resource_repository import ResourceRepository
from infrastructure.repositories.activity_log_repository import ActivityLogRepository
from infrastructure.repositories.attachment_repository import AttachmentRepository
from infrastructure.repositories.project_idea_repository import ProjectIdeaRepository
from infrastructure.repositories.project_tag_repository import ProjectTagRepository
from infrastructure.repositories.workflow_stage_repository import WorkflowStageRepository

from services.dashboard_service import DashboardService
from services.search_service import SearchService
from services.export_service import ExportService
from services.project_service import ProjectService
from services.stage_service import StageService
from services.task_service import TaskService
from services.idea_service import IdeaService
from services.decision_service import DecisionService
from services.note_service import NoteService
from services.resource_service import ResourceService
from controllers.task_controller import TaskController
from controllers.idea_controller import IdeaController
from controllers.decision_controller import DecisionController
from controllers.note_controller import NoteController
from controllers.resource_controller import ResourceController
from controllers.dashboard_controller import DashboardController
from controllers.search_controller import SearchController
from controllers.settings_controller import SettingsController

logger = logging.getLogger(__name__)


class DIContainer:
    """
    Singleton bağımlılık konteyneri.

    Uygulama başlangıcında bir kez kurulur; tüm katmanlar
    bağımlılıklarını bu konteynerin özelliklerinden alır.
    """

    _instance: DIContainer | None = None

    def __init__(self) -> None:
        self._initialized = False

    @classmethod
    def instance(cls) -> "DIContainer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def bootstrap(self) -> None:
        """
        Uygulama başlangıcında tüm yöneticileri ve servisleri sırayla başlatır.
        Çağrı sırası önemlidir: log → veri dizinleri → DB → temalar → fontlar.
        """
        if self._initialized:
            return

        config.ensure_data_dirs()
        setup_logging(config.LOG_FILE, config.LOG_MAX_BYTES, config.LOG_BACKUP_COUNT)
        install_global_exception_hook(show_dialog=True)

        logger.info("%s v%s başlatılıyor...", config.APP_NAME, config.APP_VERSION)

        self._backup_manager = BackupManager(config.DATABASE_PATH, config.BACKUPS_DIR)
        self._backup_manager.run_startup_backup()

        self._db = DatabaseManager.instance(str(config.DATABASE_URL))
        self._db.run_migrations()

        self._prefs = PreferenceManager.instance()
        self._secrets = SecretManager.instance()
        self._theme = ThemeManager.instance(config.THEMES_DIR)
        saved_theme = self._prefs.load_theme()
        if saved_theme != self._theme.current_theme:
            self._theme.switch_theme(saved_theme)
        self._fonts = FontManager.instance(config.FONTS_DIR)

        self._icons = IconManager.instance(config.RESOURCES_DIR / "icons")
        self._strings = StringManager.instance(config.RESOURCES_DIR / "locales")

        self._event_bus = EventBus.instance()

        self._activity_log_repo = ActivityLogRepository(db=self._db)
        self._workflow_stage_repo = WorkflowStageRepository(db=self._db)
        self._project_tag_repo = ProjectTagRepository(db=self._db)
        self._project_idea_repo = ProjectIdeaRepository(db=self._db)
        self._attachment_repo = AttachmentRepository(db=self._db)

        self._stage_repo = StageRepository(db=self._db)
        self._stage_service = StageService(
            repository=self._stage_repo,
            workflow_repository=self._workflow_stage_repo,
            activity_log_repository=self._activity_log_repo,
        )

        self._task_repo = TaskRepository(db=self._db)

        self._project_repo = ProjectRepository(db=self._db)
        self._project_service = ProjectService(
            repository=self._project_repo,
            stage_service=self._stage_service,
            activity_log_repository=self._activity_log_repo,
            tag_repository=self._project_tag_repo,
            task_repository=self._task_repo,
        )
        self._project_controller = ProjectController(
            service=self._project_service,
            event_bus=self._event_bus,
        )

        # StageController proje oluşturma olayına abone olur; ProjectController'dan sonra kurulmalı
        self._stage_controller = StageController(
            service=self._stage_service,
            event_bus=self._event_bus,
        )

        self._task_service = TaskService(
            repository=self._task_repo,
            project_service=self._project_service,
            activity_log_repository=self._activity_log_repo,
        )
        self._task_controller = TaskController(service=self._task_service)

        self._idea_repo = IdeaRepository(db=self._db)
        self._idea_service = IdeaService(
            repository=self._idea_repo,
            project_service=self._project_service,
            project_idea_repository=self._project_idea_repo,
            activity_log_repository=self._activity_log_repo,
        )
        self._idea_controller = IdeaController(service=self._idea_service, event_bus=self._event_bus)

        self._decision_repo = DecisionRepository(db=self._db)
        self._decision_service = DecisionService(repository=self._decision_repo)
        self._decision_controller = DecisionController(service=self._decision_service)

        self._note_repo = NoteRepository(db=self._db)
        self._note_service = NoteService(repository=self._note_repo)
        self._note_controller = NoteController(service=self._note_service)

        self._resource_repo = ResourceRepository(db=self._db)
        self._resource_service = ResourceService(repository=self._resource_repo)
        self._resource_controller = ResourceController(service=self._resource_service)

        self._dashboard_service = DashboardService(db=self._db)
        self._dashboard_controller = DashboardController(
            service=self._dashboard_service,
            event_bus=self._event_bus,
        )

        self._search_service = SearchService(db=self._db)
        self._search_controller = SearchController(service=self._search_service)

        self._export_service = ExportService(db=self._db)
        self._settings_controller = SettingsController(service=self._export_service)

        self._initialized = True
        logger.info("DI Container başarıyla kuruldu.")
        
        # Onboarding: İlk açılışta örnek proje oluşturma
        try:
            if not self._project_service.get_all_projects():
                self._project_service.create_project(
                    "Hoş Geldiniz 🎉",
                    short_description="Proje Takip Platformuna hoş geldiniz. Bu örnek bir projedir.",
                )
        except Exception as exc:
            logger.warning("Onboarding örnek projesi oluşturulamadı: %s", exc)

    # --- Yönetici erişim noktaları ---

    @property
    def db(self) -> DatabaseManager:
        return self._db

    @property
    def theme(self) -> ThemeManager:
        return self._theme

    @property
    def fonts(self) -> FontManager:
        return self._fonts

    @property
    def prefs(self) -> PreferenceManager:
        return self._prefs

    @property
    def secrets(self) -> SecretManager:
        return self._secrets

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def project_controller(self) -> ProjectController:
        return self._project_controller

    @property
    def stage_controller(self) -> StageController:
        return self._stage_controller

    @property
    def task_controller(self) -> TaskController:
        return self._task_controller

    @property
    def idea_controller(self) -> IdeaController:
        return self._idea_controller

    @property
    def decision_controller(self) -> DecisionController:
        return self._decision_controller

    @property
    def note_controller(self) -> NoteController:
        return self._note_controller

    @property
    def resource_controller(self) -> ResourceController:
        return self._resource_controller

    @property
    def activity_log_repository(self) -> ActivityLogRepository:
        return self._activity_log_repo

    @property
    def attachment_repository(self) -> AttachmentRepository:
        return self._attachment_repo

    @property
    def dashboard_controller(self) -> DashboardController:
        return self._dashboard_controller

    @property
    def search_controller(self) -> SearchController:
        return self._search_controller

    @property
    def settings_controller(self) -> SettingsController:
        return self._settings_controller
