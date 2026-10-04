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
    mgr = ThemeManager(Path("resources/themes"), Path("resources/styles"))
    mgr._palette = {"background": "#0B0F17", "surface": "#151C28"}
    assert mgr.color("surface_alt").startswith("#")
    assert mgr.color("surface_alt") != "#FFFFFF"
    assert mgr.color("hover_overlay").startswith("#")


def test_theme_bridge_all_theme_switches(qapp: QApplication) -> None:
    """ThemeBridge üzerinden farklı temalara geçildiğinde token'ların doğruluğunu test eder."""
    mgr = ThemeManager(Path("resources/themes"), Path("resources/styles"))
    bridge = ThemeBridge(mgr, None, parent=qapp)  # type: ignore[arg-type]

    themes = ["dark", "light", "emerald_dark", "indigo_dark", "ocean_dark", "rose_dark", "violet_dark"]
    for theme_name in themes:
        mgr.switch_theme(theme_name)
        assert bridge.surfaceAlt.startswith("#")
        assert bridge.hoverOverlay.startswith("#")
        assert bridge.background.startswith("#")
