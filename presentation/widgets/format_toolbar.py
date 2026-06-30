"""Zengin metin biçimlendirme araç çubuğu — QTextEdit ile entegre."""
from __future__ import annotations

from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor, QTextListFormat
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QTextEdit,
    QToolButton,
    QWidget,
)

_BTN_SS = (
    "QToolButton { border: none; border-radius: 4px; background: transparent; padding: 0 3px; }"
    " QToolButton:hover { background: rgba(128,128,128,0.15); }"
    " QToolButton:checked { background: rgba(92,107,192,0.25); color: #5C6BC0; }"
)


class FormatToolbar(QWidget):
    """Bold/italic/altçizgi/renk/liste butonlarını barındıran biçimlendirme çubuğu."""

    def __init__(self, editor: QTextEdit, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._editor = editor
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        self._bold_btn   = self._make_btn("B",  "Kalın (Ctrl+B)",   checkable=True)
        self._italic_btn = self._make_btn("İ",  "İtalik (Ctrl+I)",  checkable=True)
        self._under_btn  = self._make_btn("A̲", "Altçizgi (Ctrl+U)", checkable=True)
        self._strike_btn = self._make_btn("S̶", "Üstü çizili",       checkable=True)
        self._color_btn  = self._make_btn("A",  "Metin rengi")
        sep1 = self._sep()
        self._bullet_btn = self._make_btn("•≡", "Madde listesi",    checkable=True)
        self._num_btn    = self._make_btn("1≡", "Numaralı liste",   checkable=True)
        sep2 = self._sep()
        self._size_combo = QComboBox(parent=self)
        self._size_combo.addItems(["10", "11", "12", "14", "16", "18", "20", "24", "28", "32"])
        self._size_combo.setCurrentText("12")
        self._size_combo.setFixedSize(52, 26)

        for w in [
            self._bold_btn, self._italic_btn, self._under_btn,
            self._strike_btn, self._color_btn, sep1,
            self._bullet_btn, self._num_btn, sep2,
            self._size_combo,
        ]:
            layout.addWidget(w)
        layout.addStretch()

    def _connect_signals(self) -> None:
        self._bold_btn.clicked.connect(self._toggle_bold)
        self._italic_btn.clicked.connect(self._toggle_italic)
        self._under_btn.clicked.connect(self._toggle_underline)
        self._strike_btn.clicked.connect(self._toggle_strikeout)
        self._color_btn.clicked.connect(self._pick_color)
        self._bullet_btn.clicked.connect(self._toggle_bullet)
        self._num_btn.clicked.connect(self._toggle_numbered)
        self._size_combo.currentTextChanged.connect(self._change_font_size)
        self._editor.currentCharFormatChanged.connect(self._on_format_changed)

    # ── Widget fabrikaları ────────────────────────────────────────────────────

    def _make_btn(self, text: str, tooltip: str, checkable: bool = False) -> QToolButton:
        btn = QToolButton(parent=self)
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setCheckable(checkable)
        btn.setFixedSize(28, 26)
        btn.setStyleSheet(_BTN_SS)
        return btn

    def _sep(self) -> QFrame:
        sep = QFrame(parent=self)
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedSize(1, 20)
        sep.setStyleSheet("color: rgba(128,128,128,0.3);")
        return sep

    # ── Format aksiyonları ────────────────────────────────────────────────────

    def _toggle_bold(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontWeight(700 if self._bold_btn.isChecked() else 400)
        self._merge_format(fmt)

    def _toggle_italic(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontItalic(self._italic_btn.isChecked())
        self._merge_format(fmt)

    def _toggle_underline(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self._under_btn.isChecked())
        self._merge_format(fmt)

    def _toggle_strikeout(self) -> None:
        fmt = QTextCharFormat()
        fmt.setFontStrikeOut(self._strike_btn.isChecked())
        self._merge_format(fmt)

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(parent=self, title="Metin rengi seç")
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            self._merge_format(fmt)

    def _toggle_bullet(self) -> None:
        cursor = self._editor.textCursor()
        if self._bullet_btn.isChecked():
            self._num_btn.setChecked(False)
            cursor.createList(QTextListFormat.Style.ListDisc)
        else:
            self._remove_list(cursor)

    def _toggle_numbered(self) -> None:
        cursor = self._editor.textCursor()
        if self._num_btn.isChecked():
            self._bullet_btn.setChecked(False)
            cursor.createList(QTextListFormat.Style.ListDecimal)
        else:
            self._remove_list(cursor)

    def _change_font_size(self, size_str: str) -> None:
        try:
            size = int(size_str)
        except ValueError:
            return
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(size))
        self._merge_format(fmt)

    # ── Yardımcılar ──────────────────────────────────────────────────────────

    def _merge_format(self, fmt: QTextCharFormat) -> None:
        cursor = self._editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self._editor.mergeCurrentCharFormat(fmt)

    @staticmethod
    def _remove_list(cursor: QTextCursor) -> None:
        lst = cursor.block().textList()
        if lst:
            lst.remove(cursor.block())

    def _on_format_changed(self, fmt: QTextCharFormat) -> None:
        self._bold_btn.setChecked(fmt.fontWeight() >= 700)
        self._italic_btn.setChecked(fmt.fontItalic())
        self._under_btn.setChecked(fmt.fontUnderline())
        self._strike_btn.setChecked(fmt.fontStrikeOut())
        size = fmt.fontPointSize()
        if size > 0:
            self._size_combo.blockSignals(True)
            self._size_combo.setCurrentText(str(int(size)))
            self._size_combo.blockSignals(False)
