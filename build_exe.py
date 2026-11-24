"""PyInstaller ile ProjeTakipPlatformu.exe derler (kararlı exe: her sürümde bayt bayt aynı çıktı).

Kararlı exe yalnızca sabit başlatıcıyı (`packaging/launcher.py`) içerir; uygulama kodu `_internal` altında
`.pyc` olarak durur (`--debug=noarchive`). `SOURCE_DATE_EPOCH` ve sabit sürüm kaynağı PE zaman damgasını ve
sürüm bilgisini sabitler. Çıktının SHA-256 özeti `packaging/launcher.sha256` ile karşılaştırılır; farklıysa
derleme DURUR (bkz. docs/wiki/exe-dagitim-rehberi.md bölüm 3 ve 8).
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_EXE_NAME = "ProjeTakipPlatformu"
LAUNCHER_EPOCH = 1700000000  # DEĞİŞTİRME (bilerek yeni özet denemenin tek yolu)
HASH_FILE = ROOT / "packaging" / "launcher.sha256"

# Uygulamanın kullanmadığı Qt modülleri paketten çıkarılır (boyut). QML'in kullandığı modüller (Quick, Controls,
# Layouts) ve QtNetwork/QtSvg çıkarılmaz.
EXCLUDED_MODULES = (
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineQuick", "PySide6.QtWebEngineWidgets", "PySide6.QtWebChannel",
    "PySide6.QtWebSockets", "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DInput", "PySide6.Qt3DLogic",
    "PySide6.Qt3DAnimation", "PySide6.Qt3DExtras", "PySide6.QtQuick3D", "PySide6.QtCharts",
    "PySide6.QtDataVisualization", "PySide6.QtGraphs", "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtDesigner", "PySide6.QtHelp", "PySide6.QtLocation",
    "PySide6.QtPositioning", "PySide6.QtBluetooth", "PySide6.QtNfc", "PySide6.QtSensors", "PySide6.QtSerialPort",
    "PySide6.QtSerialBus", "PySide6.QtTest", "PySide6.QtSql", "PySide6.QtTextToSpeech", "PySide6.QtRemoteObjects",
    "PySide6.QtSpatialAudio", "PySide6.QtVirtualKeyboard", "tkinter", "_tkinter", "pytest", "mypy", "ruff",
)  # fmt: skip

HIDDEN_IMPORTS = (
    "main",
    "alembic",
    "alembic.runtime.migration",
    "alembic.operations",
    "alembic.script",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.sql.default_comparator",
    "logging.config",
    "logging.handlers",
    "core.exceptions.note_exceptions",
)

# PyInstaller'ın Qt kancası `PySide6/qml` klasörünün tamamını ve bağlı DLL'leri toplar. Kullanılmayanlar
# derlemeden sonra silinir; silinenler exe'nin dışındadır, kararlı exe özeti etkilenmez.
UNUSED_QML_DIRS = (
    "Qt3D", "Qt5Compat", "QtCharts", "QtDataVisualization", "QtGraphs", "QtLocation", "QtMultimedia",
    "QtPositioning", "QtQuick3D", "QtRemoteObjects", "QtScxml", "QtSensors", "QtTest", "QtTextToSpeech",
    "QtWebChannel", "QtWebEngine", "QtWebSockets", "QtWebView",
)  # fmt: skip
UNUSED_DLL_PREFIXES = (
    "Qt6WebEngine", "Qt6Pdf", "Qt63D", "Qt6Quick3D", "Qt6Charts", "Qt6DataVisualization", "Qt6Graphs",
    "Qt6Location", "Qt6Multimedia", "Qt6Positioning", "Qt6RemoteObjects", "Qt6Scxml", "Qt6Sensors",
    "Qt6TextToSpeech", "Qt6WebChannel", "Qt6WebSockets", "Qt6WebView", "Qt6SpatialAudio", "Qt6Test",
    "Qt6Designer", "Qt6Help", "Qt6Bluetooth", "Qt6Nfc", "Qt6SerialPort", "Qt6SerialBus", "Qt6Sql",
    "QtWebEngineProcess",
)  # fmt: skip
UNUSED_PACKAGE_DIRS = ("translations", "resources")


def executable_path() -> Path:
    """Derlenen uygulamanın ana çalıştırılabilir dosya yolunu döndürür."""
    return ROOT / "dist" / APP_EXE_NAME / f"{APP_EXE_NAME}.exe"


def sha256_of(path: Path) -> str:
    """Verilen dosyanın küçük harf SHA-256 özetini hesaplar."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _data_arguments(root: Path) -> list[str]:
    sep = os.pathsep
    entries = (
        (root / "resources", "resources"),
        (root / "presentation" / "qml", "presentation/qml"),
        (root / "icons", "icons"),
        (root / "alembic.ini", "."),
        (root / "infrastructure" / "migrations", "infrastructure/migrations"),
    )
    return [f"--add-data={src}{sep}{dst}" for src, dst in entries]


