"""
SVG ikon yönetim ve dinamik renklendirme merkezi.
"""
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

logger = logging.getLogger(__name__)

# QSvgRenderer rasterizasyon boyutu; QIcon gerektiğinde küçültür.
# Büyük tutulur ki yüksek DPI ekranlarda bulanıklık oluşmasın.
_RENDER_SIZE = 64


class Icons:
    """resources/icons/ altındaki ikon adları — çıplak string typo'larını önler."""

    CHECK_SQUARE = "check_square"
    CHEVRON_DOWN = "chevron-down"
    CHEVRON_UP = "chevron-up"
    CIRCLE_INFO = "circle-info"
    FOLDER = "folder"
    HOME = "home"
    HOUSE = "house"
    LIGHTBULB = "lightbulb"
    MENU = "menu"
    SEARCH = "search"
    SETTINGS = "settings"
    SQUARE_CHECK = "square-check"


class IconManager:
    """SVG dosyalarını okuyan ve belirtilen renge göre dinamik QIcon üreten sınıf."""

    _instance: Optional["IconManager"] = None

    def __init__(self, icons_dir: Path) -> None:
        self._icons_dir = icons_dir
        self._cache: dict[str, QIcon] = {}

    @classmethod
    def instance(cls, icons_dir: Optional[Path] = None) -> "IconManager":
        if cls._instance is None:
            if icons_dir is None:
                raise RuntimeError("IconManager ilk çağrıda icons_dir gerektirir.")
            cls._instance = cls(icons_dir)
        return cls._instance

    @classmethod
    def try_instance(cls) -> Optional["IconManager"]:
        """Bootstrap tamamlanmadıysa None döndürür; private alana dokunulmaz."""
        return cls._instance

    def get_svg_content(self, icon_name: str, color: str) -> str:
        """SVG içeriğini renklendirerek döndürür; dosya yoksa boş string."""
        icon_path = self._icons_dir / f"{icon_name}.svg"
        if not icon_path.exists():
            logger.warning("İkon bulunamadı: %s", icon_path)
            return ""
        content = icon_path.read_text(encoding="utf-8")
        # Basit replace; currentColor kullanmayan karmaşık SVG'lerde yetmeyebilir.
        content = content.replace('fill="currentColor"', f'fill="{color}"')
        content = content.replace('stroke="currentColor"', f'stroke="{color}"')
        return content

    def get_icon(self, icon_name: str, color: Optional[str] = None) -> QIcon:
        """
        SVG ikonunu döndürür; color verilirse currentColor alanları o renge
        boyanır. Üretilen QIcon, ad+renk anahtarıyla cache'lenir.
        """
        cache_key = f"{icon_name}_{color}" if color else icon_name
        if cache_key in self._cache:
            return self._cache[cache_key]

        icon_path = self._icons_dir / f"{icon_name}.svg"
        if not icon_path.exists():
            logger.warning("İkon bulunamadı: %s", icon_path)
            return QIcon()

        if color is None:
            icon = QIcon(str(icon_path))
            self._cache[cache_key] = icon
            return icon

        svg = self.get_svg_content(icon_name, color)
        if not svg:
            return QIcon(str(icon_path))

        icon = self._render_svg(svg)
        if icon.isNull():
            logger.error("İkon render edilemedi: %s", icon_name)
            return QIcon(str(icon_path))
        self._cache[cache_key] = icon
        return icon

    @staticmethod
    def _render_svg(svg: str) -> QIcon:
        """SVG metnini QSvgRenderer ile rasterize eder.

        QPixmap.loadFromData yerine renderer kullanılır: SVG'nin doğal
        boyutundan bağımsız, yüksek çözünürlükte keskin sonuç verir.
        """
        renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
        if not renderer.isValid():
            return QIcon()
        pixmap = QPixmap(_RENDER_SIZE, _RENDER_SIZE)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, _RENDER_SIZE, _RENDER_SIZE))
        painter.end()
        return QIcon(pixmap)
