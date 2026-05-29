"""
Search Dialog - Global arama ekranı. Yazıldıkça sonuçları günceller.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controllers.search_controller import SearchController


class SearchDialog(QDialog):
    # (type, id) döner
    item_selected = Signal(str, int)

    def __init__(self, controller: SearchController, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 400)

        # parent ortalaması (opsiyonel) veya main window ortası
        if parent:
            geo = parent.geometry()
            self.move(
                geo.center().x() - self.width() // 2,
                geo.center().y() - self.height() // 2 - 100,
            )

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        main_widget = QWidget(self)
        main_widget.setObjectName("search_container")
        main_widget.setFixedSize(self.size())

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._search_input = QLineEdit(parent=self)
        self._search_input.setObjectName("search_input")
        self._search_input.setPlaceholderText("Projelerde, fikirlerde ve görevlerde ara...")
        layout.addWidget(self._search_input)

        self._list_widget = QListWidget(parent=self)
        self._list_widget.setObjectName("search_results")
        layout.addWidget(self._list_widget)

        QShortcut(QKeySequence("Esc"), self).activated.connect(self.close)

    def _connect_signals(self) -> None:
        self._search_input.textChanged.connect(self._on_text_changed)
        self._controller.search_completed.connect(self._on_search_results)
        self._list_widget.itemClicked.connect(self._on_item_clicked)
        # return tuşuna basınca seçiliyi aç
        self._search_input.returnPressed.connect(self._on_return_pressed)

    def _on_text_changed(self, text: str) -> None:
        if len(text.strip()) >= 2:
            self._controller.perform_search(text)
        else:
            self._list_widget.clear()

    def _on_search_results(self, results: dict) -> None:
        self._list_widget.clear()
        
        for p in results.get("projects", []):
            self._add_item("Proje", p["id"], p["title"], p["description"])
            
        for t in results.get("tasks", []):
            self._add_item("Görev", t["id"], t["title"], t["description"])
            
        for i in results.get("ideas", []):
            self._add_item("Fikir", i["id"], i["title"], i["description"])

        if self._list_widget.count() > 0:
            self._list_widget.setCurrentRow(0)

    def _add_item(self, type_str: str, item_id: int, title: str, desc: str) -> None:
        item = QListWidgetItem()
        # Görünüm
        item.setText(f"[{type_str}] {title}\n{desc[:80] + '...' if len(desc) > 80 else desc}")
        # Data
        item.setData(Qt.ItemDataRole.UserRole, type_str)
        item.setData(Qt.ItemDataRole.UserRole + 1, item_id)
        self._list_widget.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        type_str = item.data(Qt.ItemDataRole.UserRole)
        item_id = item.data(Qt.ItemDataRole.UserRole + 1)
        self.item_selected.emit(type_str, item_id)
        self.accept()

    def _on_return_pressed(self) -> None:
        current = self._list_widget.currentItem()
        if current:
            self._on_item_clicked(current)
            
    def showEvent(self, event):
        super().showEvent(event)
        self._search_input.setFocus()
