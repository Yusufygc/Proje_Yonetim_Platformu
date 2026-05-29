"""
Proje aşamalarını dikey liste olarak gösteren bileşen.
complete_requested(int) ve activate_requested(int) sinyalleri üzerinden aksiyon iletir.
"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from domain.enums.stage_status import StageStatus
from domain.models.project_stage import ProjectStage

_STATUS_TR: dict[str, str] = {
    StageStatus.NOT_STARTED.value: "Bekliyor",
    StageStatus.ACTIVE.value: "Aktif",
    StageStatus.DONE.value: "Tamamlandı",
    StageStatus.SKIPPED.value: "Atlandı",
}


class StageTimelineWidget(QWidget):
    """Proje aşamalarını durum göstergeleriyle listeler."""

    complete_requested = Signal(int)
    activate_requested = Signal(int)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._rows_layout = QVBoxLayout(self)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(4)
        self._stages: list[ProjectStage] = []
        from core.managers.theme_manager import ThemeManager
        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _theme_name: str) -> None:
        if self._stages:
            self.update_stages(self._stages)

    def update_stages(self, stages: list[ProjectStage]) -> None:
        """Aşama listesini temizler ve yeniden oluşturur."""
        self._stages = stages
        while self._rows_layout.count() > 0:
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        has_active = any(s.status == StageStatus.ACTIVE.value for s in stages)
        for stage in stages:
            self._rows_layout.addWidget(self._build_row(stage, has_active))

    def _build_row(self, stage: ProjectStage, has_active: bool) -> QFrame:
        """Tek bir aşama satırı oluşturur; duruma göre buton ve QSS property uygular."""
        is_active = stage.status == StageStatus.ACTIVE.value
        is_completed = stage.status == StageStatus.DONE.value
        is_pending = stage.status == StageStatus.NOT_STARTED.value

        card = QFrame(parent=self)
        card.setObjectName("stage_card")
        card.setProperty("stage-status", stage.status)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        dot = QLabel("●", parent=card)
        dot.setObjectName("stage_dot")
        dot.setProperty("stage-status", stage.status)
        layout.addWidget(dot)

        name_lbl = QLabel(stage.name, parent=card)
        name_lbl.setObjectName("stage_name")
        name_lbl.setProperty("stage-status", stage.status)
        layout.addWidget(name_lbl, 1)

        status_text = _STATUS_TR.get(stage.status, stage.status)
        badge = QLabel(status_text, parent=card)
        badge.setObjectName("stage_badge")
        badge.setProperty("stage-status", stage.status)
        layout.addWidget(badge)

        if is_active:
            btn = QPushButton("Tamamla", parent=card)
            btn.setProperty("cssClass", "btn-primary")
            btn.setMinimumSize(80, 28)
            btn.clicked.connect(
                lambda checked=False, sid=stage.id: self.complete_requested.emit(sid)
            )
            layout.addWidget(btn)
        elif is_pending and not has_active:
            btn = QPushButton("Aktif Et", parent=card)
            btn.setProperty("cssClass", "btn-secondary")
            btn.setMinimumSize(80, 28)
            btn.clicked.connect(
                lambda checked=False, sid=stage.id: self.activate_requested.emit(sid)
            )
            layout.addWidget(btn)

        return card
