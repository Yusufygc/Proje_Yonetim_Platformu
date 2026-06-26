from __future__ import annotations

import webbrowser

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

from controllers.resource_controller import ResourceController
from core.managers.icon_manager import Icons
from core.managers.theme_manager import ThemeManager
from domain.models.resource import Resource
from presentation.dialogs.resource_dialog import ResourceDialog
from presentation.dimensions import Spacing
from presentation.utils.i18n import tr
from presentation.widgets.icon_action_button import IconActionButton

_RESOURCE_TYPE_META: dict[str, tuple[str, str]] = {
    "DOCUMENT": ("#42A5F5", "Doküman"),
    "ARTICLE":  ("#26A69A", "Makale"),
    "VIDEO":    ("#EF5350", "Video"),
    "GITHUB":   ("#78909C", "GitHub"),
    "DESIGN":   ("#AB47BC", "Tasarım"),
    "API":      ("#FF7043", "API"),
    "TOOL":     ("#66BB6A", "Araç"),
    "OTHER":    ("#9E9E9E", "Diğer"),
}


class _ResourceCard(QFrame):
    open_requested = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(
        self,
        resource: Resource,
        accent_color: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.resource_id = resource.id
        self._url = resource.url or ""

        self.setProperty("cssClass", "panel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.XS)

        # ── Üst satır: tip badge + başlık + aksiyonlar ──────────────────────
        top = QHBoxLayout()
        top.setSpacing(Spacing.SM)

        color, label = _RESOURCE_TYPE_META.get(resource.resource_type, ("#9E9E9E", resource.resource_type))
        badge = QLabel(label, parent=self)
        badge.setStyleSheet(
            f"QLabel {{ background-color: transparent; color: {color};"
            f" border: 1px solid {color}; border-radius: 4px; padding: 1px 8px;"
            f" font-size: 11px; font-weight: 600; }}"
        )
        top.addWidget(badge)

        title_lbl = QLabel(resource.title, parent=self)
        title_lbl.setProperty("cssClass", "text-primary")
        title_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")
        top.addWidget(title_lbl, 1)

        muted = ThemeManager.instance().color("text_muted")
        open_btn = IconActionButton(
            Icons.EXTERNAL_LINK, accent_color, accent_color,
            tr("resources_open_browser", "Tarayıcıda Aç"), parent=self,
        )
        open_btn.clicked.connect(lambda: self.open_requested.emit(self.resource_id))
        top.addWidget(open_btn)

        edit_btn = IconActionButton(
            Icons.PENCIL, muted, "#4A90D9", tr("action_edit", "Düzenle"), parent=self
        )
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.resource_id))
        top.addWidget(edit_btn)

        del_btn = IconActionButton(
            Icons.TRASH, muted, "#E53935", tr("action_delete", "Sil"), parent=self
        )
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.resource_id))
        top.addWidget(del_btn)

        layout.addLayout(top)

        # ── URL ─────────────────────────────────────────────────────────────
        if resource.url:
            url_lbl = QLabel(resource.url, parent=self)
            url_lbl.setStyleSheet(
                f"color: {accent_color}; font-size: 11px;"
            )
            url_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            url_lbl.setWordWrap(False)
            layout.addWidget(url_lbl)

        # ── Açıklama ────────────────────────────────────────────────────────
        if resource.description:
            desc_lbl = QLabel(resource.description, parent=self)
            desc_lbl.setProperty("cssClass", "text-secondary")
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("font-size: 11px;")
            layout.addWidget(desc_lbl)


class ResourceListWidget(QWidget):
    """Proje kaynaklarını kart düzeniyle listeleyen sekme widget'ı."""

    def __init__(
        self,
        controller: ResourceController,
        parent: QWidget = None,
        theme: ThemeManager | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._theme = theme or ThemeManager.instance()
        self._project_id: int | None = None
        self._cards: dict[int, _ResourceCard] = {}
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

        scroll = QScrollArea(parent=self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setAutoFillBackground(False)
        scroll.viewport().setAutoFillBackground(False)

        self._container = QWidget(parent=scroll)
        self._container.setProperty("cssClass", "transparent-bg")
        self._card_layout = QVBoxLayout(self._container)
        self._card_layout.setContentsMargins(0, 0, 0, 0)
        self._card_layout.setSpacing(Spacing.MD)
        self._card_layout.addStretch()

        scroll.setWidget(self._container)
        layout.addWidget(scroll, 1)

    def _connect_signals(self) -> None:
        self._controller.resources_loaded.connect(self._on_resources_loaded)
        self._controller.resource_created.connect(self._refresh)
        self._controller.resource_updated.connect(self._refresh)
        self._controller.resource_deleted.connect(self._refresh)
        self._theme.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _: str) -> None:
        self._refresh()

    def set_project(self, project_id: int) -> None:
        self._project_id = project_id
        self._refresh()

    def _refresh(self, *args) -> None:
        if self._project_id:
            self._controller.load_project_resources(self._project_id)

    def _on_resources_loaded(self, resources: list[Resource]) -> None:
        self._clear()
        accent = self._theme.color("accent_start")

        if not resources:
            empty = QLabel(tr("resources_empty", "Henüz kaynak eklenmedi."), parent=self._container)
            empty.setProperty("cssClass", "text-muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("padding: 24px 0;")
            self._card_layout.insertWidget(0, empty)
            return

        for r in resources:
            card = _ResourceCard(r, accent_color=accent, parent=self._container)
            card.open_requested.connect(self._on_open)
            card.edit_requested.connect(self._on_edit)
            card.delete_requested.connect(self._on_delete_confirm)
            self._card_layout.insertWidget(self._card_layout.count() - 1, card)
            self._cards[r.id] = card

    def _clear(self) -> None:
        while self._card_layout.count() > 1:
            item = self._card_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._cards.clear()

    def _on_add_resource(self) -> None:
        if not self._project_id:
            return
        dialog = ResourceDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            url = str(data.pop("url"))
            self._controller.create_resource(self._project_id, title, url, **data)

    def _on_open(self, resource_id: int) -> None:
        card = self._cards.get(resource_id)
        if card and card._url:
            webbrowser.open(card._url)

    def _on_edit(self, resource_id: int) -> None:
        resource = self._controller.get_resource_sync(resource_id)
        if resource:
            dialog = ResourceDialog(parent=self, resource=resource)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._controller.update_resource(resource_id, **dialog.get_data())

    def _on_delete_confirm(self, resource_id: int) -> None:
        reply = QMessageBox.question(
            self,
            tr("action_delete", "Sil"),
            tr("resources_delete_confirm", "Bu kaynağı silmek istediğinize emin misiniz?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._controller.delete_resource(resource_id)
