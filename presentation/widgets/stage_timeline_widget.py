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

_STATUS_THEME_KEYS: dict[str, tuple[str, str]] = {
    StageStatus.NOT_STARTED.value: ("Bekliyor", "text_secondary"),
    StageStatus.ACTIVE.value: ("Aktif", "success"),
    StageStatus.DONE.value: ("Tamamlandı", "accent_start"),
    StageStatus.SKIPPED.value: ("Atlandı", "text_muted"),
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

    def update_stages(self, stages: list[ProjectStage]) -> None:
        """Aşama listesini temizler ve yeniden oluşturur."""
        while self._rows_layout.count() > 0:
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        has_active = any(s.status == StageStatus.ACTIVE.value for s in stages)
        for stage in stages:
            self._rows_layout.addWidget(self._build_row(stage, has_active))

    def _build_row(self, stage: ProjectStage, has_active: bool) -> QFrame:
        """Tek bir aşama satırı oluşturur; duruma göre buton ve stil uygular."""
        from core.managers.theme_manager import ThemeManager
        theme_mgr = ThemeManager.instance()

        is_active = stage.status == StageStatus.ACTIVE.value
        is_completed = stage.status == StageStatus.DONE.value
        is_pending = stage.status == StageStatus.NOT_STARTED.value

        card = QFrame(parent=self)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        dot_color = stage.color if (is_active or is_completed) else theme_mgr.color("border")
        dot = QLabel("●", parent=card)
        dot.setStyleSheet(f"font-size: 10px; color: {dot_color};")
        layout.addWidget(dot)

        name_color = theme_mgr.color("text_primary") if is_active else (theme_mgr.color("accent_start") if is_completed else theme_mgr.color("text_secondary"))
        name_weight = "700" if is_active else "500"
        name_lbl = QLabel(stage.name, parent=card)
        name_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: {name_weight}; color: {name_color};"
        )
        layout.addWidget(name_lbl, 1)

        status_text, theme_key = _STATUS_THEME_KEYS.get(stage.status, (stage.status, "text_secondary"))
        status_color = theme_mgr.color(theme_key)
        badge = QLabel(status_text, parent=card)
        badge.setStyleSheet(
            f"font-size: 10px; font-weight: 600; color: {status_color};"
            f" background: {status_color}22; padding: 3px 8px; border-radius: 8px;"
        )
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

        border_color = stage.color if is_active else theme_mgr.color("border")
        bg_color = f"{stage.color}15" if is_active else "transparent"
        card.setStyleSheet(
            f"QFrame {{ background: {bg_color}; border-left: 2px solid {border_color};"
            f" border-radius: 4px; }}"
        )
        return card