def pyinstaller_arguments(root: Path = ROOT) -> list[str]:
    """Özeti belirleyen PyInstaller bağımsız değişkenleri (testle sabitlenir)."""
    return [
        str(root / "packaging" / "launcher.py"),
        f"--paths={root}",
        f"--name={APP_EXE_NAME}",
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--noupx",
        "--debug=noarchive",
        *(f"--exclude-module={module}" for module in EXCLUDED_MODULES),
        *(f"--hidden-import={module}" for module in HIDDEN_IMPORTS),
        "--collect-binaries=vosk",
        "--collect-data=_sounddevice_data",
        f"--icon={root / 'icons' / 'app_icon.ico'}",
        f"--version-file={root / 'packaging' / 'launcher_version_info.txt'}",
        f"--distpath={root / 'dist'}",
        f"--workpath={root / 'build'}",
        f"--specpath={root / 'build'}",
        *_data_arguments(root),
    ]


def is_unused(relative: str) -> bool:
    """`PySide6/...` altındaki bağıl yolun kullanılmayan bir Qt parçasına ait olup olmadığını döndürür."""
    parts = relative.replace("\\", "/").split("/")
    if len(parts) < 2 or parts[0] != "PySide6":
        return False
    if parts[1] in UNUSED_PACKAGE_DIRS:
        return True
    if parts[1] == "qml":
        return len(parts) > 2 and parts[2] in UNUSED_QML_DIRS
    return len(parts) == 2 and parts[1].startswith(UNUSED_DLL_PREFIXES)


def prune(app_dir: Path) -> None:
    """Kullanılmayan Qt parçalarını `_internal/PySide6` altından siler (exe etkilenmez)."""
    internal = app_dir / "_internal"
    package = internal / "PySide6"
    if not package.is_dir():
        return
    qml_dir = package / "qml"
    candidates = [*package.iterdir(), *(qml_dir.iterdir() if qml_dir.is_dir() else ())]
    for path in candidates:
        if not is_unused(path.relative_to(internal).as_posix()):
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def _fail_missing_hash() -> None:
    print(
        "HATA: packaging/launcher.sha256 yok.\n"
        "  İlk kez derliyorsan: exe'yi bu makinede aç (build_verify.launch_check), sonra\n"
        "  `python build_installer.py --update-launcher-hash` ile özeti onayla ve commit'le.",
        file=sys.stderr,
    )
    sys.exit(1)


def _fail_changed_hash(approved: str, actual: str) -> None:
    print(
        "HATA: Kararlı exe özeti DEĞİŞTİ; derleme ve yayın durduruldu.\n"
        f"  onaylanan: {approved}\n  derlenen : {actual}\n"
        "  Nedenleri: PyInstaller/Python sürümü, satır sonları, simge, sürüm kaynağı, giriş betiği.\n"
        "  Bilerek değiştirdiysen docs/wiki/exe-dagitim-rehberi.md bölüm 8'i uygula; "
        "bilmeden değiştiyse nedenini bul.",
        file=sys.stderr,
    )
    sys.exit(1)


def check_launcher_hash(exe: Path, update: bool = False, hash_file: Path = HASH_FILE) -> None:
    """Derlenen exe özetini onaylanmışla karşılaştırır; farklıysa veya dosya yoksa durdurur."""
    actual = sha256_of(exe)
    if update:
        hash_file.parent.mkdir(parents=True, exist_ok=True)
        hash_file.write_text(f"{actual} *{exe.name}\n", encoding="utf-8", newline="\n")
        print(f"[kapı] Onaylı exe özeti güncellendi: {actual}")
        return
    if not hash_file.is_file():
        _fail_missing_hash()
    approved = hash_file.read_text(encoding="utf-8").split()[0].lower()
    if approved != actual.lower():
        _fail_changed_hash(approved, actual)
    print(f"[kapı] Kararlı exe özeti onaylananla aynı: {actual}")


def build_executable(update_hash: bool = False) -> Path:
    """PyInstaller'ı çalıştırır, özet kapısından geçirir ve exe yolunu döndürür."""
    import PyInstaller.__main__

    os.environ["SOURCE_DATE_EPOCH"] = str(LAUNCHER_EPOCH)
    PyInstaller.__main__.run(pyinstaller_arguments())
    prune(executable_path().parent)
    exe = executable_path()
    if not exe.is_file():
        print(f"HATA: exe oluşmadı: {exe}", file=sys.stderr)
        sys.exit(1)
    check_launcher_hash(exe, update=update_hash)
    return exe


if __name__ == "__main__":
    build_executable(update_hash="--update-launcher-hash" in sys.argv)
