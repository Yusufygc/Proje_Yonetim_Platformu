# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

# SPECPATH = packaging/ dizini; bir üst = proje kökü
ROOT = Path(SPECPATH).parent

# Vosk CFFI native kütüphaneleri — PyInstaller cffi.dlopen() ile yüklenen
# DLL'leri statik analizle bulamaz; elle eklenmesi zorunludur.
VOSK_DIR = str(ROOT / ".venv" / "Lib" / "site-packages" / "vosk")

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[
        # Vosk ses tanıma C++ motoru ve bağımlılıkları
        (f"{VOSK_DIR}\\libvosk.dll",          "vosk"),
        (f"{VOSK_DIR}\\libgcc_s_seh-1.dll",   "vosk"),
        (f"{VOSK_DIR}\\libstdc++-6.dll",      "vosk"),
        (f"{VOSK_DIR}\\libwinpthread-1.dll",  "vosk"),
    ],
    datas=[
        (str(ROOT / "resources"), "resources"),
        # QML arayüz dosyaları çalışma anında Path(__file__) ile yüklenir; pakete dahil edilmezse pencere açılmaz.
        (str(ROOT / "presentation" / "qml"), "presentation/qml"),
        (str(ROOT / "icons"), "icons"),
        (str(ROOT / "alembic.ini"), "."),
        (str(ROOT / "infrastructure" / "migrations"), "infrastructure/migrations"),
    ],
    hiddenimports=[
        "alembic",
        "alembic.runtime.migration",
        "alembic.operations",
        "alembic.script",
        "keyring.backends.Windows",
        "sqlalchemy.dialects.sqlite",
        "sqlalchemy.sql.default_comparator",
        "logging.config",
        "logging.handlers",
        "core.exceptions.note_exceptions",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["_tkinter", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="ProjeTakipPlatformu",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "icons" / "app_icon.ico"),
    version=str(ROOT / "packaging" / "version_info.txt"),
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ProjeTakipPlatformu",
)
