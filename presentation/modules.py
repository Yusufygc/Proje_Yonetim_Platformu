"""Uygulama modüllerinin ModuleRegistry'ye kaydedildiği merkezi kurulum dosyası.

Her FeaturePlugin sayfa anahtarını ve kenar çubuğu navigasyon meta-verisini taşır;
sayfaların kendisi QML tarafında `main.qml` içinde yüklenir.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from core.module_registry import FeaturePlugin, ModuleRegistry

if TYPE_CHECKING:
    from app.di_container import DIContainer

# (page_key, nav_label_key, varsayılan etiket, ikon) — sıra kenar çubuğu sırasıdır.
_NAV_ENTRIES: tuple[tuple[str, str, str, str], ...] = (
    ("dashboard", "nav_dashboard", "Dashboard", "house"),
    ("projects", "nav_projects", "Projeler", "folder"),
    ("ideas", "nav_ideas", "Fikirler", "lightbulb"),
    ("tasks", "nav_tasks", "Görevler", "square-check"),  # l10n: data — nav anahtarının fallback'i
    ("memo", "nav_memo", "Notlarım", "note-sticky"),  # l10n: data — nav anahtarının fallback'i
    ("analytics", "nav_analytics", "Analitik", "chart-bar"),
    ("archive", "nav_archive", "Arşiv", "archive"),  # l10n: data — nav anahtarının fallback'i
    ("info", "nav_info", "Bilgilendirme", "circle-info"),
    ("settings", "nav_settings", "Ayarlar", "settings"),
)


def setup_modules(_di: DIContainer) -> None:
    """Tüm modülleri ModuleRegistry'ye kayıt eder (zaten kayıtlıysa dokunmaz)."""
    registry = ModuleRegistry.instance()
    if registry.plugins():
        return
    for page_key, label_key, default_label, icon in _NAV_ENTRIES:
        registry.register(FeaturePlugin(page_key, label_key, default_label, icon))
