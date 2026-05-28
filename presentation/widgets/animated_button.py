"""
Mikro-animasyonlu özel buton sınıfı.
Hover durumunda QPropertyAnimation ile büyüme (scale) veya renk geçişi yapar.
"""
from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QPushButton, QWidget


class AnimatedButton(QPushButton):
    """Hover esnasında genişleme animasyonu sunan buton."""
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setProperty("primary", True)
        
        # Geometri animasyonu (büyüme efekti simülasyonu)
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(150)
        self._original_geometry = QRect()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self._original_geometry = self.geometry()
        new_geo = self._original_geometry.adjusted(-2, -2, 2, 2)
        
        self._anim.setStartValue(self._original_geometry)
        self._anim.setEndValue(new_geo)
        self._anim.start()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self._anim.setStartValue(self.geometry())
        self._anim.setEndValue(self._original_geometry)
        self._anim.start()
