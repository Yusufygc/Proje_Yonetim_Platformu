"""Uygulama ana giriş noktası (main.py).

QML arayüzünü (main_qml.py) başlatır. PyInstaller paketinde Windows DLL arama yolunu hazırlar.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Proje kökünü import path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

# --- Windows DLL Arama Yolu Düzeltmesi (Python 3.8+) ---
if getattr(sys, "frozen", False) and sys.platform == "win32":
    _base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent
    _dll_dirs = [
        _base,
        _base / "vosk",
        _base / "_sounddevice_data" / "portaudio-binaries",
    ]
    for _d in _dll_dirs:
        if _d.exists():
            os.add_dll_directory(str(_d))


def main() -> None:
    """Uygulamayı başlatan ana fonksiyon."""
    from main_qml import run_qml_app  # noqa: PLC0415

    sys.exit(run_qml_app())


if __name__ == "__main__":
    main()
