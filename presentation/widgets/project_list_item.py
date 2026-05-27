"""
Proje listesindeki her projeyi temsil eden tıklanabilir kart widget'ı.
clicked(int) sinyali ile proje ID'sini üst bileşene iletir.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from domain.models.project import Project

_STATUS_TR: dict[str, str] = {
    "PLANNED": "Planlandı",
    "ACTIVE": "Aktif",
    "ON_HOLD": "Beklemede",
    "BLOCKED": "Engellendi",
    "COMPLETED": "Tamamlandı",
    "ARCHIVED": "Arşivlendi",
    "CANCELLED": "İptal",
}

_STATUS_COLORS: dict[str, str] = {
    "PLANNED": "#8B8FA8",
    "ACTIVE": "#22C55E",
    "ON_HOLD": "#F59E0B",
    "BLOCKED": "#EF4444",
    "COMPLETED": "#22C55E",
    "ARCHIVED": "#4A4D5C",
    "CANCELLED": "#EF4444",
}

_PRIORITY_TR: dict[str, str] = {
    "LOW": "Düşük",
    "MEDIUM": "Orta",
    "HIGH": "Yüksek",
    "CRITICAL": "Kritik",
}

_PRIORITY_COLORS: dict[str, str] = {
    "LOW": "#4A4D5C",
    "MEDIUM": "#6366F1",
    "HIGH": "#F59E0B",
    "CRITICAL": "#EF4444",
}


class ProjectListItem(QFrame):
    """Tıklanabilir proje kartı; clicked(int) sinyali ile project_id yayar."""

    clicked = Signal(int)

    def __init__(self, project: Project, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._project_id: int = project.id
        self._title_lower: str = project.title.lower()
        self._setup_ui(project)
        self._apply_style(selected=False)

    def _setup_ui(self, project: Project) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(72)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(5)

        # Başlık + durum satırı
        top_row = QWidget(parent=self)
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        title_lbl = QLabel(project.title, parent=top_row)
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #E8EAF0;")
        top_layout.addWidget(title_lbl, 1)

        status_text = _STATUS_TR.get(project.status, project.status)
        status_color = _STATUS_COLORS.get(project.status, "#8B8FA8")
        status_lbl = QLabel(status_text, parent=top_row)
        status_lbl.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {status_color};")
        top_layout.addWidget(status_lbl)
        layout.addWidget(top_row)

        # Öncelik + progress satırı
        bottom_row = QWidget(parent=self)
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)

        priority_text = _PRIORITY_TR.get(project.priority, project.priority)
        priority_color = _PRIORITY_COLORS.get(project.priority, "#6366F1")
        priority_lbl = QLabel(f"● {priority_text}", parent=bottom_row)
        priority_lbl.setStyleSheet(f"font-size: 11px; color: {priority_color};")
        bottom_layout.addWidget(priority_lbl)
        bottom_layout.addStretch()

        progress = QProgressBar(parent=bottom_row)
        progress.setRange(0, 100)
        progress.setValue(project.progress_percent)
        progress.setMaximumWidth(80)
        progress.setMaximumHeight(4)
        progress.setTextVisible(False)
        progress.setStyleSheet(
            "QProgressBar { background: #2A2D38; border-radius: 2px; border: none; }"
            "QProgressBar::chunk { background: qlineargradient("
            "x1:0,y1:0,x2:1,y2:0,stop:0 #6366F1,stop:1 #8B5CF6); border-radius: 2px; }"
        )
        bottom_layout.addWidget(progress)
        layout.addWidget(bottom_row)

    def _apply_style(self, selected: bool) -> None:
        if selected:
            self.setStyleSheet(
                "ProjectListItem { background: #22263A; border-left: 3px solid #6366F1;"
                " border-radius: 8px; }"
            )
        else:
            self.setStyleSheet(
                "ProjectListItem { background: transparent; border-left: 3px solid transparent;"
                " border-radius: 8px; }"
                "ProjectListItem:hover { background: #1C1F26; }"
            )

    def set_selected(self, selected: bool) -> None:
        self._apply_style(selected)

    def matches_filter(self, text: str) -> bool:
        return not text or text in self._title_lower

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.clicked.emit(self._project_id)
