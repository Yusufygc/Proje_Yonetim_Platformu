"""
SVG ikon dosyalarını okuyup istenen renge boyayan merkez (QML IconImageProvider kullanır).
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class IconManager:
    """resources/icons altındaki SVG dosyalarını renklendirerek sunan sınıf."""

    _instance: Optional["IconManager"] = None

    def __init__(self, icons_dir: Path) -> None:
        self._icons_dir = icons_dir

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
        # Basit replace; currentColor kullanmayan karmaşık SVG'lerde yetmeyebilir.
        content = content.replace('fill="currentColor"', f'fill="{color}"')
        content = content.replace('stroke="currentColor"', f'stroke="{color}"')
        return content
