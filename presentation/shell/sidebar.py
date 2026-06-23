"""Animated sidebar navigation with persisted theme switching."""
from __future__ import annotations

import logging

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

import config
from core.managers.icon_manager import IconManager, Icons
from core.managers.preference_manager import PreferenceManager
from core.managers.theme_manager import ThemeManager
from core.module_registry import ModuleRegistry
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr as _tr

logger = logging.getLogger(__name__)


class ThemeToggleSwitch(QFrame):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(Size.THEME_SWITCH_H)
        self.setFixedWidth(Size.THEME_SWITCH_W)
        self._active = False
        self._thumb = QFrame(parent=self)
        self._thumb.setFixedSize(Size.THEME_THUMB, Size.THEME_THUMB)
        self._anim = QPropertyAnimation(self._thumb, b"pos", parent=self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._refresh_qss()
        self._thumb.move(self._get_x(), 3)

    def animate_to_state(self, active: bool) -> None:
        self._active = active
        self._refresh_qss()
        self._anim.stop()
        self._anim.setStartValue(self._thumb.pos())
        self._anim.setEndValue(QPoint(self._get_x(), 3))
        self._anim.start()

    def _get_x(self) -> int:
        # Thumb, switch içinde 3px boşlukla konumlanır; sağ taraf = switch_w - thumb - 3
        return Size.THEME_SWITCH_W - Size.THEME_THUMB - 3 if self._active else 3

    def _refresh_qss(self) -> None:
        """active property'sini günceller; QSS kuralı ThemeToggleSwitch[active="true"] ile çalışır."""
        self.setProperty("active", "true" if self._active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._thumb.style().unpolish(self._thumb)
        self._thumb.style().polish(self._thumb)

    def mousePressEvent(self, event: object) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)


class SidebarNavButton(QPushButton):
    def __init__(
        self,
        page_name: str,
        label_key: str,
        default_label: str,
        icon_name: str,
        parent: QWidget,
        theme: ThemeManager,
        icons: IconManager,
    ) -> None:
        super().__init__(parent=parent)
        self.page_name = page_name
        self._label_key = label_key
        self._default_label = default_label
        self._icon_name = icon_name
        self._theme = theme
        self._icons = icons
        self.setCheckable(True)
        self.setFixedHeight(Size.SIDEBAR_NAV_BTN_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_expanded(True)
        self._update_icon(active=False)

    def set_expanded(self, expanded: bool) -> None:
        self.setText(f"  {_tr(self._label_key, self._default_label)}" if expanded else "")

    def set_active(self, active: bool) -> None:
        self.setChecked(active)
        self._update_icon(active)

    def refresh_theme(self) -> None:
        self._update_icon(self.isChecked())

    def enterEvent(self, event: object) -> None:
        super().enterEvent(event)
        if not self.isChecked():
            self.setIcon(self._icons.get_icon(
                self._icon_name, self._theme.color("sidebar_text_active")
            ))

    def leaveEvent(self, event: object) -> None:
        super().leaveEvent(event)
        if not self.isChecked():
            self.setIcon(self._icons.get_icon(
                self._icon_name, self._theme.color("sidebar_text")
            ))

    def _update_icon(self, active: bool) -> None:
        """Tema/aktiflik durumuna göre ikon rengini günceller; renk paletten alınır."""
        if active:
            # Aktif buton rengi tema paletindeki icon_on_accent token'ından gelir;
            # koyu temada beyaz, açık temada tema tanımlı kontrast rengi.
            icon_color = self._theme.color("icon_on_accent")
        else:
            icon_color = self._theme.color("sidebar_text")
        self.setIcon(self._icons.get_icon(self._icon_name, icon_color))


class Sidebar(QFrame):
    page_requested = Signal(str)
    search_requested = Signal()

    def __init__(
        self,
        parent: QWidget,
        theme: ThemeManager | None = None,
        icons: IconManager | None = None,
        prefs: PreferenceManager | None = None,
    ) -> None:
        super().__init__(parent=parent)
        # Constructor injection tercih edilir; None ise singleton'a düşülür
        # (geriye dönük uyum ve basit test kurulumları için).
        self._theme = theme or ThemeManager.instance()
        self._icons = icons or IconManager.instance()
        self._prefs = prefs or PreferenceManager.instance()
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
        layout.setContentsMargins(Spacing.MD, Spacing.XL, Spacing.MD, Spacing.XL)
        layout.setSpacing(Spacing.XS)

        # Layout: [title(0)] [stretch(1)] [btn(2)]
        # Collapse'da stretch kaldırılıp iki taraflı stretch eklenerek buton ortalanır.
        self._header_layout = QHBoxLayout()
        self._title_label = QLabel(_tr("app_short_name", "Proje Takip"), parent=self)
        self._title_label.setProperty("cssClass", "title-small")
        self._header_layout.addWidget(self._title_label)
        self._header_layout.addStretch()

        self._toggle_btn = QPushButton("", parent=self)
        self._toggle_btn.setFixedSize(Size.SIDEBAR_TOGGLE_W, Size.SIDEBAR_TOGGLE_H)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setProperty("cssClass", "btn-secondary")
        self._toggle_btn.clicked.connect(self.toggle_collapse)
        self._toggle_btn.setIcon(
            self._icons.get_icon(Icons.MENU, self._theme.color("sidebar_text"))
        )
        self._header_layout.addWidget(self._toggle_btn)
        layout.addLayout(self._header_layout)

        self._search_btn = QPushButton(_tr("sidebar_search", "🔍 Ara (Ctrl+F)"), parent=self)
        self._search_btn.setFixedHeight(Size.SIDEBAR_SEARCH_H)
        self._search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._search_btn.setProperty("cssClass", "btn-secondary")
        self._search_btn.setObjectName("sidebar_search_btn")
        self._search_btn.clicked.connect(self.search_requested.emit)
        layout.addWidget(self._search_btn)

        separator = QFrame(parent=self)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setProperty("cssClass", "divider")
        separator.setFixedHeight(Size.SIDEBAR_DIVIDER_H)
        layout.addWidget(separator)

        for plugin in ModuleRegistry.instance().plugins():
            btn = SidebarNavButton(
                plugin.page_key, plugin.nav_label_key,
                plugin.nav_label_default, plugin.nav_icon,
                parent=self,
                theme=self._theme,
                icons=self._icons,
            )
            btn.clicked.connect(lambda checked, p=plugin.page_key: self._on_nav_clicked(p))
            self._nav_buttons[plugin.page_key] = btn
            layout.addWidget(btn)

        layout.addStretch(1)

        self._theme_container = QWidget(parent=self)
        theme_layout = QHBoxLayout(self._theme_container)
        theme_layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        theme_layout.setSpacing(Spacing.MD)

        self._theme_label = QLabel(parent=self._theme_container)
        self._theme_label.setProperty("cssClass", "theme-label")
        self._theme_switch = ThemeToggleSwitch(parent=self._theme_container)
        self._theme_switch.clicked.connect(self._toggle_theme)
        theme_layout.addWidget(self._theme_label, 1)
        theme_layout.addWidget(self._theme_switch)
        layout.addWidget(self._theme_container)

        self._theme_collapsed_btn = QPushButton(parent=self)
        self._theme_collapsed_btn.setFixedSize(Size.THEME_COLLAPSED_BTN, Size.THEME_COLLAPSED_BTN)
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
        self._toggle_btn.setIcon(
            self._icons.get_icon(Icons.MENU, self._theme.color("sidebar_text"))
        )

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
        self._title_label.hide()
        self._version_label.hide()
        self._search_btn.setText("🔍")
        for btn in self._nav_buttons.values():
            btn.set_expanded(False)
        self._theme_container.hide()
        self._theme_collapsed_btn.show()
        # Hamburger butonu ortalamak için: mevcut orta stretch'i kaldır,
        # başa ve sona eşit stretch ekle → [stretch][title(gizli)][btn][stretch]
        middle = self._header_layout.takeAt(1)
        del middle
        self._header_layout.insertStretch(0, 1)
        self._header_layout.addStretch(1)
        if animate:
            self._animate_width(config.SIDEBAR_COLLAPSED_WIDTH)
        else:
            self.setFixedWidth(config.SIDEBAR_COLLAPSED_WIDTH)

    def _expand(self, animate: bool = True) -> None:
        self._collapsed = False
        self._prefs.save_sidebar_collapsed(False)
        self._title_label.show()
        self._version_label.show()
        self._search_btn.setText(_tr("sidebar_search", "🔍 Ara (Ctrl+F)"))
        for btn in self._nav_buttons.values():
            btn.set_expanded(True)
        self._theme_collapsed_btn.hide()
        self._theme_container.show()
        # Collapse'da eklenen iki taraflı stretch'leri kaldır,
        # orijinal orta stretch'i geri ekle → [title(0)][stretch(1)][btn(2)]
        last = self._header_layout.count() - 1
        trail = self._header_layout.takeAt(last)
        del trail
        lead = self._header_layout.takeAt(0)
        del lead
        self._header_layout.insertStretch(1, 1)
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
