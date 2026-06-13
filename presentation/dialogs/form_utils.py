"""
Dialog formları için ortak yapı taşları.

"Etiket + boşluk + alan + boşluk" ve "etiketli combo kolonu" desenleri
birden çok dialogda tekrarlandığı için tek yerde toplanır (DRY).
"""
from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from presentation.dimensions import Size, Spacing


def make_field_label(text: str, parent: QWidget) -> QLabel:
    """QSS field-label sınıfıyla form alanı etiketi üretir."""
    lbl = QLabel(text, parent=parent)
    lbl.setProperty("cssClass", "field-label")
    return lbl


def add_field(layout: QVBoxLayout, label: str, widget: QWidget, gap_after: int = Spacing.XL) -> None:
    """Etiket + alan ikilisini standart boşluklarla form layout'una ekler."""
    parent = layout.parentWidget() or widget
    layout.addWidget(make_field_label(label, parent))
    layout.addSpacing(Spacing.SM)
    layout.addWidget(widget)
    layout.addSpacing(gap_after)


def make_combo_column(
    parent: QWidget,
    label: str,
    items: list[tuple[str, object]],
) -> tuple[QWidget, QComboBox]:
    """Üstte etiket, altta combobox içeren dikey kolon döndürür."""
    column = QWidget(parent=parent)
    col_layout = QVBoxLayout(column)
    col_layout.setContentsMargins(0, 0, 0, 0)
    col_layout.setSpacing(Spacing.SM)
    col_layout.addWidget(make_field_label(label, column))
    combo = QComboBox(parent=column)
    combo.setMinimumHeight(Size.INPUT_H_LG)
    for text, data in items:
        combo.addItem(text, data)
    col_layout.addWidget(combo)
    return column, combo


def make_two_column_row(parent: QWidget, left: QWidget, right: QWidget) -> QWidget:
    """İki kolonu yan yana yerleştiren satır widget'ı üretir."""
    row = QWidget(parent=parent)
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(Spacing.XL)
    left.setParent(row)
    right.setParent(row)
    layout.addWidget(left)
    layout.addWidget(right)
    return row


def select_combo_data(combo: QComboBox, value: object) -> None:
    """Combobox'ta itemData'sı verilen değere eşit olan satırı seçer."""
    idx = combo.findData(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


def set_field_error(widget: QWidget, error: bool) -> None:
    """QSS error property'sini ayarlar ve stili yeniler (kırmızı çerçeve)."""
    widget.setProperty("error", "true" if error else "false")
    widget.style().unpolish(widget)
    widget.style().polish(widget)
