"""Yayın paketleme bekçileri: kararlı exe sabitleri, özet kapısı, tek sürüm kaynağı, Inno betiği, iş akışı, release.py."""

from __future__ import annotations

import hashlib
import importlib.util
import re
from pathlib import Path

import pytest

import build_exe
import build_installer
import version
from app import config

ROOT = Path(__file__).resolve().parents[1]

# Bu iki dosyanın içeriği exe özetine girer: DEĞİŞTİRME. Bilerek değişiyorsa docs/wiki/exe-dagitim-rehberi.md bölüm 8.
LAUNCHER_SHA256 = "244a1b3f78b712463dbbe1dff75b43d079de2904fa1eda8365d390408e755904"
VERSION_INFO_SHA256 = "418316448816cfccb2434436aaca4b9dfd1306a20e176283e82b55e0bba2ee8e"


def _lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _load_release_tool():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("release_tool", ROOT / "tools" / "release.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_launcher_and_version_resource_are_pinned() -> None:
    assert _lf_sha256(ROOT / "packaging" / "launcher.py") == LAUNCHER_SHA256, (
        "packaging/launcher.py DEĞİŞMEMELİ (exe özetine girer)."
    )
    assert _lf_sha256(ROOT / "packaging" / "launcher_version_info.txt") == VERSION_INFO_SHA256
    launcher = (ROOT / "packaging" / "launcher.py").read_text(encoding="utf-8")
    assert "from main import main" in launcher and launcher.rstrip().endswith("main()")


def test_version_resource_is_constant_and_not_the_product_version() -> None:
    text = (ROOT / "packaging" / "launcher_version_info.txt").read_text(encoding="utf-8")
    assert "filevers=(1, 0, 0, 0)" in text and "1.0.0.0" in text
    assert version.__version__ not in text or version.__version__ == "1.0.0"
    assert not (ROOT / "packaging" / "version_info.txt").exists()
    assert not (ROOT / "version_info.txt").exists()


def test_pyinstaller_arguments_keep_exe_stable() -> None:
    args = build_exe.pyinstaller_arguments(ROOT)
    for required in ("--onedir", "--windowed", "--noupx", "--debug=noarchive", "--noconfirm", "--clean"):
        assert required in args
    assert str(ROOT / "packaging" / "launcher.py") == args[0]
    assert any(a.startswith("--version-file=") and a.endswith("launcher_version_info.txt") for a in args)
    assert any(a.startswith("--icon=") and a.endswith("app_icon.ico") for a in args)
    assert build_exe.LAUNCHER_EPOCH == 1700000000
    source = (ROOT / "build_exe.py").read_text(encoding="utf-8")
    assert 'os.environ["SOURCE_DATE_EPOCH"] = str(LAUNCHER_EPOCH)' in source

    data = [a.split("=", 1)[1] for a in args if a.startswith("--add-data=")]
    destinations = {entry.rsplit(build_exe.os.pathsep, 1)[-1] for entry in data}
    assert destinations == {"resources", "presentation/qml", "icons", ".", "infrastructure/migrations"}
    assert (ROOT / "resources").is_dir()
    assert (ROOT / "presentation" / "qml").is_dir()
    assert (ROOT / "icons").is_dir()
    assert (ROOT / "alembic.ini").is_file()
    assert (ROOT / "infrastructure" / "migrations").is_dir()


def test_launcher_hash_gate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exe = tmp_path / "ProjeTakipPlatformu.exe"
    exe.write_bytes(b"ornek-exe")
    hash_file = tmp_path / "launcher.sha256"

    with pytest.raises(SystemExit):
        build_exe.check_launcher_hash(exe, hash_file=hash_file)

    build_exe.check_launcher_hash(exe, update=True, hash_file=hash_file)
    build_exe.check_launcher_hash(exe, hash_file=hash_file)
    assert "onaylananla aynı" in capsys.readouterr().out

    exe.write_bytes(b"degisti")
    with pytest.raises(SystemExit):
        build_exe.check_launcher_hash(exe, hash_file=hash_file)
    assert "DEĞİŞTİ" in capsys.readouterr().err


def test_approved_hash_file_is_committed_and_well_formed() -> None:
    line = (ROOT / "packaging" / "launcher.sha256").read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"[0-9a-f]{64} \*ProjeTakipPlatformu\.exe", line)


def test_release_workflow_cannot_skip_the_gate() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "python build_installer.py" in workflow
    assert "--no-verify" not in workflow and "--update-launcher-hash" not in workflow
    assert "tags:" in workflow and '"v*"' in workflow
    assert "--check-tag" in workflow and "--verify-tag" in workflow
    assert "env:" in workflow and "TAG: ${{ github.ref_name }}" in workflow
    assert "${{ github.ref_name }}" not in workflow.replace("TAG: ${{ github.ref_name }}", "")
    assert 'python-version: "3.10"' in workflow
    assert "contents: write" in workflow
    assert "-c requirements-lock.txt" in workflow


