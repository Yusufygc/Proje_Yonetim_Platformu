"""
UI bileşenleri için görsel yardımcı fonksiyonlar (Gölge, Animasyon vb.).
"""
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect

def apply_shadow(widget: QWidget, blur_radius: int = 20, y_offset: int = 4, alpha: int = 40) -> None:
    """
    Belirtilen widget'a yumuşak (soft) gölge efekti uygular.
    Özellikle kartlar ve dialoglar için 'Premium His' yaratır.
    """
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(0)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)
