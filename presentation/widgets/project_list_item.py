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
        self.setMinimumHeight(58)
        # Not: QGraphicsDropShadowEffect kaldırıldı — hover ile yanmasönmede neden oluyordu

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Başlık + durum satırı
        top_row = QWidget(parent=self)
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        title_lbl = QLabel(project.title, parent=top_row)
        title_lbl.setProperty("cssClass", "text-primary")
        title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        top_layout.addWidget(title_lbl, 1)

        status_text = _STATUS_TR.get(project.status, project.status)
        status_color = _STATUS_COLORS.get(project.status, "#8B8FA8")
        status_lbl = QLabel(status_text, parent=top_row)
        status_lbl.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {status_color};")
        status_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        top_layout.addWidget(status_lbl)
        layout.addWidget(top_row)

        if project.short_description:
            desc_lbl = QLabel(project.short_description, parent=self)
            desc_lbl.setProperty("cssClass", "text-secondary")
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("font-size: 11px;")
            desc_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            layout.addWidget(desc_lbl)

        # Öncelik + progress satırı
        bottom_row = QWidget(parent=self)
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)

        priority_text = _PRIORITY_TR.get(project.priority, project.priority)
        priority_color = _PRIORITY_COLORS.get(project.priority, "#6366F1")
        priority_lbl = QLabel(f"● {priority_text}", parent=bottom_row)
        priority_lbl.setStyleSheet(f"font-size: 11px; color: {priority_color};")
        priority_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        bottom_layout.addWidget(priority_lbl)
        bottom_layout.addStretch()

        progress = QProgressBar(parent=bottom_row)
        progress.setRange(0, 100)
        progress.setValue(project.progress_percent)
        progress.setMaximumWidth(80)
        progress.setMaximumHeight(4)
        progress.setTextVisible(False)
        progress.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        # QProgressBar stili global QSS içinde yönetilir
        bottom_layout.addWidget(progress)
        layout.addWidget(bottom_row)

        meta_parts = []
        try:
            active_stage = next((s.name for s in project.stages if s.status == "ACTIVE"), None)
            if active_stage:
                meta_parts.append(f"Aşama: {active_stage}")
        except Exception:
            pass
        try:
            open_tasks = len([t for t in project.tasks if t.status not in {"DONE", "CANCELLED"}])
            meta_parts.append(f"Açık görev: {open_tasks}")
        except Exception:
            pass
        meta_parts.append(f"Güncellendi: {project.updated_at.date()}")
        try:
            tags = [tag.tag_name for tag in project.tags[:3]]
            if tags:
                meta_parts.append("Etiket: " + ", ".join(tags))
        except Exception:
            pass
        meta_lbl = QLabel(" · ".join(meta_parts), parent=self)
        meta_lbl.setProperty("cssClass", "text-muted")
        meta_lbl.setWordWrap(True)
        meta_lbl.setStyleSheet("font-size: 10px;")
        meta_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(meta_lbl)

    def _apply_style(self, selected: bool) -> None:
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_selected(self, selected: bool) -> None:
        self._apply_style(selected)

    def matches_filter(self, text: str) -> bool:
        return not text or text in self._title_lower

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.clicked.emit(self._project_id)
