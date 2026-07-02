# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

# SPECPATH = packaging/ dizini; bir üst = proje kökü
ROOT = Path(SPECPATH).parent

# Conda environment içindeki sistem DLL'leri — .venv bunları PATH'te bulamıyor,
# EXE'ye elle eklenerek conda bağımlılığı ortadan kaldırılır.
CONDA_BIN = r"C:\Users\ysfygc\anaconda3\envs\projeTakip\Library\bin"

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[
        # Python stdlib C uzantıları için gereken sistem DLL'leri.
        (f"{CONDA_BIN}\\sqlite3.dll",         "."),
        (f"{CONDA_BIN}\\zstd.dll",            "."),
        (f"{CONDA_BIN}\\liblzma.dll",         "."),
        (f"{CONDA_BIN}\\libbz2.dll",          "."),
        (f"{CONDA_BIN}\\libmpdec-4.dll",      "."),
        (f"{CONDA_BIN}\\libexpat.dll",        "."),
        (f"{CONDA_BIN}\\ffi-8.dll",           "."),
        (f"{CONDA_BIN}\\libcrypto-3-x64.dll", "."),
        (f"{CONDA_BIN}\\libssl-3-x64.dll",    "."),
    ],
    datas=[
        (str(ROOT / "resources"), "resources"),
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


