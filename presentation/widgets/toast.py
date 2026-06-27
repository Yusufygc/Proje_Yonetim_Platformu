"""
Premium bildirim sistemi (Toast / Snackbar).
Kısa süreli (ephemeral) mesajları ekranda gösterip otomatik kaybolan widget.
"""
from collections.abc import Callable

from PySide6.QtCore import QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from core.events.event_bus import EventBus
from presentation.dimensions import Shadow, Size, Spacing
from presentation.utils.ui_utils import apply_shadow


class Toast(QWidget):
    """Ekranda geçici olarak beliren şık bildirim mesajı."""
    def __init__(self, parent: QWidget, event_bus: EventBus | None = None) -> None:
        super().__init__(parent)
        self.hide()
        self._undo_callback: Callable[[], None] | None = None

        self._setup_ui()
        self._show_anim = QPropertyAnimation(self, b"geometry")
        self._show_anim.setDuration(300)
        self._show_anim.finished.connect(self._on_show_finished)

        self._hide_anim = QPropertyAnimation(self, b"geometry")
        self._hide_anim.setDuration(300)
        self._hide_anim.finished.connect(self.hide)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide_toast)

        # Constructor injection tercih edilir; None ise singleton'a düşülür.
        # WeakMethod aboneliği sayesinde widget yok olunca otomatik düşer.
        bus = event_bus or EventBus.instance()
        bus.subscribe("toast.show", self._on_toast_requested)
        
    def _setup_ui(self) -> None:
        self.setFixedHeight(Size.TOAST_H)
        self.setMinimumWidth(Size.TOAST_MIN_W)
        self.setMaximumWidth(Size.TOAST_MAX_W)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.MD, Spacing.XL, Spacing.MD)
        
        self._label = QLabel(self)
        self._label.setObjectName("toast_label")
        layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignCenter)

        self._undo_btn = QPushButton(parent=self)
        self._undo_btn.setObjectName("toast_undo_btn")
        self._undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._undo_btn.clicked.connect(self._on_undo_clicked)
        self._undo_btn.hide()
        layout.addWidget(self._undo_btn)

        self.setProperty("type", "success")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        apply_shadow(self, blur_radius=Shadow.TOAST_BLUR, y_offset=Shadow.TOAST_Y, alpha=Shadow.TOAST_ALPHA)

    def _on_toast_requested(
        self,
        message: str,
        type_: str = "success",
        undo_label: str | None = None,
        undo_callback: Callable[[], None] | None = None,
    ) -> None:
        self.show_toast(message, type_, undo_label=undo_label, undo_callback=undo_callback)
        
    def show_toast(
        self,
        message: str,
        type_: str = "success",
        undo_label: str | None = None,
        undo_callback: Callable[[], None] | None = None,
    ) -> None:
        self._label.setText(message)
        self._undo_callback = undo_callback
        if undo_callback is not None:
            self._undo_btn.setText(undo_label or "Geri Al")
            self._undo_btn.show()
        else:
            self._undo_btn.hide()
        
        self.setProperty("type", type_)
        self.style().unpolish(self)
        self.style().polish(self)
        
        self.adjustSize()
        
        self._timer.stop()
        self._hide_anim.stop()

        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            start_y = -self.height() - 20
            end_y = 20

            self._show_anim.setStartValue(QRect(x, start_y, self.width(), self.height()))
            self._show_anim.setEndValue(QRect(x, end_y, self.width(), self.height()))

        self.show()
        self.raise_()
        self._show_anim.start()

    def _on_show_finished(self) -> None:
        self._timer.start(3000)

    def _on_undo_clicked(self) -> None:
        callback = self._undo_callback
        self._undo_callback = None
        self._timer.stop()
        self._hide_toast_immediate()
        if callback is not None:
            callback()

    def _hide_toast_immediate(self) -> None:
        self._show_anim.stop()
        self._timer.stop()
        self.hide()

    def hide_toast(self) -> None:
        self._show_anim.stop()
        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            start_y = self.geometry().y()
            end_y = -self.height() - 20

            self._hide_anim.setStartValue(QRect(x, start_y, self.width(), self.height()))
            self._hide_anim.setEndValue(QRect(x, end_y, self.width(), self.height()))
            self._hide_anim.start()
