"""
Veri yükleme esnasında gösterilen parlayıp sönen iskelet yükleyici.
Skeleton Screens, geleneksel 'kum saati' yerine modern UX sağlar.
"""
from PySide6.QtCore import Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from core.managers.theme_manager import ThemeManager


class SkeletonLoader(QWidget):
    """Gri tonlarında parlayıp sönen yükleyici widget."""

    def __init__(self, parent: QWidget | None = None, theme: ThemeManager | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(60)

        # Constructor injection tercih edilir; None ise singleton'a düşülür.
        self._theme = theme or ThemeManager.instance()
        self._color = QColor(self._theme.color("border"))

        # Parlama (Pulse) Animasyonu
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(1200)
        self._anim.setLoopCount(-1)  # Sonsuz döngü
        self._anim.valueChanged.connect(self._update_color)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        # Renkler her gösterimde çözülür; tema değişimi otomatik yansır.
        start_c = QColor(self._theme.color("border"))
        end_c = QColor(self._theme.color("surface_raised"))
        self._anim.setStartValue(start_c)
        self._anim.setEndValue(end_c)
        self._anim.start()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self._anim.stop()

    def _update_color(self, color: QColor) -> None:
        self._color = color
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color)

        # Basit bir kart/liste öğesi iskeleti çizimi
        rect = self.rect()
        painter.drawRoundedRect(rect.adjusted(8, 8, -8, -8), 8, 8)
