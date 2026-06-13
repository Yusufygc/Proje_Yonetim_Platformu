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
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


def _status_labels() -> dict[str, str]:
    """Durum etiketleri; dil değişimi kart her kurulduğunda yansısın diye fonksiyon."""
    return {
        "PLANNED": tr("status_planned", "Planlandı"),
        "ACTIVE": tr("status_active", "Aktif"),
        "ON_HOLD": tr("status_on_hold", "Beklemede"),
        "BLOCKED": tr("status_blocked", "Engellendi"),
        "COMPLETED": tr("status_completed", "Tamamlandı"),
        "ARCHIVED": tr("status_archived", "Arşivlendi"),
        "CANCELLED": tr("status_cancelled_short", "İptal"),
    }


def _priority_labels() -> dict[str, str]:
    return {
        "LOW": tr("priority_low", "Düşük"),
        "MEDIUM": tr("priority_medium", "Orta"),
        "HIGH": tr("priority_high", "Yüksek"),
        "CRITICAL": tr("priority_critical", "Kritik"),
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
        self.setMinimumHeight(Size.LIST_ITEM_MIN_H)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        layout.setSpacing(Spacing.XS)

        top_row = QWidget(parent=self)
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(Spacing.MD)

        title_lbl = QLabel(project.title, parent=top_row)
        title_lbl.setProperty("cssClass", "project-list-title")
        title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        top_layout.addWidget(title_lbl, 1)

        status_lbl = QLabel(_status_labels().get(project.status, project.status), parent=top_row)
        status_lbl.setProperty("inline-status", project.status)
        status_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        top_layout.addWidget(status_lbl)
        layout.addWidget(top_row)

        if project.short_description:
            desc_lbl = QLabel(project.short_description, parent=self)
            desc_lbl.setProperty("cssClass", "project-list-desc")
            desc_lbl.setWordWrap(True)
            desc_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            layout.addWidget(desc_lbl)

        bottom_row = QWidget(parent=self)
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(Spacing.MD)

        priority_lbl = QLabel(f"● {_priority_labels().get(project.priority, project.priority)}", parent=bottom_row)
        priority_lbl.setProperty("inline-priority", project.priority)
        priority_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        bottom_layout.addWidget(priority_lbl)
        bottom_layout.addStretch()

        progress = QProgressBar(parent=bottom_row)
        progress.setRange(0, 100)
        progress.setValue(project.progress_percent)
        progress.setMaximumWidth(Size.PROGRESS_W)
        progress.setMaximumHeight(Size.PROGRESS_H)
        progress.setTextVisible(False)
        progress.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        bottom_layout.addWidget(progress)
        layout.addWidget(bottom_row)

        meta_parts = []
        try:
            active_stage = next((s.name for s in project.stages if s.status == "ACTIVE"), None)
            if active_stage:
                meta_parts.append(tr("card_meta_stage", "Aşama: {name}").format(name=active_stage))
        except Exception:
            pass
        try:
            open_tasks = len([t for t in project.tasks if t.status not in {"DONE", "CANCELLED"}])
            meta_parts.append(tr("card_meta_open_tasks", "Açık görev: {count}").format(count=open_tasks))
        except Exception:
            pass
        meta_parts.append(tr("card_meta_updated", "Güncellendi: {date}").format(date=project.updated_at.date()))
        try:
            tags = [tag.tag_name for tag in project.tags[:3]]
            if tags:
                meta_parts.append(tr("card_meta_tags", "Etiket: {tags}").format(tags=", ".join(tags)))
        except Exception:
            pass
        meta_lbl = QLabel(" · ".join(meta_parts), parent=self)
        meta_lbl.setProperty("cssClass", "project-list-meta")
        meta_lbl.setWordWrap(True)
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
