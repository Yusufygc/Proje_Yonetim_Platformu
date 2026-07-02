"""
Dark/Light renk paletlerini yöneten ve QSS üretimini merkezi olarak sağlayan Singleton.
14_PREMIUM_UI_UX_TASARIM_PLANI.md'deki renk standartları burada uygulanır.

QSS dosyaları resources/styles/ altında @token_name sözdizimi ile yazılır;
bu sınıf aktif palet değerleriyle token'ları çözümler (interpolate).
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class ThemeManager(QObject):
    """
    Uygulama temasını yöneten Singleton sınıf.

    Paleti JSON dosyasından yükler; renk ve QSS erişimini merkezi hale getirir.
    QSS dosyaları resources/styles/ altındaki .qss dosyalarından okunur,
    @token_name şeklindeki yer tutucular aktif palet renkleriyle değiştirilir.
    """

    theme_changed = Signal(str)

    _instance: ThemeManager | None = None

    def __init__(self, themes_dir: Path, styles_dir: Path) -> None:
        super().__init__()
        self._themes_dir = themes_dir
        self._styles_dir = styles_dir
        self._icons_cache_dir = styles_dir / "_cache"
        self._icons_cache_dir.mkdir(parents=True, exist_ok=True)
        self._palette: dict[str, Any] = {}
        self._current_theme = "dark"
        # QSS önbelleği — tema değişene kadar disk I/O tekrarlanmaz
        self._qss_cache: str | None = None
        self._compiled_patterns: dict[str, re.Pattern] = {}
        self._load_theme(self._current_theme)

    @classmethod
    def instance(
        cls,
        themes_dir: Path | None = None,
        styles_dir: Path | None = None,
    ) -> "ThemeManager":
        if cls._instance is None:
            if themes_dir is None or styles_dir is None:
                raise RuntimeError(
                    "ThemeManager ilk çağrıda themes_dir ve styles_dir gerektirir."
                )
            cls._instance = cls(themes_dir, styles_dir)
        return cls._instance

    def _load_theme(self, theme_name: str) -> None:
        """Belirtilen tema dosyasını yükler; bulunamazsa gömülü varsayılanı kullanır."""
        theme_file = self._themes_dir / f"{theme_name}.json"
        if not theme_file.exists():
            # Kullanıcı temaları user/ alt klasöründe saklanır
            theme_file = self._themes_dir / "user" / f"{theme_name}.json"
        if theme_file.exists():
            with open(theme_file, encoding="utf-8") as f:
                self._palette = json.load(f)
            # Alpha token'ları kaynak JSON'a bağlı olmaksızın garantile
            self._palette = self.derive_alpha_tokens(self._palette)
            logger.info("Tema yüklendi: %s", theme_file)
        else:
            logger.warning(
                "Tema dosyası bulunamadı (%s), varsayılan kullanılıyor.", theme_file
            )
            self._palette = self._default_dark_palette()
        # Palette değişti; önbellek ve derlenmiş regex'ler geçersiz
        self._qss_cache = None
        self._compiled_patterns = {}

    def switch_theme(self, theme_name: str) -> None:
        """Temayı çalışma zamanında değiştirir."""
        self._current_theme = theme_name
        self._load_theme(theme_name)
        self.theme_changed.emit(theme_name)

    @property
    def current_theme(self) -> str:
        return self._current_theme

    def color(self, key: str) -> str:
        """Palet sözlüğünden renk kodu döndürür."""
        return str(self._palette.get(key, "#FFFFFF"))

    # ── QSS üretimi ─────────────────────────────────────────────────────────

    def _interpolate_tokens(self, qss: str) -> str:
        """@token_name yer tutucularını aktif palet hex değerleriyle değiştirir.

        Regex kullanımı: @warning, @warning_alpha içinde kısmen eşleşip
        '#F59E0B_alpha' gibi geçersiz renk isimleri oluşmasını engeller.
        Derlenmiş pattern varsa yeniden derleme yapılmaz.
        """
        if self._compiled_patterns:
            for key, pattern in sorted(
                self._compiled_patterns.items(), key=lambda kv: len(kv[0]), reverse=True
            ):
                qss = pattern.sub(str(self._palette[key]), qss)
        else:
            for key, value in sorted(self._palette.items(), key=lambda kv: len(kv[0]), reverse=True):
                qss = re.sub(r"@" + re.escape(key) + r"(?![A-Za-z0-9_])", str(value), qss)
        return qss

    def _load_styles(self) -> str:
        """
        resources/styles/ altındaki tüm .qss dosyalarını alfabetik sırayla okur,
        token'ları çözümler ve birleştirilmiş QSS dizgesini döndürür.
        """
        if not self._styles_dir.exists():
            logger.warning("Styles dizini bulunamadı: %s", self._styles_dir)
            return ""
        parts: list[str] = []
        for qss_file in sorted(self._styles_dir.rglob("*.qss")):
            try:
                raw = qss_file.read_text(encoding="utf-8")
                parts.append(self._interpolate_tokens(raw))
                logger.debug("QSS yüklendi: %s", qss_file.name)
            except OSError as exc:
                logger.error("QSS okunamadı (%s): %s", qss_file, exc)
        return "\n".join(parts)

    def _generate_icon_tokens(self) -> None:
        """
        QSS ok ikonlarını tema rengiyle oluşturur, cache'e yazar ve palette'e ekler.
        IconManager bootstrap'ten sonra hazır olduğunda çalışır; önceyse atlanır.
        """
        from core.managers.icon_manager import IconManager, Icons  # noqa: I001 — döngüsel bağımlılık önlemi için geç import

        icon_mgr = IconManager.try_instance()
        if icon_mgr is None:
            return

        for token, icon_name, color_name in (
            ("icon_chevron_down", Icons.CHEVRON_DOWN, "text_secondary"),
            ("icon_chevron_up", Icons.CHEVRON_UP, "text_secondary"),
            ("icon_check", Icons.SQUARE_CHECK, "accent_start"),
        ):
            color_val = self.color(color_name)
            cache_file = self._icons_cache_dir / f"{icon_name}_{color_val.lstrip('#')}.svg"
            # Aynı renk için dosya zaten üretildiyse disk I/O tekrarlanmaz.
            if not cache_file.exists():
                svg = icon_mgr.get_svg_content(icon_name, color_val)
                if not svg:
                    continue
                cache_file.write_text(svg, encoding="utf-8")
            self._palette[token] = str(cache_file).replace("\\", "/")

    def resolve_tokens(self, text: str) -> str:
        """@token_name yer tutucularını aktif palet değerleriyle değiştirir.

        QSS dışındaki dosyalar (CSS, HTML şablonları vb.) için public API.
        """
        return self._interpolate_tokens(text)

    def build_global_qss(self) -> str:
        """Tüm uygulama için merkezi QSS stil dizgesini üretir.

        İkon token'ları palette'e eklendikten sonra pattern'lar derlenir;
        tema değişene kadar disk I/O ve regex tekrarlanmaz.
        """
        if self._qss_cache is not None:
            return self._qss_cache
        self._generate_icon_tokens()
        # İkon token'ları da dahil tüm palette için pattern'ları derle
        self._compiled_patterns = {
            key: re.compile(r"@" + re.escape(key) + r"(?![A-Za-z0-9_])")
            for key in self._palette
        }
        self._qss_cache = self._load_styles()
        return self._qss_cache

    @staticmethod
    def derive_alpha_tokens(palette: dict[str, str]) -> dict[str, str]:
        """8 alpha token'ını ana renklerden otomatik türetir (#RRGGBB22 formatı)."""
        result = dict(palette)
        mappings = [
            ("success_alpha", "success"),
            ("warning_alpha", "warning"),
            ("danger_alpha", "danger"),
            ("accent_alpha", "accent_start"),
            ("secondary_alpha", "text_secondary"),
            ("muted_alpha", "text_muted"),
            ("stage_active_alpha", "stage_active"),
            ("stage_done_alpha", "stage_done"),
        ]
        for alpha_key, src_key in mappings:
            src_color = result.get(src_key, "#888888")
            result[alpha_key] = src_color[:7] + "22"
        return result

    # ── Varsayılan palet ─────────────────────────────────────────────────────

    @staticmethod
    def _default_dark_palette() -> dict[str, str]:
        """Tema dosyası yokken kullanılacak gömülü koyu tema paleti.

        QSS dosyalarının kullandığı tüm token'ları içermeli; eksik token
        kısmî eşleşme hatalarına yol açar (ör. #6366F1_bg).
        """
        return ThemeManager.derive_alpha_tokens({
            "background": "#12141A",
            "surface": "#1C1F26",
            "surface_raised": "#22263A",
            "text_primary": "#E8EAF0",
            "text_secondary": "#8B8FA8",
            "text_muted": "#4A4D5C",
            "accent_start": "#6366F1",
            "accent_end": "#8B5CF6",
            "icon_on_accent": "#FFFFFF",
            "success": "#22C55E",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "border": "#2A2D38",
            "scrollbar_bg": "#1C1F26",
            "scrollbar_handle": "#3A3D4A",
            "sidebar_bg": "#0F1117",
            "sidebar_active": "#6366F1",
            "sidebar_text": "#8B8FA8",
            "sidebar_text_active": "#FFFFFF",
            "sidebar_hover_bg": "#1A1D25",
            "sidebar_active_bg": "#1E2136",
            "h-sidebar_bg": "#0A0C10",
            "stage_active": "#6366F1",
            "stage_done": "#22C55E",
        })
