"""Animated sidebar navigation with persisted theme switching."""
from __future__ import annotations

import logging

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

import config
from core.managers.icon_manager import IconManager
from core.managers.preference_manager import PreferenceManager
from core.managers.string_manager import StringManager
from core.managers.theme_manager import ThemeManager

logger = logging.getLogger(__name__)

NAV_ITEMS: list[tuple[str, str, str, str]] = [
    ("dashboard", "nav_dashboard", "Dashboard", "house"),
    ("projects", "nav_projects", "Projeler", "folder"),
    ("ideas", "nav_ideas", "Fikirler", "lightbulb"),
    ("tasks", "nav_tasks", "Görevler", "square-check"),
    ("settings", "nav_settings", "Ayarlar", "settings"),
]


def _tr(key: str, default: str) -> str:
    return StringManager.get(key, default)


class ThemeToggleSwitch(QFrame):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(24)
        self.setFixedWidth(44)
        self._active = False
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
            self.setStyleSheet("ThemeToggleSwitch { background-color: #6366F1; border-radius: 12px; }")
            self._thumb.setStyleSheet("background-color: #FFFFFF; border-radius: 9px;")
        else:
            self.setStyleSheet("ThemeToggleSwitch { background-color: #2A2D38; border-radius: 12px; }")
            self._thumb.setStyleSheet("background-color: #8B8FA8; border-radius: 9px;")

    def mousePressEvent(self, event: object) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)


