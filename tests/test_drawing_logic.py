"""Çizim tuvalinin saf JS yardımcılarının (şekil üretimi, vuruş testi, serileştirme) testleri."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QObject, Qt
from PySide6.QtQml import QQmlComponent, QQmlEngine

_DRAWING_DIR = (Path(__file__).parent.parent / "presentation" / "qml" / "views" / "memo" / "drawing").as_uri()

_KEEP_ALIVE: list[Any] = []

_HARNESS = f"""
import QtQuick
import "{_DRAWING_DIR}/ShapeFactory.js" as Factory
import "{_DRAWING_DIR}/HitTest.js" as HitTest
import "{_DRAWING_DIR}/DrawingSerializer.js" as Serializer

Item {{
    function create(tool, state) {{
        return JSON.stringify(Factory.createItem(tool, state, function(c) {{ return "fill:" + c }}))
    }}
    function hit(items, x, y) {{ return HitTest.findItemAt(items, x, y) }}
    function parse(text) {{ return JSON.stringify(Serializer.parse(text, "#123456")) }}
    function serialize(items, bg) {{ return Serializer.serialize(items, bg) }}
    function restore(raw) {{ return JSON.stringify(Serializer.restoreSnapshot(raw)) }}
}}
"""


@pytest.fixture()
def harness(qapp: Any) -> QObject:
    engine = QQmlEngine(qapp)
    component = QQmlComponent(engine)
    component.setData(_HARNESS.encode(), "file:///harness.qml")
    obj = component.create()
    assert obj is not None, [e.toString() for e in component.errors()]
    _KEEP_ALIVE.extend([engine, component])  # nesne kullanılırken motor ve bileşen toplanıp silinmesin
    return obj


def call(obj: QObject, name: str, *args: Any) -> Any:
    """QML işlevini çağırır; nesne/dizi sonuçları JSON metninden Python değerine çevrilir."""
    params = [Q_ARG("QVariant", a) for a in args]
    result = QMetaObject.invokeMethod(obj, name, Qt.ConnectionType.DirectConnection, Q_RETURN_ARG("QVariant"), *params)
    return json.loads(result) if name in ("create", "parse", "restore") else result


def _state(**overrides: Any) -> dict[str, Any]:
    base = {"color": "#EF4444", "lineWidth": 3, "startX": 10, "startY": 10, "currentX": 110, "currentY": 60,
            "points": [], "fillEnabled": False}
    return base | overrides


def test_create_item_when_drag_too_short_should_return_none(harness: QObject) -> None:
    assert call(harness, "create", "line", _state(currentX=11, currentY=11)) is None
    assert call(harness, "create", "rect", _state(currentX=12, currentY=80)) is None
    assert call(harness, "create", "pen", _state(points=[])) is None


def test_create_item_when_rect_dragged_backwards_should_normalize_box(harness: QObject) -> None:
    item = call(harness, "create", "rect", _state(startX=110, startY=60, currentX=10, currentY=10, fillEnabled=True))

    assert (item["x"], item["y"], item["w"], item["h"]) == (10, 10, 100, 50)
    assert item["fill"] == "fill:#EF4444"


def test_create_item_when_flow_block_small_should_use_minimum_size_and_default_text(harness: QObject) -> None:
    item = call(harness, "create", "flow_decision", _state(currentX=15, currentY=15))

    assert (item["w"], item["h"]) == (50, 36)
    assert item["text"] == "Koşul ?"
    assert item["fill"] == "fill:#EF4444"


def test_find_item_at_when_overlapping_should_prefer_topmost(harness: QObject) -> None:
    items = [
        {"type": "rect", "x": 0, "y": 0, "w": 100, "h": 100},
        {"type": "circle", "cx": 50, "cy": 50, "rx": 20, "ry": 20},
        {"type": "pen", "points": [{"x": 50, "y": 50}]},
    ]

    assert call(harness, "hit", items, 50, 50) == 1
    assert call(harness, "hit", items, 5, 5) == 0
    assert call(harness, "hit", items, 300, 300) == -1


def test_find_item_at_when_near_line_should_hit_within_tolerance(harness: QObject) -> None:
    items = [{"type": "line", "x1": 0, "y1": 0, "x2": 100, "y2": 0}]

    assert call(harness, "hit", items, 50, 10) == 0
    assert call(harness, "hit", items, 50, 30) == -1


def test_parse_when_legacy_array_should_upgrade_items_to_pen(harness: QObject) -> None:
    legacy = json.dumps([{"points": [{"x": 1, "y": 2}]}])

    drawing = call(harness, "parse", legacy)

    assert drawing["items"][0]["type"] == "pen"
    assert drawing["items"][0]["color"] == "#123456"
    assert drawing["backgroundImage"] == ""


@pytest.mark.parametrize("raw", ["", "   ", "{bozuk", "42", '{"items": 3}'])
def test_parse_when_input_invalid_should_return_empty_drawing(harness: QObject, raw: str) -> None:
    drawing = call(harness, "parse", raw)

    assert list(drawing["items"]) == []
    assert drawing["backgroundImage"] == ""


def test_serialize_when_background_set_should_write_versioned_object(harness: QObject) -> None:
    items = [{"type": "line", "x1": 0, "y1": 0, "x2": 5, "y2": 5}]

    assert json.loads(call(harness, "serialize", items, "")) == items
    wrapped = json.loads(call(harness, "serialize", items, "file:///a.png"))
    assert wrapped == {"version": 2, "backgroundImage": "file:///a.png", "items": items}


def test_restore_snapshot_when_old_array_format_should_clear_background(harness: QObject) -> None:
    restored = call(harness, "restore", json.dumps([{"type": "line"}]))

    assert len(restored["items"]) == 1
    assert restored["backgroundImage"] == ""
