"""
Proje listesindeki her projeyi temsil eden tıklanabilir kart widget'ı.
clicked(int) sinyali ile proje ID'sini üst bileşene iletir.
"""
from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from domain.models.project import Project
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr

logger = logging.getLogger(__name__)


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

    @property
    def project_id(self) -> int:
        return self._project_id

    def _setup_ui(self, project: Project) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(Size.LIST_ITEM_MIN_H)
        # Öncelik kart çerçevesine, durum tek renkli noktaya kodlanır;
        # metin gitti, erişilebilirlik için ikisi de tooltip'te.
        self.setProperty("card-priority", project.priority)
        self.setToolTip(
            f"{_status_labels().get(project.status, project.status)}  ·  "
            f"{_priority_labels().get(project.priority, project.priority)}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        layout.setSpacing(Spacing.XS)

        top_row = QWidget(parent=self)
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(Spacing.MD)

        self._title_lbl = QLabel(project.title, parent=top_row)
        self._title_lbl.setProperty("cssClass", "project-list-title")
        self._title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._title_lbl.setMinimumWidth(0)
        self._title_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        top_layout.addWidget(self._title_lbl, 1)

        self._status_dot = QFrame(parent=top_row)
        self._status_dot.setObjectName("status_dot")
        self._status_dot.setProperty("status", project.status)
        self._status_dot.setFixedSize(Size.STATUS_DOT, Size.STATUS_DOT)
        self._status_dot.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        top_layout.addWidget(self._status_dot, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(top_row)

        bottom_row = QWidget(parent=self)
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(Spacing.MD)

        bottom_layout.addStretch()

        self._progress = QProgressBar(parent=bottom_row)
        self._progress.setRange(0, 100)
        self._progress.setValue(project.progress_percent)
        self._progress.setMaximumWidth(Size.PROGRESS_W)
        self._progress.setMaximumHeight(Size.PROGRESS_H)
        self._progress.setTextVisible(False)
        self._progress.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        bottom_layout.addWidget(self._progress)
        layout.addWidget(bottom_row)

        self._meta_lbl = QLabel(self._build_meta_text(project), parent=self)
        self._meta_lbl.setProperty("cssClass", "project-list-meta")
        self._meta_lbl.setWordWrap(True)
        self._meta_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(self._meta_lbl)

    @staticmethod
    def _build_meta_text(project: Project) -> str:
        meta_parts = []
        try:
            open_tasks = len([t for t in project.tasks if t.status not in {"DONE", "CANCELLED"}])
            meta_parts.append(tr("card_meta_open_tasks", "Açık görev: {count}").format(count=open_tasks))
        except Exception:
            # project.tasks may fail to lazy-load (e.g. detached instance) —
            # the card still renders, but this must not fail silently.
            logger.debug("Could not compute open-task count for project card (id=%s).", project.id)
        meta_parts.append(tr("card_meta_updated", "Güncellendi: {date}").format(date=project.updated_at.date()))
        try:
            tags = [tag.tag_name for tag in project.tags[:3]]
            if tags:
                meta_parts.append(tr("card_meta_tags", "Etiket: {tags}").format(tags=", ".join(tags)))
        except Exception:
            logger.debug("Could not read tags for project card (id=%s).", project.id)
        return "   ·   ".join(meta_parts)

    def _apply_style(self, selected: bool) -> None:
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_selected(self, selected: bool) -> None:
        self._apply_style(selected)

    def update_project(self, project: Project) -> None:
        """Widget'ı yok etmeden dinamik alanları günceller (örn. aşama tamamlama sonrası)."""
        self._title_lbl.setText(project.title)
        self._title_lower = project.title.lower()
        self._status_dot.setProperty("status", project.status)
        self._status_dot.style().unpolish(self._status_dot)
        self._status_dot.style().polish(self._status_dot)
        self.setProperty("card-priority", project.priority)
        self.style().unpolish(self)
        self.style().polish(self)
        self._progress.setValue(project.progress_percent)
        self._meta_lbl.setText(self._build_meta_text(project))
        self.setToolTip(
            f"{_status_labels().get(project.status, project.status)}  ·  "
            f"{_priority_labels().get(project.priority, project.priority)}"
        )

    def matches_filter(self, text: str) -> bool:
        return not text or text in self._title_lower

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.clicked.emit(self._project_id)
