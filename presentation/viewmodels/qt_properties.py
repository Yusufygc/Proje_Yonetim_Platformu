"""QML'e liste ve sözlük sunan Qt property tanımları için tipli yardımcılar.

PySide6 `Property("QVariantList")` ve `Property("QVariantMap")` yazımını çalışma anında kabul eder,
ancak tip bilgisi (stub) yalnızca `type` bekler. Bu iki sarmalayıcı uyumsuzluğu tek yerde bastırır;
ViewModel dosyalarında `arg-type` hatalarını genel olarak kapatmak gerekmez.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Property, Signal

PropertyDecorator = Callable[[Callable[..., Any]], Property]


def variant_list_property(notify: Signal | None = None) -> PropertyDecorator:
    """`notify` verilmezse değer sabit (constant) kabul edilir."""
    if notify is None:
        return Property("QVariantList", constant=True)  # type: ignore[arg-type]  # stub yalnızca type kabul eder
    return Property("QVariantList", notify=notify)  # type: ignore[arg-type]  # stub yalnızca type kabul eder


def variant_map_property(notify: Signal) -> PropertyDecorator:
    return Property("QVariantMap", notify=notify)  # type: ignore[arg-type]  # stub yalnızca type kabul eder
