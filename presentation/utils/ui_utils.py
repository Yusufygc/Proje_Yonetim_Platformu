"""
UI bileşenleri için görsel yardımcı fonksiyonlar (Gölge, Animasyon vb.).
"""
from PySide6.QtCore import QAbstractAnimation, QEasingCurve, QPoint, QPropertyAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QListWidget,
    QWidget,
)

from presentation.dimensions import Duration, Shadow


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


def animate_move(
    widget: QWidget,
    start_pos: QPoint,
    end_pos: QPoint,
    duration_ms: int = Duration.REFLOW,
) -> QPropertyAnimation:
    """Widget'ı start_pos → end_pos arasında yumuşakça kaydırır (liste sıralama reflow'u).

    Animasyon widget'a parent'lanır; widget silinirse Qt animasyonu da temizler.
    """
    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(duration_ms)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


def fade_in(widget: QWidget, duration_ms: int = Duration.FAST, start_opacity: float = 0.4) -> None:
    """Widget'a hafif bir 'yerine oturma' fade-in'i uygular (wbs_tree.py ile aynı desen)."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    effect.setOpacity(start_opacity)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.setStartValue(start_opacity)
    anim.setEndValue(1.0)
    anim.finished.connect(lambda: widget.setGraphicsEffect(None))
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


def fade_in_current_item(list_widget: QListWidget) -> None:
    """InternalMove ile sürüklenip bırakılan (hâlâ seçili) satırı yumuşakça belirginleştirir."""
    item = list_widget.currentItem()
    if item is None:
        return
    row_widget = list_widget.itemWidget(item)
    if row_widget is not None:
        fade_in(row_widget)
