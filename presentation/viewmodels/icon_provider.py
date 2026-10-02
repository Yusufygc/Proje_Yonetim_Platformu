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

        svg = self._icon_mgr.get_svg_content(icon_name, color or "#FFFFFF")
        if not svg:
            return QPixmap(width, height)

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
