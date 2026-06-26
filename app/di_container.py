"""
Bağımlılıkların merkezi Dependency Injection konteyneri.

bootstrap() yalnızca infrastructure'ı (log, DB, tema, font) başlatır.
Repository/service/controller fabrikaları katman başına registry'lere
ayrılmıştır (di_registries.py); bu sınıf ince bir facade'dır.
`X_controller` erişimleri geriye dönük uyumluluk için __getattr__ ile
ControllerRegistry'ye delege edilir.
"""
from __future__ import annotations

import logging
from functools import cached_property

from app import config
from core.events.event_bus import EventBus
from core.managers.backup_manager import BackupManager
from core.managers.font_manager import FontManager
from core.managers.icon_manager import IconManager
from core.managers.log_manager import install_global_exception_hook, setup_logging
from core.managers.preference_manager import PreferenceManager
from core.managers.secret_manager import SecretManager
from core.managers.string_manager import StringManager
from core.managers.theme_manager import ThemeManager
from app.di_registries import ControllerRegistry, RepositoryRegistry, ServiceRegistry
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class DIContainer:
    """
    Singleton bağımlılık konteyneri (facade).

    bootstrap() ile infrastructure hazırlanır; repos/services/controllers
    registry'leri ilk erişimde kurulur ve kendi nesnelerini lazy üretir.
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
        # Kayıtlı dil tercihi UI kurulmadan ÖNCE uygulanır; tüm tr() çağrıları
        # doğru sözlükle çözülür (tema kalıcılığıyla aynı desen).
        saved_language = self._prefs.load_language()
        if saved_language != self._strings.current_language:
            self._strings.set_language(saved_language)
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
    def icons(self) -> IconManager:
        assert self._icons is not None, "bootstrap() henüz çağrılmadı"
        return self._icons

    @property
    def strings(self) -> StringManager:
        assert self._strings is not None, "bootstrap() henüz çağrılmadı"
        return self._strings

    @property
    def event_bus(self) -> EventBus:
        assert self._event_bus is not None, "bootstrap() henüz çağrılmadı"
        return self._event_bus

    # ── Katman registry'leri (lazy) ──────────────────────────────────────────

    @cached_property
    def repos(self) -> RepositoryRegistry:
        return RepositoryRegistry(db=self.db)

    @cached_property
    def services(self) -> ServiceRegistry:
        return ServiceRegistry(repos=self.repos, db=self.db)

    @cached_property
    def controllers(self) -> ControllerRegistry:
        return ControllerRegistry(services=self.services, event_bus=self.event_bus)

    def __getattr__(self, name: str):
        # Geriye dönük uyumluluk: di.task_controller → di.controllers.task_controller.
        # __getattr__ yalnızca normal aramada bulunamayan adlar için çalışır.
        if name.endswith("_controller"):
            return getattr(self.controllers, name)
        raise AttributeError(f"{type(self).__name__!r} nesnesinde {name!r} yok")


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
            project_service = self._container.services.project
            if not project_service.get_all_projects():
                project_service.create_project(
                    "Hoş Geldiniz 🎉",
                    short_description="Proje Takip Platformuna hoş geldiniz. Bu örnek bir projedir.",
                )
        except Exception as exc:
            logger.warning("Onboarding örnek projesi oluşturulamadı: %s", exc)
