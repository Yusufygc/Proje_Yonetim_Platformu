from __future__ import annotations

import webbrowser

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

from PySide6.QtGui import QColor

from controllers.resource_controller import ResourceController
from core.managers.theme_manager import ThemeManager
from domain.models.resource import Resource
from presentation.dialogs.resource_dialog import ResourceDialog
from presentation.dimensions import Spacing
from presentation.utils.i18n import tr


class ResourceListWidget(QWidget):
    """Proje kaynaklarını listeleyen sekme widget'ı."""

    def __init__(
        self,
        controller: ResourceController,
        parent: QWidget = None,
        theme: ThemeManager | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        # Constructor injection tercih edilir; None ise singleton'a düşülür.
        self._theme = theme or ThemeManager.instance()
        self._project_id: int | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.XL)

        header = QHBoxLayout()
        title = QLabel(tr("resources_title", "Proje Kaynakları"), parent=self)
        title.setProperty("cssClass", "title-small")
        header.addWidget(title)

        header.addStretch()

        self._add_btn = QPushButton(tr("resources_add_btn", "+ Kaynak Ekle"), parent=self)
        self._add_btn.setProperty("cssClass", "btn-primary")
        self._add_btn.clicked.connect(self._on_add_resource)
        header.addWidget(self._add_btn)
        
        layout.addLayout(header)

        self._list_widget = QListWidget(parent=self)
        self._list_widget.setProperty("cssClass", "panel")
        self._list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list_widget.customContextMenuRequested.connect(self._on_context_menu)
        self._list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._list_widget)

    def _connect_signals(self) -> None:
        self._controller.resources_loaded.connect(self._on_resources_loaded)
        self._controller.resource_created.connect(self._refresh)
        self._controller.resource_updated.connect(self._refresh)
        self._controller.resource_deleted.connect(self._refresh)
        # Link rengi setForeground ile programatik atanır; tema değişince
        # liste yeni paletle yeniden çizilmelidir.
        self._theme.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _theme_name: str) -> None:
        self._refresh()

    def set_project(self, project_id: int) -> None:
        self._project_id = project_id
        self._refresh()

    def _refresh(self, *args) -> None:
        if self._project_id:
            self._controller.load_project_resources(self._project_id)

    def _on_resources_loaded(self, resources: list[Resource]) -> None:
        self._list_widget.clear()
        link_color = self._theme.color("accent_start")

        for r in resources:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, r.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, r.url)
            
            text = f"[{r.resource_type}] {r.title}\n{r.url}"
            if r.description:
                text += f"\n{r.description}"
                
            item.setText(text)
            item.setForeground(QColor(link_color))
            self._list_widget.addItem(item)

    def _on_add_resource(self) -> None:
        if not self._project_id:
            return
            
        dialog = ResourceDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            url = str(data.pop("url"))
            self._controller.create_resource(self._project_id, title, url, **data)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        url = item.data(Qt.ItemDataRole.UserRole + 1)
        if url:
            webbrowser.open(url)

    def _on_context_menu(self, pos) -> None:
        item = self._list_widget.itemAt(pos)
        if not item:
            return
            
        resource_id = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
                           
        open_action = menu.addAction(tr("resources_open_browser", "Tarayıcıda Aç"))
        edit_action = menu.addAction(tr("action_edit", "Düzenle"))
        delete_action = menu.addAction(tr("action_delete", "Sil"))
        
        action = menu.exec(self._list_widget.mapToGlobal(pos))
        if action == open_action:
            self._on_item_double_clicked(item)
        elif action == edit_action:
            resource = self._controller.get_resource_sync(resource_id)
            if resource:
                dialog = ResourceDialog(parent=self, resource=resource)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self._controller.update_resource(resource_id, **dialog.get_data())
        elif action == delete_action:
            reply = QMessageBox.question(
                self,
                tr("action_delete", "Sil"),
                tr("resources_delete_confirm", "Bu kaynağı silmek istediğinize emin misiniz?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._controller.delete_resource(resource_id)
