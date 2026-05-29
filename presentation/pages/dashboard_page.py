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
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controllers.dashboard_controller import DashboardController
from controllers.idea_controller import IdeaController
from core.managers.theme_manager import ThemeManager
from presentation.utils.ui_utils import apply_shadow


class DashboardPage(QWidget):
    """Ana dashboard ekranı — özet istatistikler ve son aktiviteler."""

    def __init__(
        self,
        parent: QWidget,
        controller: DashboardController,
        idea_controller: IdeaController | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._idea_controller = idea_controller
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        title = QLabel("Ana Panel", parent=self)
        title.setProperty("cssClass", "title-large")
        layout.addWidget(title)

        # Stats Cards
        stats_layout = QHBoxLayout()
        self._lbl_projects = self._create_stat_card(stats_layout, "Toplam Proje", "0")
        self._lbl_active = self._create_stat_card(stats_layout, "Aktif", "0")
        self._lbl_completed = self._create_stat_card(stats_layout, "Tamamlanan", "0")
        self._lbl_ideas = self._create_stat_card(stats_layout, "Toplam Fikir", "0")
        self._lbl_tasks = self._create_stat_card(stats_layout, "Toplam Görev", "0")
        self._lbl_updated_week = self._create_stat_card(stats_layout, "Bu Hafta", "0")
        layout.addLayout(stats_layout)

        quick_layout = QHBoxLayout()
        self._quick_idea_edit = QLineEdit(parent=self)
        self._quick_idea_edit.setPlaceholderText("Hızlı fikir kaydet...")
        quick_layout.addWidget(self._quick_idea_edit, 1)
        quick_btn = QPushButton("+ Fikir", parent=self)
        quick_btn.setProperty("cssClass", "btn-primary")
        quick_btn.clicked.connect(self._on_quick_idea)
        quick_layout.addWidget(quick_btn)
        layout.addLayout(quick_layout)

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

        high_container = QWidget(parent=self)
        high_layout = QVBoxLayout(high_container)
        high_layout.setContentsMargins(0, 0, 0, 0)
        lbl_high = QLabel("Yüksek Öncelikli Açık Görevler")
        lbl_high.setProperty("cssClass", "title-small")
        high_layout.addWidget(lbl_high)
        self._high_priority_list = QListWidget(parent=high_container)
        self._high_priority_list.setProperty("cssClass", "panel")
        high_layout.addWidget(self._high_priority_list)
        lists_layout.addWidget(high_container)

        ideas_container = QWidget(parent=self)
        ideas_layout = QVBoxLayout(ideas_container)
        ideas_layout.setContentsMargins(0, 0, 0, 0)
        lbl_ideas = QLabel("Son Fikirler")
        lbl_ideas.setProperty("cssClass", "title-small")
        ideas_layout.addWidget(lbl_ideas)
        self._recent_ideas_list = QListWidget(parent=ideas_container)
        self._recent_ideas_list.setProperty("cssClass", "panel")
        ideas_layout.addWidget(self._recent_ideas_list)
        lists_layout.addWidget(ideas_container)

        layout.addLayout(lists_layout, 1)

    def _create_stat_card(self, layout: QHBoxLayout, title: str, initial_val: str) -> QLabel:
        card = QFrame(parent=self)
        card.setProperty("cssClass", "panel")
        apply_shadow(card, blur_radius=15, y_offset=3, alpha=20)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        lbl_title = QLabel(title, parent=card)
        lbl_title.setProperty("cssClass", "stat-card-title")
        card_layout.addWidget(lbl_title)

        lbl_val = QLabel(initial_val, parent=card)
        lbl_val.setProperty("cssClass", "stat-card-value")
        card_layout.addWidget(lbl_val)

        layout.addWidget(card)
        return lbl_val

    def _connect_signals(self) -> None:
        self._controller.stats_loaded.connect(self._on_stats_loaded)

    def _on_stats_loaded(self, stats: dict) -> None:
        self._lbl_projects.setText(str(stats.get("total_projects", 0)))
        self._lbl_active.setText(str(stats.get("active_projects", 0)))
        self._lbl_completed.setText(str(stats.get("completed_projects", 0)))
        self._lbl_ideas.setText(str(stats.get("total_ideas", 0)))
        self._lbl_tasks.setText(str(stats.get("total_tasks", 0)))
        self._lbl_updated_week.setText(str(stats.get("updated_this_week", 0)))

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

        self._high_priority_list.clear()
        for t in stats.get("high_priority_tasks", []):
            self._high_priority_list.addItem(
                QListWidgetItem(f"[{t['project_name']}] {t['title']} ({t['priority']})")
            )

        self._recent_ideas_list.clear()
        for idea in stats.get("recent_ideas", []):
            self._recent_ideas_list.addItem(QListWidgetItem(f"{idea['title']} ({idea['status']})"))

    def _on_quick_idea(self) -> None:
        title = self._quick_idea_edit.text().strip()
        if not title or self._idea_controller is None:
            return
        self._idea_controller.create_idea(title)
        self._quick_idea_edit.clear()
        self._controller.load_stats()

    def showEvent(self, event):
        super().showEvent(event)
        self._controller.load_stats()
