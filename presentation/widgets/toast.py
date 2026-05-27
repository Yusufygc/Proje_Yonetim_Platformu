"""
Premium bildirim sistemi (Toast / Snackbar).
Kısa süreli (ephemeral) mesajları ekranda gösterip otomatik kaybolan widget.
"""
from PySide6.QtCore import QPropertyAnimation, QTimer, Qt, QRect
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QGraphicsDropShadowEffect

from core.events.event_bus import EventBus
from presentation.utils.ui_utils import apply_shadow

class Toast(QWidget):
    """Ekranda geçici olarak beliren şık bildirim mesajı."""
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()
        
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
        
        self.setStyleSheet("Toast { background-color: #22C55E; border-radius: 8px; }")
        apply_shadow(self, blur_radius=20, y_offset=6, alpha=40)

    def _on_toast_requested(self, message: str, type_: str = "success") -> None:
        self.show_toast(message, type_)
        
    def show_toast(self, message: str, type_: str = "success") -> None:
        self._label.setText(message)
        
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
