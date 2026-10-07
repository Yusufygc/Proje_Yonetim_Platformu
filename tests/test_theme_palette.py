"""Tema paletleri ve ThemeBridge token doğrulama testleri."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from core.managers.theme_manager import ThemeManager
from presentation.viewmodels.theme_bridge import ThemeBridge


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app  # type: ignore[return-value]


def test_all_theme_palettes_json_completeness() -> None:
    """Tüm tema JSON dosyalarının gerekli anahtarları ve kontrastı sağladığını doğrular."""
    themes_dir = Path("resources/themes")
    theme_files = list(themes_dir.glob("*.json"))
    assert len(theme_files) >= 12

    required_keys = {
        "background", "surface", "surface_raised", "surface_alt", "border",
        "text_primary", "text_secondary", "text_muted", "accent_start",
        "sidebar_bg", "sidebar_active", "sidebar_text", "hover_overlay",
    }

    for path in theme_files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        missing = required_keys - set(data.keys())
        assert not missing, f"{path.name} eksik anahtarlar: {missing}"
        if "dark" in path.name:
            assert data["surface_alt"] != "#FFFFFF", f"{path.name} dark temada surface_alt beyaz olamaz"
            assert data["border"] != data["surface"], f"{path.name} border ile surface ayni olamaz"


def test_theme_manager_fallback_and_derivation() -> None:
    """Eksik token'lar için akıllı yedek değerlerin üretildiğini test eder."""
    mgr = ThemeManager(Path("resources/themes"))
    mgr._palette = {"background": "#0B0F17", "surface": "#151C28"}
    assert mgr.color("surface_alt").startswith("#")
    assert mgr.color("surface_alt") != "#FFFFFF"
    assert mgr.color("hover_overlay").startswith("#")


def test_theme_bridge_all_theme_switches(qapp: QApplication) -> None:
    """ThemeBridge üzerinden farklı temalara geçildiğinde token'ların doğruluğunu test eder."""
    mgr = ThemeManager(Path("resources/themes"))
    bridge = ThemeBridge(mgr, None, parent=qapp)  # type: ignore[arg-type]

    themes = ["dark", "light", "emerald_dark", "indigo_dark", "ocean_dark", "rose_dark", "violet_dark"]
    for theme_name in themes:
        mgr.switch_theme(theme_name)
        assert bridge.surfaceAlt.startswith("#")
        assert bridge.hoverOverlay.startswith("#")
        assert bridge.background.startswith("#")


@pytest.mark.parametrize(
    ("css_value", "qt_value"),
    [("#FFFFFF0D", "#0DFFFFFF"), ("#10B98122", "#2210B981"), ("#00000008", "#08000000"), ("#FFF1F2", "#FFF1F2")],
)
def test_to_qt_color_when_css_alpha_order_should_convert_to_argb(css_value: str, qt_value: str) -> None:
    assert ThemeManager.to_qt_color(css_value) == qt_value


def test_color_when_dark_theme_hover_overlay_should_not_be_opaque() -> None:
    mgr = ThemeManager(Path("resources/themes"))
    mgr.switch_theme("dark")

    # Qt #AARRGGBB okur: ilk iki hane alfa. Opak (FF) olursa üstüne gelinen satır sarı dolar.
    assert mgr.color("hover_overlay").startswith("#0D")


def test_qml_files_when_scanned_should_not_call_non_reactive_theme_color_slot() -> None:
    """`themeBridge.color("x")` bir slot çağrısıdır; tema değişince QML bağlaması yenilenmez.

    Açık temadan koyu temaya geçince bu çağrılarla boyanan alanlar eski renkte (beyaz zemin,
    koyu yazı) kalır. Bildirimli özellikler (`themeBridge.surface`, `.textPrimary` ...) kullanılmalı.
    """
    qml_root = Path(__file__).parent.parent / "presentation" / "qml"
    offenders = [
        str(path.relative_to(qml_root))
        for path in qml_root.rglob("*.qml")
        if "themeBridge.color(" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []
