"""
QPropertyAnimation ile genişleyen/daralan premium sol navigasyon menüsü.
14_PREMIUM_UI_UX_TASARIM_PLANI.md'deki animasyon standartları uygulanır.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal, QPoint
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
from core.managers.icon_manager import IconManager
from core.managers.theme_manager import ThemeManager

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Sidebar navigasyon öğelerinin tanımları: (sayfa_adı, etiket, icon_adı)
# Sidebar navigasyon öğelerinin tanımları: (sayfa_adı, etiket, icon_adı)
NAV_ITEMS: list[tuple[str, str, str]] = [
    ("dashboard", "Dashboard", "house"),
    ("projects", "Projeler", "folder"),
    ("ideas", "Fikirler", "lightbulb"),
    ("tasks", "Görevler", "square-check"),
    ("settings", "Ayarlar", "settings"),
]


class ThemeToggleSwitch(QFrame):
    """Koyu/Açık tema geçişi sağlayan premium kayar buton."""
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(24)
        self.setFixedWidth(44)
        self._active = False  # False: Dark, True: Light

        self._thumb = QFrame(parent=self)
        self._thumb.setFixedSize(18, 18)

        self._anim = QPropertyAnimation(self._thumb, b"pos", parent=self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._apply_style()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_style()
        self._thumb.move(self._get_x(), 3)

    def animate_to_state(self, active: bool) -> None:
        self._active = active
        self._apply_style()
        self._anim.stop()
        self._anim.setStartValue(self._thumb.pos())
        self._anim.setEndValue(QPoint(self._get_x(), 3))
        self._anim.start()

    def _get_x(self) -> int:
        return 23 if self._active else 3

    def _apply_style(self) -> None:
        if self._active:
            self.setStyleSheet(
                "ThemeToggleSwitch { background-color: #6366F1; border-radius: 12px; }"
            )
            self._thumb.setStyleSheet(
                "background-color: #FFFFFF; border-radius: 9px;"
            )
        else:
            self.setStyleSheet(
                "ThemeToggleSwitch { background-color: #2A2D38; border-radius: 12px; }"
            )
            self._thumb.setStyleSheet(
                "background-color: #8B8FA8; border-radius: 9px;"
            )

    def mousePressEvent(self, event: object) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)


class SidebarNavButton(QPushButton):
    """
    Sidebar'da tek bir navigasyon öğesini temsil eden buton.
    Aktif/pasif duruma göre stil değişir.
    """

    def __init__(self, page_name: str, label: str, icon_name: str, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.page_name = page_name
        self._label = label
        self._icon_name = icon_name
        self.setCheckable(True)
        self.setText(f"  {label}")
        
        icon_mgr = IconManager.instance()
        self.setIcon(icon_mgr.get_icon(self._icon_name, "#8B8FA8"))
        
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(active=False)

    def set_active(self, active: bool) -> None:
        self.setChecked(active)
        self._apply_style(active)

    def _apply_style(self, active: bool) -> None:
        theme_mgr = ThemeManager.instance()
        icon_color = "#FFFFFF" if active else theme_mgr.color("text_secondary")
        self.setIcon(IconManager.instance().get_icon(self._icon_name, icon_color))


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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(4)

        # Başlık + toggle butonu
        header = QHBoxLayout()
        self._title_label = QLabel("Proje Takip", parent=self)
        self._title_label.setProperty("cssClass", "title-small")
        header.addWidget(self._title_label)
        header.addStretch()

        self._toggle_btn = QPushButton("◀", parent=self)
        self._toggle_btn.setFixedSize(28, 28)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setProperty("cssClass", "btn-secondary")
        self._toggle_btn.clicked.connect(self.toggle_collapse)
        header.addWidget(self._toggle_btn)
        layout.addLayout(header)

        # Search Button
        self._search_btn = QPushButton("🔍 Ara (Ctrl+F)", parent=self)
        self._search_btn.setFixedHeight(36)
        self._search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._search_btn.setProperty("cssClass", "btn-secondary")
        self._search_btn.setStyleSheet("text-align: left; padding-left: 12px; margin-top: 8px;")
        self._search_btn.clicked.connect(self.search_requested.emit)
        layout.addWidget(self._search_btn)

        # Ayırıcı
        separator = QFrame(parent=self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setProperty("cssClass", "divider")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Navigasyon butonları
        for page_name, label, icon_name in NAV_ITEMS:
            btn = SidebarNavButton(page_name, label, icon_name, parent=self)
            btn.clicked.connect(lambda checked, p=page_name: self._on_nav_clicked(p))
            self._nav_buttons[page_name] = btn
            layout.addWidget(btn)

        layout.addStretch(1)

        # Tema Değiştirme Butonu (Geniş mod için Switch, dar mod için emoji buton)
        theme_mgr = ThemeManager.instance()
        is_light = theme_mgr._current_theme == "light"

        self._theme_container = QWidget(parent=self)
        theme_layout = QHBoxLayout(self._theme_container)
        theme_layout.setContentsMargins(12, 8, 12, 8)
        theme_layout.setSpacing(8)

        self._theme_label = QLabel("Koyu Tema", parent=self._theme_container)
        self._theme_label.setProperty("cssClass", "text-secondary")
        self._theme_label.setStyleSheet("font-size: 13px; font-weight: 500;")

        self._theme_switch = ThemeToggleSwitch(parent=self._theme_container)
        self._theme_switch.clicked.connect(self._toggle_theme)

        theme_layout.addWidget(self._theme_label, 1)
        theme_layout.addWidget(self._theme_switch)
        layout.addWidget(self._theme_container)

        self._theme_collapsed_btn = QPushButton("🌙", parent=self)
        self._theme_collapsed_btn.setFixedSize(36, 36)
        self._theme_collapsed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_collapsed_btn.setProperty("cssClass", "theme-collapsed-btn")
        self._theme_collapsed_btn.clicked.connect(self._toggle_theme)
        self._theme_collapsed_btn.hide()
        layout.addWidget(self._theme_collapsed_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set initial switch/label state
        self._theme_switch.set_active(is_light)
        self._theme_label.setText("Açık Tema" if is_light else "Koyu Tema")
        self._theme_collapsed_btn.setText("☀️" if is_light else "🌙")

        # Sürüm etiketi
        self._version_label = QLabel(f"v{config.APP_VERSION}", parent=self)
        self._version_label.setProperty("cssClass", "text-muted")
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._version_label)

    def _toggle_theme(self) -> None:
        theme_mgr = ThemeManager.instance()
        if theme_mgr._current_theme == "dark":
            theme_mgr.switch_theme("light")
            self._theme_switch.animate_to_state(True)
            self._theme_label.setText("Açık Tema")
            self._theme_collapsed_btn.setText("☀️")
        else:
            theme_mgr.switch_theme("dark")
            self._theme_switch.animate_to_state(False)
            self._theme_label.setText("Koyu Tema")
            self._theme_collapsed_btn.setText("🌙")

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

        self._theme_container.hide()
        self._theme_collapsed_btn.show()

        self._animate_width(config.SIDEBAR_COLLAPSED_WIDTH)

    def _expand(self) -> None:
        self._collapsed = False
        self._toggle_btn.setText("◀")
        self._title_label.show()
        self._version_label.show()
        self._search_btn.setText("🔍 Ara (Ctrl+F)")
        for page_name, btn in self._nav_buttons.items():
            label = next(lbl for pn, lbl, icon in NAV_ITEMS if pn == page_name)
            btn.setText(f"  {label}")

        self._theme_collapsed_btn.hide()
        self._theme_container.show()

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
