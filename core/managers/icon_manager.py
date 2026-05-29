"""
SVG ikon yönetim ve dinamik renklendirme merkezi.
"""
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QByteArray, QSize
from PySide6.QtGui import QIcon, QImage, QPixmap

logger = logging.getLogger(__name__)

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

    def get_svg_content(self, icon_name: str, color: str) -> str:
        """SVG içeriğini renklendirerek döndürür; dosya yoksa boş string."""
        icon_path = self._icons_dir / f"{icon_name}.svg"
        if not icon_path.exists():
            logger.warning("İkon bulunamadı: %s", icon_path)
            return ""
        content = icon_path.read_text(encoding="utf-8")
        content = content.replace('fill="currentColor"', f'fill="{color}"')
        content = content.replace('stroke="currentColor"', f'stroke="{color}"')
        return content

    def get_icon(self, icon_name: str, color: Optional[str] = None) -> QIcon:
        """
        SVG ikonunu döndürür. Eğer color verilirse SVG içindeki
        siyah/varsayılan rengi değiştirerek yeni bir ikon üretir.
        """
        cache_key = f"{icon_name}_{color}" if color else icon_name
        if cache_key in self._cache:
            return self._cache[cache_key]

        icon_path = self._icons_dir / f"{icon_name}.svg"
        if not icon_path.exists():
            logger.warning("İkon bulunamadı: %s", icon_path)
            return QIcon()

        if color:
            try:
                # SVG XML'ini oku ve fill="currentColor" veya stroke="#000000" benzeri yapıları değiştir
                content = icon_path.read_text(encoding="utf-8")
                # Basit bir replace işlemi. Çok karmaşık SVG'lerde yetmeyebilir.
                content = content.replace('fill="currentColor"', f'fill="{color}"')
                content = content.replace('stroke="currentColor"', f'stroke="{color}"')
                
                # QByteArray ile bellekte yükle
                byte_array = QByteArray(content.encode("utf-8"))
                pixmap = QPixmap()
                pixmap.loadFromData(byte_array, "SVG")
                icon = QIcon(pixmap)
                self._cache[cache_key] = icon
                return icon
            except Exception as e:
                logger.error("İkon renklendirilemedi %s: %s", icon_name, e)
                return QIcon(str(icon_path))
        else:
            icon = QIcon(str(icon_path))
            self._cache[cache_key] = icon
            return icon
