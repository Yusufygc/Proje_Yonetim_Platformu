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
from core.managers.font_manager import FontManager
from core.managers.log_manager import install_global_exception_hook, setup_logging
from core.managers.preference_manager import PreferenceManager
from core.managers.theme_manager import ThemeManager
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.repositories.project_repository import ProjectRepository
from infrastructure.repositories.stage_repository import StageRepository
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.repositories.idea_repository import IdeaRepository
from services.project_service import ProjectService
from services.stage_service import StageService
from services.task_service import TaskService
from services.idea_service import IdeaService
from controllers.task_controller import TaskController
from controllers.idea_controller import IdeaController

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
        install_global_exception_hook()

        logger.info("%s v%s başlatılıyor...", config.APP_NAME, config.APP_VERSION)

        self._db = DatabaseManager.instance(str(config.DATABASE_URL))
        self._db.create_all_tables()

        self._theme = ThemeManager.instance(config.THEMES_DIR)
        self._fonts = FontManager.instance(config.FONTS_DIR)
        self._fonts.load_all()

        self._prefs = PreferenceManager.instance()
        self._event_bus = EventBus.instance()

        self._project_repo = ProjectRepository(db=self._db)
        self._project_service = ProjectService(repository=self._project_repo)
        self._project_controller = ProjectController(
            service=self._project_service,
            event_bus=self._event_bus,
        )

        self._stage_repo = StageRepository(db=self._db)
        self._stage_service = StageService(repository=self._stage_repo)
        # StageController proje oluşturma olayına abone olur; ProjectController'dan sonra kurulmalı
        self._stage_controller = StageController(
            service=self._stage_service,
            event_bus=self._event_bus,
        )

        self._task_repo = TaskRepository(db=self._db)
        self._task_service = TaskService(repository=self._task_repo)
        self._task_controller = TaskController(service=self._task_service)

        self._idea_repo = IdeaRepository(db=self._db)
        self._idea_service = IdeaService(repository=self._idea_repo, project_service=self._project_service)
        self._idea_controller = IdeaController(service=self._idea_service)

        self._initialized = True
        logger.info("DI Container başarıyla kuruldu.")

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
