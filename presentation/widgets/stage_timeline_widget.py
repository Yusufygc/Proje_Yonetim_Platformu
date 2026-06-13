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

from core.managers.theme_manager import ThemeManager
from domain.enums.stage_status import StageStatus
from domain.models.project_stage import ProjectStage
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


def _status_labels() -> dict[str, str]:
    """Aşama durum etiketleri; dil değişimi her render'da yansısın diye fonksiyon."""
    return {
        StageStatus.NOT_STARTED.value: tr("stage_status_not_started", "Bekliyor"),
        StageStatus.ACTIVE.value: tr("stage_status_active", "Aktif"),
        StageStatus.DONE.value: tr("stage_status_done", "Tamamlandı"),
        StageStatus.SKIPPED.value: tr("stage_status_skipped", "Atlandı"),
    }


class StageTimelineWidget(QWidget):
    """Proje aşamalarını durum göstergeleriyle listeler."""

    complete_requested = Signal(int)
    activate_requested = Signal(int)

    def __init__(self, parent: QWidget, theme: ThemeManager | None = None) -> None:
        super().__init__(parent=parent)
        self._rows_layout = QVBoxLayout(self)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(Spacing.XS)
        self._stages: list[ProjectStage] = []
        # Constructor injection tercih edilir; None ise singleton'a düşülür.
        self._theme = theme or ThemeManager.instance()
        self._theme.theme_changed.connect(self._on_theme_changed)

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
        is_pending = stage.status == StageStatus.NOT_STARTED.value

        card = QFrame(parent=self)
        card.setObjectName("stage_card")
        card.setProperty("stage-status", stage.status)
        # Sabit yükseklik: 8 aşamalık liste detay panelin yarısını yutmasın.
        card.setFixedHeight(Size.STAGE_ROW_H)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, Spacing.XS, 14, Spacing.XS)
        layout.setSpacing(Spacing.MD)

        dot = QLabel("●", parent=card)
        dot.setObjectName("stage_dot")
        dot.setProperty("stage-status", stage.status)
        layout.addWidget(dot)

        name_lbl = QLabel(stage.name, parent=card)
        name_lbl.setObjectName("stage_name")
        name_lbl.setProperty("stage-status", stage.status)
        layout.addWidget(name_lbl, 1)

        status_text = _status_labels().get(stage.status, stage.status)
        badge = QLabel(status_text, parent=card)
        badge.setObjectName("stage_badge")
        badge.setProperty("stage-status", stage.status)
        layout.addWidget(badge)

        if is_active:
            btn = QPushButton(tr("stage_complete_btn", "Tamamla"), parent=card)
            btn.setProperty("cssClass", "btn-primary")
            btn.setMinimumSize(Size.BTN_MD_W, Size.STAGE_BTN_H)
            btn.clicked.connect(
                lambda checked=False, sid=stage.id: self.complete_requested.emit(sid)
            )
            layout.addWidget(btn)
        elif is_pending and not has_active:
            btn = QPushButton(tr("stage_activate_btn", "Aktif Et"), parent=card)
            btn.setProperty("cssClass", "btn-secondary")
            btn.setMinimumSize(Size.BTN_MD_W, Size.STAGE_BTN_H)
            btn.clicked.connect(
                lambda checked=False, sid=stage.id: self.activate_requested.emit(sid)
            )
            layout.addWidget(btn)

        return card
