from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controllers.decision_controller import DecisionController
from domain.enums.decision_status import DecisionStatus
from domain.models.decision_record import DecisionRecord
from presentation.dialogs.decision_dialog import DecisionDialog


class DecisionListWidget(QWidget):
    """Proje kararlarını listeleyen sekme widget'ı."""

    def __init__(self, controller: DecisionController, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._project_id: int | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Karar Kayıtları", parent=self)
        title.setProperty("cssClass", "title-small")
        header.addWidget(title)
        
        header.addStretch()
        
        self._add_btn = QPushButton("+ Karar Ekle", parent=self)
        self._add_btn.setProperty("cssClass", "btn-primary")
        self._add_btn.clicked.connect(self._on_add_decision)
        header.addWidget(self._add_btn)
        
        layout.addLayout(header)

        self._list_widget = QListWidget(parent=self)
        self._list_widget.setProperty("cssClass", "panel")
        self._list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list_widget.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._list_widget)

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
        self._list_widget.clear()
        for d in decisions:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, d.id)
            
            # Simple text representation for now
            status_text = d.status
            if d.status == DecisionStatus.ACCEPTED.value:
                status_text = "✅ KABUL"
            elif d.status == DecisionStatus.CANCELLED.value:
                status_text = "❌ İPTAL"
                
            text = f"{d.title}\nDurum: {status_text}\nKarar: {d.decision}"
            item.setText(text)
            self._list_widget.addItem(item)

    def _on_add_decision(self) -> None:
        if not self._project_id:
            return
            
        dialog = DecisionDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            decision = str(data.pop("decision"))
            self._controller.create_decision(self._project_id, title, decision, **data)

    def _on_context_menu(self, pos) -> None:
        item = self._list_widget.itemAt(pos)
        if not item:
            return
            
        decision_id = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
                           
        edit_action = menu.addAction("Düzenle")
        delete_action = menu.addAction("İptal Et")
        
        action = menu.exec(self._list_widget.mapToGlobal(pos))
        if action == edit_action:
            record = self._controller.get_decision_sync(decision_id)
            if record:
                dialog = DecisionDialog(parent=self, decision=record)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self._controller.update_decision(decision_id, **dialog.get_data())
        elif action == delete_action:
            reply = QMessageBox.question(self, "İptal Et", "Bu kararı iptal etmek istediğinize emin misiniz?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self._controller.delete_decision(decision_id)
