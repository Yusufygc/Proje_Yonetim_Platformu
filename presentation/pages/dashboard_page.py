"""
Dashboard sayfası — istatistik kartlarını ve son aktiviteleri barındırır.
Faz 7 kapsamında DashboardController ile veri çeker.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controllers.dashboard_controller import DashboardController
from core.managers.theme_manager import ThemeManager
from presentation.utils.ui_utils import apply_shadow


class DashboardPage(QWidget):
    """Ana dashboard ekranı — özet istatistikler ve son aktiviteler."""

    def __init__(self, parent: QWidget, controller: DashboardController) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        title = QLabel("Dashboard", parent=self)
        title.setProperty("cssClass", "title-large")
        layout.addWidget(title)

        # Stats Cards
        stats_layout = QHBoxLayout()
        self._lbl_projects = self._create_stat_card(stats_layout, "Toplam Proje", "0")
        self._lbl_ideas = self._create_stat_card(stats_layout, "Toplam Fikir", "0")
        self._lbl_tasks = self._create_stat_card(stats_layout, "Toplam Görev", "0")
        layout.addLayout(stats_layout)

        # Lists Layout
        lists_layout = QHBoxLayout()
        lists_layout.setSpacing(24)

        # Blocked Projects
        blocked_container = QWidget(parent=self)
        blocked_layout = QVBoxLayout(blocked_container)
        blocked_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_blocked = QLabel("Tıkanan / Riskli Projeler")
        lbl_blocked.setProperty("cssClass", "title-small")
        blocked_layout.addWidget(lbl_blocked)

        self._blocked_list = QListWidget(parent=blocked_container)
        self._blocked_list.setProperty("cssClass", "panel")
        apply_shadow(self._blocked_list, blur_radius=15, y_offset=3, alpha=15)
        blocked_layout.addWidget(self._blocked_list)
        lists_layout.addWidget(blocked_container)

        # Recent Tasks
        recent_container = QWidget(parent=self)
        recent_layout = QVBoxLayout(recent_container)
        recent_layout.setContentsMargins(0, 0, 0, 0)

        lbl_recent = QLabel("Son Aktiviteler (Görevler)")
        lbl_recent.setProperty("cssClass", "title-small")
        recent_layout.addWidget(lbl_recent)

        self._recent_list = QListWidget(parent=recent_container)
        self._recent_list.setProperty("cssClass", "panel")
        apply_shadow(self._recent_list, blur_radius=15, y_offset=3, alpha=15)
        recent_layout.addWidget(self._recent_list)
        lists_layout.addWidget(recent_container)

        layout.addLayout(lists_layout, 1)

    def _create_stat_card(self, layout: QHBoxLayout, title: str, initial_val: str) -> QLabel:
        card = QFrame(parent=self)
        card.setProperty("cssClass", "panel")
        apply_shadow(card, blur_radius=15, y_offset=3, alpha=20)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        lbl_title = QLabel(title, parent=card)
        lbl_title.setProperty("cssClass", "text-secondary")
        lbl_title.setStyleSheet("font-weight: bold;")
        card_layout.addWidget(lbl_title)

        lbl_val = QLabel(initial_val, parent=card)
        lbl_val.setProperty("cssClass", "text-primary")
        lbl_val.setStyleSheet("font-size: 32px; font-weight: 800;")
        card_layout.addWidget(lbl_val)

        layout.addWidget(card)
        return lbl_val

    def _connect_signals(self) -> None:
        self._controller.stats_loaded.connect(self._on_stats_loaded)

    def _on_stats_loaded(self, stats: dict) -> None:
        self._lbl_projects.setText(str(stats.get("total_projects", 0)))
        self._lbl_ideas.setText(str(stats.get("total_ideas", 0)))
        self._lbl_tasks.setText(str(stats.get("total_tasks", 0)))

        self._blocked_list.clear()
        theme_mgr = ThemeManager.instance()
        danger_color = theme_mgr.color("danger")
        for p in stats.get("blocked_projects", []):
            item = QListWidgetItem()
            item.setText(f"{p['name']} ({p['status']})")
            item.setForeground(QColor(danger_color))
            self._blocked_list.addItem(item)

        self._recent_list.clear()
        text_sec_color = theme_mgr.color("text_secondary")
        for t in stats.get("recent_tasks", []):
            item = QListWidgetItem()
            item.setText(f"[{t['project_name']}] {t['title']} ({t['status']})")
            item.setForeground(QColor(text_sec_color))
            self._recent_list.addItem(item)

    def showEvent(self, event):
        super().showEvent(event)
        self._controller.load_stats()