class SidebarNavButton(QPushButton):
    def __init__(self, page_name: str, label_key: str, default_label: str, icon_name: str, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.page_name = page_name
        self._label_key = label_key
        self._default_label = default_label
        self._icon_name = icon_name
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_expanded(True)
        self._apply_style(active=False)

    def set_expanded(self, expanded: bool) -> None:
        self.setText(f"  {_tr(self._label_key, self._default_label)}" if expanded else "")

    def set_active(self, active: bool) -> None:
        self.setChecked(active)
        self._apply_style(active)

    def refresh_theme(self) -> None:
        self._apply_style(self.isChecked())

    def _apply_style(self, active: bool) -> None:
        theme_mgr = ThemeManager.instance()
        is_dark = theme_mgr.current_theme == "dark"
        if active:
            # Dark modda beyaz ikon (koyu arka planüzerinde), light modda accent rengi (açık arka plan üzerinde)
            icon_color = "#FFFFFF" if is_dark else theme_mgr.color("accent_start")
            # Aktif buton arka planı — her iki temada da accent yarı saydam
            accent = theme_mgr.color("accent_start")
            self.setStyleSheet(
                f"QPushButton {{ background-color: rgba(99,102,241,0.18); "
                f"border-left: 3px solid {accent}; "
                f"border-radius: 8px; color: {accent}; font-weight: 700; }}"
            )
        else:
            icon_color = theme_mgr.color("text_secondary")
            self.setStyleSheet("")
        self.setIcon(IconManager.instance().get_icon(self._icon_name, icon_color))


class Sidebar(QFrame):
    page_requested = Signal(str)
    search_requested = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._prefs = PreferenceManager.instance()
        self._theme = ThemeManager.instance()
        self._collapsed = self._prefs.load_sidebar_collapsed()
        self._nav_buttons: dict[str, SidebarNavButton] = {}
        self._setup_ui()
        self._setup_animation()
        self._theme.theme_changed.connect(self._on_theme_changed)
        if self._collapsed:
            self._collapse(animate=False)

    def _setup_ui(self) -> None:
        self.setFixedWidth(config.SIDEBAR_EXPANDED_WIDTH)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(4)

        header = QHBoxLayout()
        self._title_label = QLabel(_tr("app_short_name", "Proje Takip"), parent=self)
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

        self._search_btn = QPushButton(_tr("sidebar_search", "🔍 Ara (Ctrl+F)"), parent=self)
        self._search_btn.setFixedHeight(36)
        self._search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._search_btn.setProperty("cssClass", "btn-secondary")
        self._search_btn.setStyleSheet("text-align: left; padding-left: 12px; margin-top: 8px;")
        self._search_btn.clicked.connect(self.search_requested.emit)
        layout.addWidget(self._search_btn)

        separator = QFrame(parent=self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setProperty("cssClass", "divider")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        for page_name, label_key, default_label, icon_name in NAV_ITEMS:
            btn = SidebarNavButton(page_name, label_key, default_label, icon_name, parent=self)
            btn.clicked.connect(lambda checked, p=page_name: self._on_nav_clicked(p))
            self._nav_buttons[page_name] = btn
            layout.addWidget(btn)

        layout.addStretch(1)

        self._theme_container = QWidget(parent=self)
        theme_layout = QHBoxLayout(self._theme_container)
        theme_layout.setContentsMargins(12, 8, 12, 8)
        theme_layout.setSpacing(8)

        self._theme_label = QLabel(parent=self._theme_container)
        self._theme_label.setProperty("cssClass", "text-secondary")
        self._theme_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        self._theme_switch = ThemeToggleSwitch(parent=self._theme_container)
        self._theme_switch.clicked.connect(self._toggle_theme)
        theme_layout.addWidget(self._theme_label, 1)
        theme_layout.addWidget(self._theme_switch)
        layout.addWidget(self._theme_container)

        self._theme_collapsed_btn = QPushButton(parent=self)
        self._theme_collapsed_btn.setFixedSize(36, 36)
        self._theme_collapsed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_collapsed_btn.setProperty("cssClass", "theme-collapsed-btn")
        self._theme_collapsed_btn.clicked.connect(self._toggle_theme)
        self._theme_collapsed_btn.hide()
        layout.addWidget(self._theme_collapsed_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._version_label = QLabel(f"v{config.APP_VERSION}", parent=self)
        self._version_label.setProperty("cssClass", "text-muted")
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._version_label)
        self._apply_theme_labels(animate=False)

    def _toggle_theme(self) -> None:
        new_theme = "light" if self._theme.current_theme == "dark" else "dark"
        self._prefs.save_theme(new_theme)
        self._theme.switch_theme(new_theme)

    def _on_theme_changed(self, _theme_name: str) -> None:
        self._apply_theme_labels(animate=True)
        for btn in self._nav_buttons.values():
            btn.refresh_theme()

    def _apply_theme_labels(self, animate: bool) -> None:
        is_light = self._theme.current_theme == "light"
        if animate:
            self._theme_switch.animate_to_state(is_light)
        else:
            self._theme_switch.set_active(is_light)
        self._theme_label.setText(_tr("theme_light", "Açık Tema") if is_light else _tr("theme_dark", "Koyu Tema"))
        self._theme_collapsed_btn.setText("☀️" if is_light else "🌙")

    def _setup_animation(self) -> None:
        self._animation = QPropertyAnimation(self, b"minimumWidth", parent=self)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._animation.setDuration(config.ANIMATION_DURATION_MS)
        self._max_anim = QPropertyAnimation(self, b"maximumWidth", parent=self)
        self._max_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._max_anim.setDuration(config.ANIMATION_DURATION_MS)

    def toggle_collapse(self) -> None:
        if self._collapsed:
            self._expand()
        else:
            self._collapse()

    def set_collapsed(self, collapsed: bool, animate: bool = True) -> None:
        if collapsed == self._collapsed:
            return
        if collapsed:
            self._collapse(animate=animate)
        else:
            self._expand(animate=animate)

    def _collapse(self, animate: bool = True) -> None:
        self._collapsed = True
        self._prefs.save_sidebar_collapsed(True)
        self._toggle_btn.setText("▶")
        self._title_label.hide()
        self._version_label.hide()
        self._search_btn.setText("🔍")
        for btn in self._nav_buttons.values():
            btn.set_expanded(False)
        self._theme_container.hide()
        self._theme_collapsed_btn.show()
        if animate:
            self._animate_width(config.SIDEBAR_COLLAPSED_WIDTH)
        else:
            self.setFixedWidth(config.SIDEBAR_COLLAPSED_WIDTH)

    def _expand(self, animate: bool = True) -> None:
        self._collapsed = False
        self._prefs.save_sidebar_collapsed(False)
        self._toggle_btn.setText("◀")
        self._title_label.show()
        self._version_label.show()
        self._search_btn.setText(_tr("sidebar_search", "🔍 Ara (Ctrl+F)"))
        for btn in self._nav_buttons.values():
            btn.set_expanded(True)
        self._theme_collapsed_btn.hide()
        self._theme_container.show()
        if animate:
            self._animate_width(config.SIDEBAR_EXPANDED_WIDTH)
        else:
            self.setFixedWidth(config.SIDEBAR_EXPANDED_WIDTH)

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
        for name, btn in self._nav_buttons.items():
            btn.set_active(name == page_name)
