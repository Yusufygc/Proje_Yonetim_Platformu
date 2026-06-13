"""
UI bileşenleri için görsel yardımcı fonksiyonlar (Gölge, Animasyon vb.).
"""
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from presentation.dimensions import Shadow


def apply_shadow(
    widget: QWidget,
    blur_radius: int = Shadow.BLUR,
    y_offset: int = Shadow.Y_OFFSET,
    alpha: int = Shadow.ALPHA,
) -> None:
    """
    Belirtilen widget'a yumuşak (soft) gölge efekti uygular.
    Özellikle kartlar ve dialoglar için 'Premium His' yaratır.

    QSS gölge efektini yönetemediğinden varsayılan değerler
    presentation.dimensions.Shadow sabitlerinden alınır.
    """
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(0)
    shadow.setYOffset(y_offset)
    shadow.setColor(QColor(Shadow.COLOR_R, Shadow.COLOR_G, Shadow.COLOR_B, alpha))
    widget.setGraphicsEffect(shadow)
