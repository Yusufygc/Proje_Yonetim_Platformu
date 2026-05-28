"""
Premium bildirim sistemi (Toast / Snackbar).
Kısa süreli (ephemeral) mesajları ekranda gösterip otomatik kaybolan widget.
"""
from collections.abc import Callable

from PySide6.QtCore import QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from core.events.event_bus import EventBus
from presentation.utils.ui_utils import apply_shadow


class Toast(QWidget):
    """Ekranda geçici olarak beliren şık bildirim mesajı."""
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.hide()
        self._undo_callback: Callable[[], None] | None = None
        
        self._setup_ui()
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(300)
        
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide_toast)
        
        # Olay dinleyicisi
        EventBus.instance().subscribe("toast.show", self._on_toast_requested)
        
    def _setup_ui(self) -> None:
        self.setFixedHeight(48)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        
        self._label = QLabel(self)
        self._label.setStyleSheet("color: white; font-weight: 500; font-size: 13px;")
        layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignCenter)

        self._undo_btn = QPushButton(parent=self)
        self._undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._undo_btn.setStyleSheet(
            "QPushButton { color: white; background: rgba(255,255,255,0.18); "
            "border-radius: 6px; padding: 6px 10px; font-weight: 600; }"
            "QPushButton:hover { background: rgba(255,255,255,0.28); }"
        )
        self._undo_btn.clicked.connect(self._on_undo_clicked)
        self._undo_btn.hide()
        layout.addWidget(self._undo_btn)
        
        self.setStyleSheet("Toast { background-color: #22C55E; border-radius: 8px; }")
        apply_shadow(self, blur_radius=20, y_offset=6, alpha=40)

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
        
        from core.managers.theme_manager import ThemeManager
        theme_mgr = ThemeManager.instance()
        theme_key = "success" if type_ == "success" else ("accent_start" if type_ == "info" else "danger")
        bg_color = theme_mgr.color(theme_key)
        self.setStyleSheet(f"Toast {{ background-color: {bg_color}; border-radius: 8px; }}")
        
        self.adjustSize()
        
        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            start_y = -self.height() - 20
            end_y = 20
            
            self._anim.setStartValue(QRect(x, start_y, self.width(), self.height()))
            self._anim.setEndValue(QRect(x, end_y, self.width(), self.height()))
            
        self.show()
        self.raise_()
        self._anim.start()
        self._timer.start(3000)

    def _on_undo_clicked(self) -> None:
        callback = self._undo_callback
        self._undo_callback = None
        self.hide()
        if callback is not None:
            callback()

    def hide_toast(self) -> None:
        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            start_y = self.geometry().y()
            end_y = -self.height() - 20
            
            self._anim.setStartValue(QRect(x, start_y, self.width(), self.height()))
            self._anim.setEndValue(QRect(x, end_y, self.width(), self.height()))
            self._anim.finished.connect(self.hide)
            self._anim.start()
