from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from controllers.decision_controller import DecisionController
from core.managers.icon_manager import Icons
from core.managers.theme_manager import ThemeManager
from domain.models.decision_record import DecisionRecord
from presentation.dialogs.decision_dialog import DecisionDialog
from presentation.dimensions import Spacing
from presentation.utils.i18n import tr
from presentation.widgets.icon_action_button import IconActionButton

_STATUS_META: dict[str, tuple[str, str]] = {
    "DRAFT":      ("#78909C", "Taslak"),
    "ACCEPTED":   ("#43A047", "Kabul Edildi"),
    "SUPERSEDED": ("#FB8C00", "Güncellendi"),
    "CANCELLED":  ("#E53935", "İptal Edildi"),
}


class _DecisionRow(QFrame):
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, decision: DecisionRecord, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.decision_id = decision.id
        self.setProperty("cssClass", "panel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.XS)

        top = QHBoxLayout()
        top.setSpacing(Spacing.SM)

        color, label = _STATUS_META.get(decision.status, ("#888888", decision.status))
        badge = QLabel(label, parent=self)
        badge.setStyleSheet(
            f"QLabel {{ background-color: transparent; color: {color};"
            f" border: 1px solid {color}; border-radius: 4px; padding: 1px 8px;"
            f" font-size: 11px; font-weight: 600; }}"
        )
        top.addWidget(badge)

        title_lbl = QLabel(decision.title, parent=self)
        title_lbl.setProperty("cssClass", "text-primary")
        title_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")
        top.addWidget(title_lbl, 1)

        muted = ThemeManager.instance().color("text_muted")
        edit_btn = IconActionButton(
            Icons.PENCIL, muted, "#4A90D9", tr("action_edit", "Düzenle"), parent=self
        )
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.decision_id))
        top.addWidget(edit_btn)

        del_btn = IconActionButton(
            Icons.TRASH, muted, "#E53935", tr("action_delete", "Sil"), parent=self
        )
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.decision_id))
        top.addWidget(del_btn)

        layout.addLayout(top)

        if decision.decision:
            dec_lbl = QLabel(decision.decision, parent=self)
            dec_lbl.setProperty("cssClass", "text-secondary")
            dec_lbl.setWordWrap(True)
            dec_lbl.setStyleSheet("font-size: 12px; padding-left: 2px;")
            layout.addWidget(dec_lbl)


class DecisionListWidget(QWidget):
    """Proje kararlarını modern satır düzeniyle listeleyen sekme widget'ı."""

    def __init__(self, controller: DecisionController, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._project_id: int | None = None
        self._rows: dict[int, _DecisionRow] = {}
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.XL)

        header = QHBoxLayout()
        title = QLabel(tr("decisions_title", "Karar Kayıtları"), parent=self)
        title.setProperty("cssClass", "title-small")
        header.addWidget(title)
        header.addStretch()

        self._add_btn = QPushButton(tr("decisions_add_btn", "+ Karar Ekle"), parent=self)
        self._add_btn.setProperty("cssClass", "btn-primary")
        self._add_btn.clicked.connect(self._on_add_decision)
        header.addWidget(self._add_btn)
        layout.addLayout(header)

        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAutoFillBackground(False)
        scroll.viewport().setAutoFillBackground(False)

        self._container = QWidget(parent=scroll)
        self._container.setProperty("cssClass", "transparent-bg")
        self._list_layout = QVBoxLayout(self._container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(Spacing.SM)
        self._list_layout.addStretch()

        scroll.setWidget(self._container)
        layout.addWidget(scroll, 1)

    def _connect_signals(self) -> None:
        self._controller.decisions_loaded.connect(self._on_decisions_loaded)
        self._controller.decision_created.connect(self._refresh)
        self._controller.decision_updated.connect(self._refresh)
        self._controller.decision_deleted.connect(self._refresh)

    def set_project(self, project_id: int) -> None:
        self._project_id = project_id
        self._refresh()

    def _refresh(self, *args) -> None:
        if self._project_id:
            self._controller.load_project_decisions(self._project_id)

    def _on_decisions_loaded(self, decisions: list[DecisionRecord]) -> None:
        self._clear()

        if not decisions:
            empty = QLabel(tr("decisions_empty", "Henüz karar kaydı yok."), parent=self._container)
            empty.setProperty("cssClass", "text-muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("padding: 24px 0;")
            self._list_layout.insertWidget(0, empty)
            return

        for d in decisions:
            row = _DecisionRow(d, parent=self._container)
            row.edit_requested.connect(self._on_edit)
            row.delete_requested.connect(self._on_delete_confirm)
            pos = self._list_layout.count() - 1
            self._list_layout.insertWidget(pos, row)
            self._rows[d.id] = row



    def _clear(self) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._rows.clear()

    def _on_add_decision(self) -> None:
        if not self._project_id:
            return
        dialog = DecisionDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            decision = str(data.pop("decision"))
            self._controller.create_decision(self._project_id, title, decision, **data)

    def _on_edit(self, decision_id: int) -> None:
        record = self._controller.get_decision_sync(decision_id)
        if record:
            dialog = DecisionDialog(parent=self, decision=record)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._controller.update_decision(decision_id, **dialog.get_data())

    def _on_delete_confirm(self, decision_id: int) -> None:
        reply = QMessageBox.question(
            self,
            tr("action_cancel_record", "İptal Et"),
            tr("decisions_cancel_confirm", "Bu kararı iptal etmek istediğinize emin misiniz?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.delete_decision(decision_id)
