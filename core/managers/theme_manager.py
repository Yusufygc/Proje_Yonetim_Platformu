"""
Dark/Light renk paletlerini yöneten ve QSS üretimini merkezi olarak sağlayan Singleton.
14_PREMIUM_UI_UX_TASARIM_PLANI.md'deki renk standartları burada uygulanır.

QSS dosyaları resources/styles/ altında @token_name sözdizimi ile yazılır;
bu sınıf aktif palet değerleriyle token'ları çözümler (interpolate).
"""
from __future__ import annotations

import json
import logging
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

    # Önizleme sonrası geri yüklenecek durum
    _preview_saved_theme: str | None = None
    _preview_saved_palette: dict | None = None

    def __init__(self, themes_dir: Path, styles_dir: Path) -> None:
        super().__init__()
        self._themes_dir = themes_dir
        self._styles_dir = styles_dir
        self._icons_cache_dir = styles_dir / "_cache"
        self._icons_cache_dir.mkdir(parents=True, exist_ok=True)
        self._palette: dict[str, Any] = {}
        self._current_theme = "dark"
        self._preview_saved_theme: str | None = None
        self._preview_saved_palette: dict | None = None
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
        if theme_file.exists():
            with open(theme_file, encoding="utf-8") as f:
                self._palette = json.load(f)
            logger.info("Tema yüklendi: %s", theme_file)
        else:
            logger.warning(
                "Tema dosyası bulunamadı (%s), varsayılan kullanılıyor.", theme_file
            )
            self._palette = self._default_dark_palette()

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

        Uzun anahtarlar önce işlenir; @surface_raised, @surface'den önce eşleşir.
        """
        for key, value in sorted(self._palette.items(), key=lambda kv: len(kv[0]), reverse=True):
            qss = qss.replace(f"@{key}", str(value))
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
        """Tüm uygulama için merkezi QSS stil dizgesini üretir."""
        self._generate_icon_tokens()
        return self._load_styles()

    # ── Kullanıcı Tema Yönetimi ──────────────────────────────────────────────

    def is_builtin(self, name: str) -> bool:
        """Yerleşik (değiştirilemez) tema mı kontrol eder."""
        return (self._themes_dir / f"{name}.json").exists() and not name.startswith("old_")

    def list_themes(self) -> list[dict]:
        """Yerleşik ve kullanıcı tanımlı tüm temaları döndürür."""
        themes: list[dict] = []
        for f in sorted(self._themes_dir.glob("*.json")):
            if not f.stem.startswith("old_"):
                themes.append({"name": f.stem, "builtin": True})
        user_dir = self._themes_dir / "user"
        if user_dir.exists():
            for f in sorted(user_dir.glob("*.json")):
                themes.append({"name": f.stem, "builtin": False})
        return themes

    def create_theme(self, name: str, palette: dict) -> None:
        """Yeni kullanıcı teması oluşturur; user/ altına kaydeder."""
        user_dir = self._themes_dir / "user"
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / f"{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(palette, f, indent=2, ensure_ascii=False)
        logger.info("Kullanıcı teması oluşturuldu: %s", name)

    def update_theme(self, name: str, palette: dict) -> bool:
        """Kullanıcı temasını günceller; yerleşik temada False döner."""
        if self.is_builtin(name):
            logger.warning("Yerleşik tema değiştirilemez: %s", name)
            return False
        user_path = self._themes_dir / "user" / f"{name}.json"
        if not user_path.exists():
            return False
        with open(user_path, "w", encoding="utf-8") as f:
            json.dump(palette, f, indent=2, ensure_ascii=False)
        return True

    def delete_theme(self, name: str) -> bool:
        """Kullanıcı temasını siler; yerleşik veya bulunamayan temada False döner."""
        if self.is_builtin(name):
            return False
        user_path = self._themes_dir / "user" / f"{name}.json"
        if not user_path.exists():
            return False
        user_path.unlink()
        logger.info("Kullanıcı teması silindi: %s", name)
        return True

    def duplicate_theme(self, src_name: str, dest_name: str) -> bool:
        """Temayı kopyalar; kopya her zaman user/ klasörüne yazılır."""
        src = self._themes_dir / f"{src_name}.json"
        if not src.exists():
            src = self._themes_dir / "user" / f"{src_name}.json"
        if not src.exists():
            return False
        with open(src, encoding="utf-8") as f:
            palette = json.load(f)
        self.create_theme(dest_name, palette)
        return True

    def export_theme(self, name: str) -> str | None:
        """Tema JSON içeriğini string olarak döndürür."""
        path = self._themes_dir / f"{name}.json"
        if not path.exists():
            path = self._themes_dir / "user" / f"{name}.json"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def import_theme(self, json_str: str, name: str) -> bool:
        """JSON string'den kullanıcı teması oluşturur."""
        try:
            palette = json.loads(json_str)
            if not isinstance(palette, dict):
                return False
            self.create_theme(name, palette)
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def get_palette_copy(self) -> dict[str, str]:
        """Düzenlenebilir token'ların aktif palet kopyasını döndürür (alpha hariç)."""
        editable = [
            "background", "surface", "surface_raised", "border",
            "text_primary", "text_secondary", "text_muted",
            "accent_start", "accent_end", "icon_on_accent",
            "success", "warning", "danger",
            "sidebar_bg", "sidebar_active", "sidebar_text", "sidebar_text_active",
            "sidebar_hover_bg", "sidebar_active_bg", "h-sidebar_bg",
            "stage_active", "stage_done",
            "scrollbar_bg", "scrollbar_handle",
        ]
        return {k: str(self._palette.get(k, "#888888")) for k in editable}

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

    def preview_palette(self, palette: dict[str, str]) -> None:
        """Geçici önizleme: paleti uygular, orijinali saklar."""
        if self._preview_saved_theme is None:
            self._preview_saved_theme = self._current_theme
            self._preview_saved_palette = dict(self._palette)
        self._palette = dict(palette)
        self.theme_changed.emit(self._current_theme)

    def restore_preview(self) -> None:
        """Geçici önizlemeyi geri alır; orijinal paleti yükler."""
        if self._preview_saved_theme is not None:
            self._palette = dict(self._preview_saved_palette or {})
            self.theme_changed.emit(self._preview_saved_theme)
            self._preview_saved_theme = None
            self._preview_saved_palette = None

    # ── Varsayılan palet ─────────────────────────────────────────────────────

    @staticmethod
    def _default_dark_palette() -> dict[str, str]:
        """Tema dosyası yokken kullanılacak gömülü koyu tema paleti."""
        return {
            "background": "#12141A",
            "surface": "#1C1F26",
            "surface_raised": "#22263A",
            "text_primary": "#E8EAF0",
            "text_secondary": "#8B8FA8",
            "text_muted": "#4A4D5C",
            "accent_start": "#6366F1",
            "accent_end": "#8B5CF6",
            "success": "#22C55E",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "border": "#2A2D38",
            "scrollbar_bg": "#1C1F26",
            "scrollbar_handle": "#3A3D4A",
            "sidebar_bg": "#0F1117",
            "sidebar_active": "#6366F1",
            "icon_on_accent": "#FFFFFF",
        }
