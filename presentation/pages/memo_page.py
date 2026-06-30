"""
Memo sayfası — zengin metin editörü ve çizim tuvali ile donatılmış not defteri.
Sol panel: memo listesi (her satırda çöp ikonu). Sağ panel: başlık + QTabWidget editörü.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QTimer, Signal
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
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from controllers.memo_controller import MemoController
from domain.models.memo import Memo
from presentation.dimensions import Size, Spacing
from presentation.utils.i18n import tr
from presentation.widgets.delete_icon_button import DeleteIconButton
from presentation.widgets.drawing_canvas import DrawingCanvas, DrawingToolbar
from presentation.widgets.format_toolbar import FormatToolbar
from presentation.widgets.voice_input_button import attach_voice_button

_MEMO_ROW_H = 52


class MemoRowWidget(QWidget):
    """Memo liste satırı: başlık + sağ tarafta çöp kutusu ikonu."""

    delete_requested = Signal(int)

    def __init__(self, memo: Memo, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.memo_id = memo.id
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 10, 6)
        layout.setSpacing(8)

        self._title_lbl = QLabel(memo.title, parent=self)
        layout.addWidget(self._title_lbl, 1)

        del_btn = DeleteIconButton(parent=self)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.memo_id))
        layout.addWidget(del_btn, 0, Qt.AlignmentFlag.AlignVCenter)

    def update_title(self, title: str) -> None:
        self._title_lbl.setText(title)


class MemoListItem(QListWidgetItem):
    def __init__(self, memo: Memo) -> None:
        super().__init__()
        self.setData(Qt.ItemDataRole.UserRole, memo.id)
        self.setSizeHint(QSize(0, _MEMO_ROW_H))


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
        self._list_widget = QListWidget(parent=panel)
        self._list_widget.setObjectName("memo_list")
        layout.addWidget(self._list_widget)
        self._list_empty_label = QLabel(
            tr("memo_list_empty", "Henüz memo yok.\n+ Yeni Memo ile başlayın."),
            parent=panel,
        )
        self._list_empty_label.setProperty("cssClass", "text-secondary")
        self._list_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._list_empty_label.hide()
        layout.addWidget(self._list_empty_label)
        return panel

    def _build_right_panel(self, splitter: QSplitter) -> QFrame:
        panel = QFrame(parent=splitter)
        panel.setProperty("cssClass", "panel")
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
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
        editor_layout.addWidget(self._build_editor_tabs(), 1)
        editor_layout.addWidget(self._build_editor_bottom())
        self._editor_area.hide()
        outer.addWidget(self._editor_area, 1)
        self._editor_empty_label = QLabel(
            tr("memo_select_hint", "Bir memo seçin veya yeni oluşturun."),
            parent=panel,
        )
        self._editor_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._editor_empty_label.setProperty("cssClass", "text-muted")
        outer.addWidget(self._editor_empty_label, 1)
        return panel

    def _build_editor_tabs(self) -> QTabWidget:
        self._tab_widget = QTabWidget(parent=self._editor_area)

        text_tab = QWidget(parent=self._tab_widget)
        text_layout = QVBoxLayout(text_tab)
        text_layout.setContentsMargins(0, Spacing.XS, 0, 0)
        text_layout.setSpacing(Spacing.XS)
        self._editor = QTextEdit(parent=text_tab)
        self._editor.setAcceptRichText(True)
        self._editor.setPlaceholderText(tr("memo_body_placeholder", "Notlarınızı buraya yazın..."))
        self._editor.setFrameShape(QFrame.Shape.NoFrame)
        self._format_toolbar = FormatToolbar(self._editor, parent=text_tab)
        text_layout.addWidget(self._format_toolbar)
        text_layout.addWidget(attach_voice_button(self._editor, text_tab), 1)
        self._tab_widget.addTab(text_tab, tr("memo_tab_text", "Metin"))

        drawing_tab = QWidget(parent=self._tab_widget)
        drawing_layout = QVBoxLayout(drawing_tab)
        drawing_layout.setContentsMargins(0, Spacing.XS, 0, 0)
        drawing_layout.setSpacing(Spacing.XS)
        self._canvas = DrawingCanvas(parent=drawing_tab)
        self._drawing_toolbar = DrawingToolbar(self._canvas, parent=drawing_tab)
        drawing_layout.addWidget(self._drawing_toolbar)
        drawing_layout.addWidget(self._canvas, 1)
        self._tab_widget.addTab(drawing_tab, tr("memo_tab_drawing", "✏ Çizim"))

        return self._tab_widget

    def _build_editor_bottom(self) -> QWidget:
        bar = QWidget(parent=self._editor_area)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.MD)
        self._autosave_label = QLabel("", parent=bar)
        self._autosave_label.setProperty("cssClass", "text-muted")
        layout.addWidget(self._autosave_label)
        layout.addStretch()
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
        self._canvas.drawing_modified.connect(self._autosave_timer.start)

    # ── Liste Sinyal İşleyicileri ────────────────────────────────────────────

    def _on_memos_loaded(self, memos: list[Memo]) -> None:
        self._list_widget.blockSignals(True)
        self._list_widget.clear()
        if not memos:
            self._list_widget.hide()
            self._list_empty_label.show()
        else:
            self._list_empty_label.hide()
            self._list_widget.show()
            for memo in memos:
                item = MemoListItem(memo)
                self._list_widget.addItem(item)
                row = MemoRowWidget(memo, parent=self._list_widget)
                row.delete_requested.connect(self._on_delete_by_id)
                self._list_widget.setItemWidget(item, row)
                if memo.id == self._selected_memo_id:
                    item.setSelected(True)
        self._list_widget.blockSignals(False)

    def _on_memo_created(self, memo: Memo) -> None:
        self._selected_memo_id = memo.id
        self._controller.load_all()

    def _on_memo_updated(self, memo: Memo) -> None:
        self._autosave_label.setText(tr("memo_saved", "Kaydedildi"))
        QTimer.singleShot(2000, lambda: self._autosave_label.setText(""))
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == memo.id:
                widget = self._list_widget.itemWidget(item)
                if isinstance(widget, MemoRowWidget):
                    widget.update_title(memo.title)
                break

    def _on_memo_deleted(self, _memo_id: int) -> None:
        self._selected_memo_id = None
        self._controller.load_all()
        self._show_empty_state()

    def _on_error(self, message: str) -> None:
        self._autosave_label.setText(f"Hata: {message}")

    # ── Seçim / Yükleme ────────────────────────────────────────────────────

    def _on_selection_changed(self) -> None:
        self._autosave_timer.stop()
        if self._selected_memo_id is not None:
            self._flush_current()
        selected = self._list_widget.selectedItems()
        if not selected:
            self._selected_memo_id = None
            self._show_empty_state()
            return
        memo_id = selected[0].data(Qt.ItemDataRole.UserRole)
        if memo_id != self._selected_memo_id:
            self._load_memo(memo_id)

    def _flush_current(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            return
        body = self._editor.toHtml()
        drawing_data = self._canvas.to_base64_png() if not self._canvas.is_empty() else None
        self._controller.update(self._selected_memo_id, title=title, body=body, drawing_data=drawing_data)

    def _load_memo(self, memo_id: int) -> None:
        memo = self._controller.get_sync(memo_id)
        if memo is None:
            return
        self._selected_memo_id = memo.id
        self._autosave_timer.stop()
        self._title_edit.blockSignals(True)
        self._editor.blockSignals(True)
        self._title_edit.setText(memo.title)
        if memo.body and memo.body.strip().startswith("<!DOCTYPE"):
            self._editor.setHtml(memo.body)
        else:
            self._editor.setPlainText(memo.body)
        self._editor.blockSignals(False)
        self._title_edit.blockSignals(False)
        if memo.drawing_data:
            self._canvas.load_from_base64(memo.drawing_data)
        else:
            self._canvas.clear_canvas()
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
            self._flush_current()
        self._list_widget.clearSelection()
        self._selected_memo_id = None
        self._title_edit.blockSignals(True)
        self._editor.blockSignals(True)
        self._title_edit.clear()
        self._editor.clear()
        self._canvas.clear_canvas()
        self._title_edit.blockSignals(False)
        self._editor.blockSignals(False)
        self._autosave_label.setText("")
        self._show_editor()
        self._title_edit.setFocus()

    def _on_delete_by_id(self, memo_id: int) -> None:
        reply = QMessageBox.question(
            self,
            tr("action_delete", "Sil"),
            tr("memo_delete_confirm", "Bu memo silinecek. Emin misiniz?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._autosave_timer.stop()
            self._controller.delete(memo_id)

    # ── Otomatik Kayıt ──────────────────────────────────────────────────────

    def _save_current(self) -> None:
        title = self._title_edit.text().strip()
        body = self._editor.toHtml()
        drawing_data: str | None = None
        if not self._canvas.is_empty():
            encoded = self._canvas.to_base64_png()
            if encoded:
                drawing_data = encoded
        if self._selected_memo_id is not None:
            if title:
                self._autosave_label.setText(tr("memo_saving", "Kaydediliyor..."))
                self._controller.update(self._selected_memo_id, title=title, body=body, drawing_data=drawing_data)
        elif title:
            self._controller.create(title, body, drawing_data)