def test_single_version_source_and_release_repo() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", version.__version__)
    assert config.APP_VERSION == version.__version__
    assert version.APP_NAME == "ProjeTakipPlatformu"
    assert version.RELEASE_REPO == "Yusufygc/Proje_Yonetim_Platformu"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"badge/s%C3%BCr%C3%BCm-{version.__version__}-" in readme
    assert build_installer.installer_path().name == f"{version.APP_NAME}-Setup-{version.__version__}.exe"


def test_inno_script_has_required_settings() -> None:
    iss = (ROOT / "packaging" / "ProjeTakipPlatformu.iss").read_text(encoding="utf-8-sig")
    assert "AppId={{99B49D61-13F5-4CE1-8D86-9E569F516358}" in iss
    for line in (
        "PrivilegesRequired=lowest",
        "CloseApplications=yes",
        "RestartApplications=no",
        "OutputBaseFilename=ProjeTakipPlatformu-Setup-{#AppVersion}",
        "SetupIconFile=..\\icons\\app_icon.ico",
        "Check: RelaunchAfterUpdate",
    ):
        assert line in iss
    assert "WizardSilent and not HasParam('/VERYSILENT')" in iss
    assert "WizardVerySilent" not in iss.replace("WizardVerySilent diye", "")
    assert (ROOT / "icons" / "app_icon.ico").is_file()


def test_release_tool_check_tag_and_version_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tool = _load_release_tool()
    version_file = tmp_path / "version.py"
    version_file.write_text('__version__ = "1.2.3"\nAPP_NAME = "X"\n', encoding="utf-8")

    assert tool.check_tag("v1.2.3", version_file) == 0
    assert tool.check_tag("v1.2.4", version_file) == 1
    assert tool.check_tag("1.2.3", version_file) == 1
    assert tool.parse_new_version("2.0.0") == (2, 0, 0)
    with pytest.raises(SystemExit):
        tool.parse_new_version("2.0.0-rc1")

    readme = tmp_path / "README.md"
    readme.write_text("![Sürüm](https://img.shields.io/badge/s%C3%BCr%C3%BCm-1.2.3-38BDF8)\n", encoding="utf-8")
    monkeypatch.setattr(tool, "VERSION_FILE", version_file)
    monkeypatch.setattr(tool, "README", readme)
    tool.write_version((2, 0, 0))
    assert '__version__ = "2.0.0"' in version_file.read_text(encoding="utf-8")
    assert "s%C3%BCr%C3%BCm-2.0.0-" in readme.read_text(encoding="utf-8")
    assert tool.current_version(version_file) == (2, 0, 0)


def test_release_tool_never_pushes() -> None:
    source = (ROOT / "tools" / "release.py").read_text(encoding="utf-8")
    assert 'git("push"' not in source and "git push" not in source.replace("git push origin", "")
    assert "--follow-tags" not in source.replace("--follow-tags KULLANMA", "")


def test_user_data_dir_honours_override_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PROJE_TAKIP_HOME", str(tmp_path / "veri"))
    assert config._resolve_data_dir() == (tmp_path / "veri").resolve()


def test_gitignore_keeps_release_tool_tracked() -> None:
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "tools/" not in lines
    assert "dist/" in lines and "build/" in lines


def test_installer_discovery_and_checksum_file(tmp_path: Path) -> None:
    installer = tmp_path / "ProjeTakipPlatformu-Setup-0.0.1.exe"
    installer.write_bytes(b"x" * 100)
    checksum = build_installer.write_checksum(installer)
    assert checksum.name == installer.name + ".sha256"
    assert checksum.read_text(encoding="utf-8") == f"{hashlib.sha256(b'x' * 100).hexdigest()} *{installer.name}\n"


def test_lock_file_pins_direct_and_transitive_build_dependencies() -> None:
    def norm(name: str) -> str:
        return name.strip().lower().replace("_", "-")

    lock = (ROOT / "requirements-lock.txt").read_text(encoding="utf-8")
    pins = {
        norm(line.split("==")[0]): line.split("==")[1].strip()
        for line in lock.splitlines()
        if "==" in line and not line.startswith("#")
    }
    for line in (ROOT / "requirements-build.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line and not line.startswith("-"):
            name, ver = line.split("==")
            assert norm(name) in pins, f"{name} kilitte yok"
            assert pins[norm(name)] == ver.strip(), f"{name} sürümü kilitle uyumsuz"
    for transitive in ("shiboken6", "pyinstaller-hooks-contrib", "urllib3", "pyside6"):
        assert transitive in pins, f"geçişli bağımlılık kilitli olmalı: {transitive}"
