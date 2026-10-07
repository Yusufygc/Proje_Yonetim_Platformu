# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

# SPECPATH = packaging/ dizini; bir üst = proje kökü
ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
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
    a.binaries,
    a.datas,
    [],
    name="ProjeTakipPlatformu",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "icons" / "app_icon.ico"),
    version=str(ROOT / "packaging" / "version_info.txt"),
)


