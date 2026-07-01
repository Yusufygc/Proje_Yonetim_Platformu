"""
Proje aşamalarını dikey liste olarak gösteren bileşen.
complete_requested(int) ve activate_requested(int) sinyalleri üzerinden aksiyon iletir.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.managers.icon_manager import IconManager, Icons
from core.managers.theme_manager import ThemeManager
from domain.enums.stage_status import StageStatus
from domain.models.project_stage import ProjectStage
from presentation.dimensions import Shadow, Size, Spacing
from presentation.utils.i18n import tr
from presentation.utils.ui_utils import apply_shadow


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
        self.setUpdatesEnabled(False)
        try:
            while self._rows_layout.count() > 0:
                item = self._rows_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            has_active = any(s.status == StageStatus.ACTIVE.value for s in stages)
            for stage in stages:
                self._rows_layout.addWidget(self._build_row(stage, has_active))
        finally:
            self.setUpdatesEnabled(True)

    def _build_row(self, stage: ProjectStage, has_active: bool) -> QFrame:
        """Tek bir aşama satırı oluşturur; duruma göre buton ve QSS property uygular."""
        card = QFrame(parent=self)
        card.setObjectName("stage_card")
        card.setProperty("stage-status", stage.status)
        # Sabit yükseklik: 8 aşamalık liste detay panelin yarısını yutmasın.
        card.setFixedHeight(Size.STAGE_ROW_H)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, Spacing.XS, 14, Spacing.XS)
        layout.setSpacing(Spacing.MD)

        layout.addWidget(self._build_dot(card, stage.status), 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._build_name_label(card, stage), 1)
        self._add_action_button(layout, card, stage, has_active)

        if stage.status == StageStatus.ACTIVE.value:
            # Aktif aşamayı diğerlerinden ayıran accent renkli parlama.
            apply_shadow(
                card,
                blur_radius=Shadow.GLOW_BLUR,
                y_offset=0,
                alpha=Shadow.GLOW_ALPHA,
                color=QColor(self._theme.color("stage_active")),
            )

        return card

    def _build_dot(self, card: QFrame, status: str) -> QWidget:
        """Tamamlanan aşamada tik ikonu, aksi halde durum renkli daire döndürür."""
        if status == StageStatus.DONE.value:
            check = self._build_check_icon(card)
            if check is not None:
                return check
        # Sabit boyutlu daire; unicode karakterin font-bağımlı dikey kaymasını önler.
        dot = QFrame(parent=card)
        dot.setObjectName("stage_dot")
        dot.setProperty("stage-status", status)
        dot.setFixedSize(Size.STAGE_DOT, Size.STAGE_DOT)
        return dot

    def _build_check_icon(self, card: QFrame) -> QLabel | None:
        """Tamamlanan aşama için tik ikonu; ikon yöneticisi yoksa None (daireye düşülür)."""
        icons = IconManager.try_instance()
        if icons is None:
            return None
        label = QLabel(parent=card)
        pixmap = icons.get_icon(Icons.SQUARE_CHECK, self._theme.color("stage_done")).pixmap(
            Size.STAGE_CHECK, Size.STAGE_CHECK
        )
        label.setPixmap(pixmap)
        label.setFixedSize(Size.STAGE_CHECK, Size.STAGE_CHECK)
        return label

    def _build_name_label(self, card: QFrame, stage: ProjectStage) -> QLabel:
        name_lbl = QLabel(stage.name, parent=card)
        name_lbl.setObjectName("stage_name")
        name_lbl.setProperty("stage-status", stage.status)
        return name_lbl

    def _add_action_button(
        self,
        layout: QHBoxLayout,
        card: QFrame,
        stage: ProjectStage,
        has_active: bool,
    ) -> None:
        is_active = stage.status == StageStatus.ACTIVE.value
        is_pending = stage.status == StageStatus.NOT_STARTED.value
        if is_active:
            btn = QPushButton(tr("stage_complete_btn", "Tamamla"), parent=card)
            btn.setProperty("cssClass", "btn-primary")
            btn.setMinimumSize(Size.BTN_MD_W, Size.STAGE_BTN_H)
            btn.clicked.connect(
                lambda checked=False, sid=stage.id: self.complete_requested.emit(sid)
            )
        elif is_pending and not has_active:
            btn = QPushButton(tr("stage_activate_btn", "Aktif Et"), parent=card)
            btn.setProperty("cssClass", "btn-secondary")
            btn.setMinimumSize(Size.BTN_MD_W, Size.STAGE_BTN_H)
            btn.clicked.connect(
                lambda checked=False, sid=stage.id: self.activate_requested.emit(sid)
            )
        else:
            return
        layout.addSpacing(Spacing.SM)
        layout.addWidget(btn)
