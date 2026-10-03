"""QML için dinamik renklendirilebilir SVG ikon sağlayıcısı (QQuickImageProvider)."""
from __future__ import annotations

import logging
from urllib.parse import parse_qs, unquote, urlparse

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtSvg import QSvgRenderer

from core.managers.icon_manager import IconManager

logger = logging.getLogger(__name__)
_DEFAULT_SIZE = 64

_ICON_ALIASES: dict[str, str] = {
    "ideas": "lightbulb",
    "idea": "lightbulb",
    "mic": "microphone",
    "tasks": "check_square",
    "task": "check_square",
    "check": "check_square",
    "check-square": "check_square",
    "edit": "pencil",
    "pen-tool": "pencil",
    "trash-2": "trash",
    "delete": "trash",
    "info": "circle-info",
    "home": "house",
    "dashboard": "house",
    "analytics": "chart-bar",
    "memo": "note-sticky",
    "notes": "note-sticky",
    "note": "note-sticky",
    "align-left": "note-sticky",
    "sticky-note": "note-sticky",
}

_BUILTIN_SVGS: dict[str, str] = {
    "plus": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line>'
        "</svg>"
    ),
    "x": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>'
        "</svg>"
    ),
    "close": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>'
        "</svg>"
    ),
}


class IconImageProvider(QQuickImageProvider):
    """QML Image bileşenlerine 'image://icons/<ad>?color=<hex>' formatında ikon sağlar."""

    def __init__(self, icon_mgr: IconManager) -> None:
        super().__init__(QQuickImageProvider.ImageType.Pixmap)
        self._icon_mgr = icon_mgr
        self._cache: dict[str, QPixmap] = {}

    def requestPixmap(self, path_id: str, size: QSize, requested_size: QSize) -> QPixmap:
        """QML'den gelen ikon isteğini çözümler ve boyanmış QPixmap döner."""
        if path_id in self._cache:
            return self._cache[path_id]

        icon_name, color = self._parse_request(path_id)
        width, height = self._calculate_dimensions(requested_size)
        fill_color = color or "#FFFFFF"

        resolved_name = _ICON_ALIASES.get(icon_name, icon_name)
        if resolved_name in _BUILTIN_SVGS:
            svg = _BUILTIN_SVGS[resolved_name].format(color=fill_color)
        else:
            svg = self._icon_mgr.get_svg_content(resolved_name, fill_color)

        if not svg:
            empty = QPixmap(width, height)
            empty.fill(Qt.GlobalColor.transparent)
            return empty

        pixmap = self._render_svg(svg, width, height)
        self._cache[path_id] = pixmap
        return pixmap

    def _parse_request(self, path_id: str) -> tuple[str, str | None]:
        parsed = urlparse(path_id)
        icon_name = parsed.path.lstrip("/")
        params = parse_qs(parsed.query)
        raw_color = params.get("color", [None])[0]
        color = unquote(raw_color) if raw_color else None
        return icon_name, color

    def _calculate_dimensions(self, requested_size: QSize) -> tuple[int, int]:
        req_w = requested_size.width()
        req_h = requested_size.height()
        width = req_w if req_w > 0 else _DEFAULT_SIZE
        height = req_h if req_h > 0 else _DEFAULT_SIZE
        return width, height

    def _render_svg(self, svg_content: str, width: int, height: int) -> QPixmap:
        renderer = QSvgRenderer(QByteArray(svg_content.encode("utf-8")))
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap
