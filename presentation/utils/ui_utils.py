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
    color: QColor | None = None,
) -> None:
    """
    Belirtilen widget'a yumuşak (soft) gölge efekti uygular.
    Özellikle kartlar ve dialoglar için 'Premium His' yaratır.

    QSS gölge efektini yönetemediğinden varsayılan değerler
    presentation.dimensions.Shadow sabitlerinden alınır. color verilirse
    (örn. aktif öğe için accent renkli glow) siyah taban yerine kullanılır.
    """
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setXOffset(0)
    shadow.setYOffset(y_offset)
    base = QColor(color) if color is not None else QColor(Shadow.COLOR_R, Shadow.COLOR_G, Shadow.COLOR_B)
    base.setAlpha(alpha)
    shadow.setColor(base)
    widget.setGraphicsEffect(shadow)
