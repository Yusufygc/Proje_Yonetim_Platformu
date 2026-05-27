"""
QPropertyAnimation ile genişleyen/daralan premium sol navigasyon menüsü.
14_PREMIUM_UI_UX_TASARIM_PLANI.md'deki animasyon standartları uygulanır.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import config

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Sidebar navigasyon öğelerinin tanımları: (sayfa_adı, etiket)
NAV_ITEMS: list[tuple[str, str]] = [
    ("dashboard", "Dashboard"),
    ("projects", "Projeler"),
    ("ideas", "Fikirler"),
    ("tasks", "Görevler"),
    ("settings", "Ayarlar"),
]


class SidebarNavButton(QPushButton):
    """
    Sidebar'da tek bir navigasyon öğesini temsil eden buton.
    Aktif/pasif duruma göre stil değişir.
    """

    def __init__(self, page_name: str, label: str, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.page_name = page_name
        self._label = label
        self.setCheckable(True)
        self.setText(label)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(active=False)

    def set_active(self, active: bool) -> None:
        self.setChecked(active)
        self._apply_style(active)

    def _apply_style(self, active: bool) -> None:
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #6366F1, stop:1 #8B5CF6);
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 0 16px;
                    text-align: left;
                    font-weight: 600;
                    font-size: 13px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #8B8FA8;
                    border: none;
                    border-radius: 8px;
                    padding: 0 16px;
                    text-align: left;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #1C1F26;
                    color: #E8EAF0;
                }
            """)


class Sidebar(QFrame):
    """
    Uygulamanın sol navigasyon paneli.
    Daralt/genişlet animasyonu QPropertyAnimation ile 300ms'de çalışır.
    """

    page_requested = Signal(str)
    search_requested = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._collapsed = False
        self._nav_buttons: dict[str, SidebarNavButton] = {}

        self._setup_ui()
        self._setup_animation()

    def _setup_ui(self) -> None:
        self.setFixedWidth(config.SIDEBAR_EXPANDED_WIDTH)
        self.setObjectName("sidebar")
        self.setStyleSheet("""
            QFrame#sidebar {
                background-color: #0F1117;
                border-right: 1px solid #2A2D38;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(4)

        # Başlık + toggle butonu
        header = QHBoxLayout()
        self._title_label = QLabel("Proje Takip", parent=self)
        self._title_label.setStyleSheet("color: #E8EAF0; font-weight: 700; font-size: 14px;")
        header.addWidget(self._title_label)
        header.addStretch()

        self._toggle_btn = QPushButton("◀", parent=self)
        self._toggle_btn.setFixedSize(28, 28)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #1C1F26;
                color: #8B8FA8;
                border: 1px solid #2A2D38;
                border-radius: 6px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #2A2D38; color: #E8EAF0; }
        """)
        self._toggle_btn.clicked.connect(self.toggle_collapse)
        header.addWidget(self._toggle_btn)
        layout.addLayout(header)

        # Search Button
        self._search_btn = QPushButton("🔍 Ara (Ctrl+F)", parent=self)
        self._search_btn.setFixedHeight(36)
        self._search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1C1F26;
                color: #8B8FA8;
                border: 1px solid #2A2D38;
                border-radius: 6px;
                text-align: left;
                padding-left: 12px;
                font-size: 13px;
                margin-top: 8px;
            }
            QPushButton:hover { background-color: #2A2D38; color: #E8EAF0; }
        """)
        self._search_btn.clicked.connect(self.search_requested.emit)
        layout.addWidget(self._search_btn)

        # Ayırıcı
        separator = QFrame(parent=self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #2A2D38; margin: 8px 0;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Navigasyon butonları
        for page_name, label in NAV_ITEMS:
            btn = SidebarNavButton(page_name, label, parent=self)
            btn.clicked.connect(lambda checked, p=page_name: self._on_nav_clicked(p))
            self._nav_buttons[page_name] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Sürüm etiketi
        self._version_label = QLabel(f"v{config.APP_VERSION}", parent=self)
        self._version_label.setStyleSheet("color: #4A4D5C; font-size: 11px;")
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._version_label)

    def _setup_animation(self) -> None:
        self._animation = QPropertyAnimation(self, b"minimumWidth", parent=self)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._animation.setDuration(config.ANIMATION_DURATION_MS)

        self._max_anim = QPropertyAnimation(self, b"maximumWidth", parent=self)
        self._max_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._max_anim.setDuration(config.ANIMATION_DURATION_MS)

    def toggle_collapse(self) -> None:
        """Sidebar'ı daraltır veya genişletir."""
        if self._collapsed:
            self._expand()
        else:
            self._collapse()

    def _collapse(self) -> None:
        self._collapsed = True
        self._toggle_btn.setText("▶")
        self._title_label.hide()
        self._version_label.hide()
        self._search_btn.setText("🔍")
        for btn in self._nav_buttons.values():
            btn.setText("")

        self._animate_width(config.SIDEBAR_COLLAPSED_WIDTH)

    def _expand(self) -> None:
        self._collapsed = False
        self._toggle_btn.setText("◀")
        self._title_label.show()
        self._version_label.show()
        self._search_btn.setText("🔍 Ara (Ctrl+F)")
        for page_name, btn in self._nav_buttons.items():
            label = next(lbl for pn, lbl in NAV_ITEMS if pn == page_name)
            btn.setText(label)

        self._animate_width(config.SIDEBAR_EXPANDED_WIDTH)

    def _animate_width(self, target: int) -> None:
        current = self.width()
        self._animation.setStartValue(current)
        self._animation.setEndValue(target)
        self._max_anim.setStartValue(current)
        self._max_anim.setEndValue(target)
        self._animation.start()
        self._max_anim.start()

    def _on_nav_clicked(self, page_name: str) -> None:
        for name, btn in self._nav_buttons.items():
            btn.set_active(name == page_name)
        self.page_requested.emit(page_name)

    def set_active_page(self, page_name: str) -> None:
        """Dışarıdan aktif sayfa seçimini günceller."""
        for name, btn in self._nav_buttons.items():
            btn.set_active(name == page_name)
