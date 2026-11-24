"""build_verify: gerçek kurulum kaydını koruma, exe deneme mantığı ve simge dosyaları."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

import build_verify as bv

ROOT = Path(__file__).resolve().parents[1]


def test_app_id_is_read_from_inno_script() -> None:
    app_id = bv.read_app_id(ROOT / "packaging" / "ProjeTakipPlatformu.iss")
    assert app_id == "{99B49D61-13F5-4CE1-8D86-9E569F516358}"
    assert bv.uninstall_key_path(app_id).endswith(r"Uninstall\{99B49D61-13F5-4CE1-8D86-9E569F516358}_is1")


class FakeWinreg(types.SimpleNamespace):
    """Yalnızca kullanılan winreg işlevlerini taklit eder (gerçek kayıt defterine dokunmaz)."""

    def __init__(self, store: dict[str, list[tuple[str, object, int]]]) -> None:
        super().__init__(HKEY_CURRENT_USER="HKCU", KEY_SET_VALUE=2)
        self.store = store

    def OpenKey(self, _root: str, path: str):  # noqa: N802
        if path not in self.store:
            raise FileNotFoundError(path)

        class _Key:
            def __enter__(self_inner):  # noqa: N805
                return path

            def __exit__(self_inner, *_a):  # noqa: N805
                return False

        return _Key()

    def EnumValue(self, path: str, index: int):  # noqa: N802
        values = self.store[path]
        if index >= len(values):
            raise OSError("bitti")
        return values[index]

    def CreateKeyEx(self, _root: str, path: str, _r: int, _access: int):  # noqa: N802
        self.store.setdefault(path, [])

        class _Key:
            def __enter__(self_inner):  # noqa: N805
                return path

            def __exit__(self_inner, *_a):  # noqa: N805
                return False

        return _Key()

    def SetValueEx(self, path: str, name: str, _r: int, kind: int, data: object) -> None:  # noqa: N802
        values = [v for v in self.store[path] if v[0] != name]
        values.append((name, data, kind))
        self.store[path] = values

    def DeleteKey(self, _root: str, path: str) -> None:  # noqa: N802
        self.store.pop(path, None)


def test_real_registration_is_restored_after_trial_install_overwrites_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_id = "{TEST-GUID}"
    path = bv.uninstall_key_path(app_id)
    real = [
        ("InstallLocation", r"C:\Users\u\AppData\Local\Programs\ProjeTakipPlatformu", 1),
        ("DisplayVersion", "0.1.4", 1),
    ]
    store = {path: list(real)}
    monkeypatch.setitem(sys.modules, "winreg", FakeWinreg(store))

    start_menu = tmp_path / "Programs" / "Proje Takip Platformu"
    start_menu.mkdir(parents=True)
    (start_menu / "Proje Takip Platformu.lnk").write_bytes(b"GERCEK-KISAYOL")

    saved = bv.save_registration(app_id, start_menu)

    store[path] = [("InstallLocation", r"C:\Temp\deneme", 1), ("DisplayVersion", "9.9.9", 1)]
    (start_menu / "Proje Takip Platformu.lnk").write_bytes(b"DENEME-KISAYOLU")

    bv.restore_registration(app_id, saved, start_menu)
    assert dict((n, d) for n, d, _ in store[path])["InstallLocation"] == real[0][1]
    assert dict((n, d) for n, d, _ in store[path])["DisplayVersion"] == "0.1.4"
    assert (start_menu / "Proje Takip Platformu.lnk").read_bytes() == b"GERCEK-KISAYOL"


def test_trial_leftovers_are_removed_when_no_real_install_existed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_id = "{TEST-GUID}"
    path = bv.uninstall_key_path(app_id)
    store: dict[str, list[tuple[str, object, int]]] = {}
    monkeypatch.setitem(sys.modules, "winreg", FakeWinreg(store))
    start_menu = tmp_path / "Proje Takip Platformu"

    saved = bv.save_registration(app_id, start_menu)
    assert saved.registry_values is None and not saved.shortcut_files

    store[path] = [("InstallLocation", "x", 1)]
    start_menu.mkdir()
    (start_menu / "k.lnk").write_bytes(b"x")
    bv.restore_registration(app_id, saved, start_menu)
    assert path not in store and not start_menu.exists()


def _batch(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_bytes(body.replace("\n", "\r\n").encode("ascii"))
    return path


def test_launch_check_reports_running_and_early_exit(tmp_path: Path) -> None:
    long_running = _batch(tmp_path, "uzun.bat", "@echo off\nping -n 30 127.0.0.1 >nul\n")
    assert bv.launch_check(long_running, seconds=1.0).ok is True

    crashing = _batch(tmp_path, "coker.bat", "@echo off\nexit /b 3\n")
    result = bv.launch_check(crashing, seconds=2.0)
    assert result.ok is False and "çıkış kodu 3" in result.detail

    missing = bv.launch_check(tmp_path / "yok.exe", seconds=1.0)
    assert missing.ok is False


def test_launch_check_passes_isolation_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeProc:
        pid = 1

        def poll(self) -> None:
            return None

    def fake_popen(args: list[str], env: dict[str, str], cwd: str) -> FakeProc:
        captured.update(env)
        return FakeProc()

    monkeypatch.setattr(bv.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(bv.subprocess, "run", lambda *a, **k: None)
    assert bv.launch_check(tmp_path / "x.exe", seconds=0.3).ok is True
    assert captured["PROJE_TAKIP_NO_UPDATE_CHECK"] == "1"
    assert "proje_takip_verify_home_" in str(captured["PROJE_TAKIP_HOME"])


def test_app_icon_is_a_real_ico_file() -> None:
    data = (ROOT / "icons" / "app_icon.ico").read_bytes()
    assert data[:4] == b"\x00\x00\x01\x00"
