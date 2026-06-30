"""
Memo sayfası — proje bağımsız, otomatik kaydedilen not defteri.
Sol panel: memo listesi. Sağ panel: başlık + QTextEdit editörü.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from controllers.memo_controller import MemoController
from domain.models.memo import Memo
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr


class MemoPage(QWidget):
    """Sol liste + sağ editör düzeninde proje bağımsız not defteri sayfası."""

    def __init__(self, parent: QWidget, controller: MemoController) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._selected_memo_id: int | None = None
        self._setup_ui()
        self._connect_signals()
        self._controller.load_all()

    # ── UI Kurulumu ──────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.PAGE, Spacing.PAGE, Spacing.PAGE, Spacing.PAGE)
        layout.setSpacing(Spacing.LG)

        layout.addWidget(self._build_header())

        splitter = QSplitter(Qt.Orientation.Horizontal, parent=self)
        splitter.setObjectName("memo_splitter")
        splitter.addWidget(self._build_left_panel(splitter))
        splitter.addWidget(self._build_right_panel(splitter))
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

    def _build_header(self) -> QWidget:
        header = QWidget(parent=self)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD)

        title = QLabel(tr("nav_memo", "Notlarım"), parent=header)
        title.setProperty("cssClass", "title-medium")
        layout.addWidget(title)
        layout.addStretch()

        self._new_btn = QPushButton(tr("memo_new_btn", "+ Yeni Memo"), parent=header)
        self._new_btn.setProperty("cssClass", "btn-primary")
        self._new_btn.setMinimumSize(Size.BTN_MD_W, Size.BTN_MD_H38)
        self._new_btn.clicked.connect(self._on_new_memo)
        layout.addWidget(self._new_btn)

        return header

    def _build_left_panel(self, splitter: QSplitter) -> QFrame:
        panel = QFrame(parent=splitter)
        panel.setProperty("cssClass", "panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        layout.setSpacing(0)

        self._list_widget = QListWidget(parent=panel)
        self._list_widget.setObjectName("memo_list")
        layout.addWidget(self._list_widget, 1)

        self._list_empty_label = QLabel(
            tr("memo_list_empty", "Henüz memo yok.\n+ Yeni Memo ile başlayın."),
            parent=panel,
        )
        self._list_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._list_empty_label.setProperty("cssClass", "text-muted")
        self._list_empty_label.setWordWrap(True)
        self._list_empty_label.hide()
        layout.addWidget(self._list_empty_label)

        return panel

    def _build_right_panel(self, splitter: QSplitter) -> QFrame:
        panel = QFrame(parent=splitter)
        panel.setProperty("cssClass", "panel")
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Editör alanı (seçim yokken gizli)
        self._editor_area = QWidget(parent=panel)
        editor_layout = QVBoxLayout(self._editor_area)
        editor_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.MD)
        editor_layout.setSpacing(Spacing.SM)

        self._title_edit = QLineEdit(parent=self._editor_area)
        self._title_edit.setPlaceholderText(tr("memo_title_placeholder", "Memo başlığı..."))
        self._title_edit.setMinimumHeight(Size.INPUT_H_LG)
        self._title_edit.setProperty("cssClass", "title-small")
        editor_layout.addWidget(self._title_edit)

        divider = QFrame(parent=self._editor_area)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setProperty("cssClass", "divider")
        editor_layout.addWidget(divider)

        self._editor = QTextEdit(parent=self._editor_area)
        self._editor.setPlaceholderText(tr("memo_body_placeholder", "Notlarınızı buraya yazın..."))
        self._editor.setFrameShape(QFrame.Shape.NoFrame)
        editor_layout.addWidget(self._editor, 1)

        editor_layout.addWidget(self._build_editor_bottom())

        self._editor_area.hide()
        outer.addWidget(self._editor_area, 1)

        # Boş durum etiketi
        self._editor_empty_label = QLabel(
            tr("memo_select_hint", "Bir memo seçin veya yeni oluşturun."),
            parent=panel,
        )
        self._editor_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._editor_empty_label.setProperty("cssClass", "text-muted")
        outer.addWidget(self._editor_empty_label, 1)

        return panel

    def _build_editor_bottom(self) -> QWidget:
        bar = QWidget(parent=self._editor_area)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD)

        self._autosave_label = QLabel("", parent=bar)
        self._autosave_label.setProperty("cssClass", "text-muted")
        layout.addWidget(self._autosave_label)
        layout.addStretch()

        self._delete_btn = QPushButton(tr("action_delete", "Sil"), parent=bar)
        self._delete_btn.setProperty("cssClass", "btn-danger")
        self._delete_btn.setMinimumSize(Size.BTN_MD_W, Size.BTN_MD_H38)
        self._delete_btn.clicked.connect(self._on_delete)
        layout.addWidget(self._delete_btn)

        return bar

    # ── Sinyal Bağlantıları ─────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._controller.memos_loaded.connect(self._on_memos_loaded)
        self._controller.memo_created.connect(self._on_memo_created)
        self._controller.memo_updated.connect(self._on_memo_updated)
        self._controller.memo_deleted.connect(self._on_memo_deleted)
        self._controller.error_occurred.connect(self._on_error)

        self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(1000)
        self._autosave_timer.timeout.connect(self._save_current)

        self._title_edit.textChanged.connect(self._autosave_timer.start)
        self._editor.textChanged.connect(self._autosave_timer.start)

    # ── Liste Sinyal İşleyicileri ────────────────────────────────────────────

    def _on_memos_loaded(self, memos: list[Memo]) -> None:
        self._list_widget.blockSignals(True)
        self._list_widget.clear()
        has_items = bool(memos)

        for memo in memos:
            item = QListWidgetItem(memo.title)
            item.setData(Qt.ItemDataRole.UserRole, memo.id)
            self._list_widget.addItem(item)
            if memo.id == self._selected_memo_id:
                item.setSelected(True)

        self._list_widget.blockSignals(False)
        self._list_empty_label.setVisible(not has_items)
        self._list_widget.setVisible(has_items)

    def _on_memo_created(self, memo: Memo) -> None:
        self._selected_memo_id = memo.id
        self._controller.load_all()

    def _on_memo_updated(self, memo: Memo) -> None:
        self._autosave_label.setText(tr("memo_saved", "Kaydedildi"))
        QTimer.singleShot(2000, lambda: self._autosave_label.setText(""))
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == memo.id:
                item.setText(memo.title)
                break

    def _on_memo_deleted(self, memo_id: int) -> None:
        self._selected_memo_id = None
        self._controller.load_all()
        self._show_empty_state()

    def _on_error(self, message: str) -> None:
        self._autosave_label.setText(f"Hata: {message}")

    # ── Seçim / Yükleme ────────────────────────────────────────────────────

    def _on_selection_changed(self) -> None:
        self._autosave_timer.stop()

        # Mevcut memoyu seçim değişmeden önce kaydet
        if self._selected_memo_id is not None:
            title = self._title_edit.text().strip()
            body = self._editor.toPlainText()
            if title:
                self._controller.update(self._selected_memo_id, title=title, body=body)

        selected = self._list_widget.selectedItems()
        if not selected:
            self._selected_memo_id = None
            self._show_empty_state()
            return

        memo_id = selected[0].data(Qt.ItemDataRole.UserRole)
        if memo_id == self._selected_memo_id:
            return
        self._load_memo(memo_id)

    def _load_memo(self, memo_id: int) -> None:
        memo = self._controller.get_sync(memo_id)
        if memo is None:
            return
        self._selected_memo_id = memo.id
        self._autosave_timer.stop()

        self._title_edit.blockSignals(True)
        self._editor.blockSignals(True)
        self._title_edit.setText(memo.title)
        self._editor.setPlainText(memo.body)
        self._title_edit.blockSignals(False)
        self._editor.blockSignals(False)

        self._autosave_label.setText("")
        self._show_editor()

    # ── Görünüm Yardımcıları ────────────────────────────────────────────────

    def _show_editor(self) -> None:
        self._editor_empty_label.hide()
        self._editor_area.show()

    def _show_empty_state(self) -> None:
        self._editor_area.hide()
        self._editor_empty_label.show()

    # ── Buton İşleyicileri ──────────────────────────────────────────────────

    def _on_new_memo(self) -> None:
        self._autosave_timer.stop()
        if self._selected_memo_id is not None:
            title = self._title_edit.text().strip()
            body = self._editor.toPlainText()
            if title:
                self._controller.update(self._selected_memo_id, title=title, body=body)

        self._list_widget.clearSelection()
        self._selected_memo_id = None

        self._title_edit.blockSignals(True)
        self._editor.blockSignals(True)
        self._title_edit.clear()
        self._editor.clear()
        self._title_edit.blockSignals(False)
        self._editor.blockSignals(False)

        self._autosave_label.setText("")
        self._show_editor()
        self._title_edit.setFocus()

    def _on_delete(self) -> None:
        if self._selected_memo_id is None:
            return
        reply = QMessageBox.question(
            self,
            tr("action_delete", "Sil"),
            tr("memo_delete_confirm", "Bu memo silinecek. Emin misiniz?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._autosave_timer.stop()
            self._controller.delete(self._selected_memo_id)

    # ── Otomatik Kayıt ──────────────────────────────────────────────────────

    def _save_current(self) -> None:
        title = self._title_edit.text().strip()
        body = self._editor.toPlainText()

        if self._selected_memo_id is not None:
            if title:
                self._autosave_label.setText(tr("memo_saving", "Kaydediliyor..."))
                self._controller.update(self._selected_memo_id, title=title, body=body)
        elif title:
            self._controller.create(title, body)
