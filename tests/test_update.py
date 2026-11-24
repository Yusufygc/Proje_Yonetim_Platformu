"""Güncelleme servisi (güvenlik, SHA-256, tercihler, SAC yedek yolu) ve ViewModel akışı testleri."""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from PySide6.QtCore import QCoreApplication, QThreadPool
from PySide6.QtWidgets import QApplication

from app import config
from controllers.update_controller import UpdateController
from core.exceptions.update_exceptions import InstallerBlockedError, UpdateError
from presentation.viewmodels import update_viewmodel as uvm
from services import update_service as us
from version import APP_NAME, RELEASE_REPO

REPO = RELEASE_REPO
PAYLOAD = b"MZ" + b"kurulum-icerigi" * 1000
PAYLOAD_SHA = hashlib.sha256(PAYLOAD).hexdigest()


class FakeResponse(io.BytesIO):
    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


def _make_opener(routes: dict[str, bytes], calls: list[str] | None = None) -> us.Opener:
    def _open(request: urllib.request.Request) -> FakeResponse:
        url = request.full_url
        if calls is not None:
            calls.append(url)
        if url not in routes:
            raise urllib.error.URLError(f"beklenmeyen adres: {url}")
        return FakeResponse(routes[url])

    return _open


def _asset(
    version: str, *, digest: str | None = None, size: int | None = None, name: str | None = None
) -> dict[str, object]:
    asset_name = name or us.installer_asset_name(version)
    data: dict[str, object] = {
        "name": asset_name,
        "size": len(PAYLOAD) if size is None else size,
        "browser_download_url": f"https://github.com/{REPO}/releases/download/v{version}/{asset_name}",
    }
    if digest is not None:
        data["digest"] = digest
    return data


def _release(version: str = "2.0.0", **overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "tag_name": f"v{version}",
        "draft": False,
        "prerelease": False,
        "body": "Yenilikler",
        "html_url": f"https://github.com/{REPO}/releases/tag/v{version}",
        "assets": [_asset(version, digest=f"sha256:{PAYLOAD_SHA}")],
    }
    data.update(overrides)
    return data


def _info(**overrides: object) -> us.UpdateInfo:
    base = us.release_to_update(_release("2.0.0"), "1.0.0")
    assert base is not None
    values = {**base.__dict__, **overrides}
    return us.UpdateInfo(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("text", "expected"),
    [("v1.2.3", (1, 2, 3)), ("0.10.0", (0, 10, 0)), (" v2.0.1 ", (2, 0, 1)), ("1.2", None), ("v1.2.3-beta", None), ("", None)],
)
def test_parse_version_and_numeric_comparison(text: str, expected: object) -> None:
    assert us.parse_version(text) == expected
    assert us.is_newer_version("2.10.0", "2.9.0") is True
    assert us.is_newer_version("2.1.5", "2.1.5") is False
    assert us.is_newer_version("garip", "1.0.0") is False


def test_release_to_update_accepts_only_newer_stable_releases() -> None:
    info = us.release_to_update(_release("2.0.0"), "1.0.0")
    assert info is not None
    assert (info.version, info.sha256, info.asset_name) == ("2.0.0", PAYLOAD_SHA, f"{APP_NAME}-Setup-2.0.0.exe")

    assert us.release_to_update(_release("1.0.0"), "1.0.0") is None
    assert us.release_to_update(_release("2.0.0", prerelease=True), "1.0.0") is None
    assert us.release_to_update(_release("2.0.0", draft=True), "1.0.0") is None
    assert us.release_to_update(_release("2.0.0", tag_name="v2.0.0-rc1"), "1.0.0") is None
    assert us.release_to_update(_release("2.0.0", assets=[]), "1.0.0") is None


def test_release_rejects_untrusted_download_host_and_bad_size() -> None:
    evil = _release("2.0.0")
    evil["assets"] = [{**_asset("2.0.0", digest=f"sha256:{PAYLOAD_SHA}"), "browser_download_url": "https://evil.example/x.exe"}]
    with pytest.raises(UpdateError):
        us.release_to_update(evil, "1.0.0")

    other_repo = _release("2.0.0")
    other_repo["assets"] = [{**_asset("2.0.0"), "browser_download_url": "https://github.com/baska/depo/releases/download/v2.0.0/a.exe"}]
    with pytest.raises(UpdateError):
        us.release_to_update(other_repo, "1.0.0")

    huge = _release("2.0.0", assets=[_asset("2.0.0", size=us.MAX_INSTALLER_BYTES + 1)])
    with pytest.raises(UpdateError):
        us.release_to_update(huge, "1.0.0")


def test_wrong_asset_name_is_ignored_and_notes_are_bounded() -> None:
    wrong = _release("2.0.0", assets=[_asset("2.0.0", name="Baska-Setup-2.0.0.exe")])
    assert us.release_to_update(wrong, "1.0.0") is None

    info = us.release_to_update(_release("2.0.0", body="x" * 50_000), "1.0.0")
    assert info is not None and len(info.notes) == us.MAX_NOTES_CHARS


def test_fetch_latest_release_handles_404_oversize_and_errors() -> None:
    calls: list[str] = []
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    opener = _make_opener({url: json.dumps(_release("2.0.0")).encode("utf-8")}, calls)
    assert us.check_for_update("1.0.0", opener=opener) is not None
    assert calls == [url]

    def opener_404(request: urllib.request.Request) -> FakeResponse:
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)  # type: ignore[arg-type]

    assert us.fetch_latest_release(REPO, opener_404) == {}
    assert us.check_for_update("2.0.0", REPO, opener_404) is None

    with pytest.raises(UpdateError):
        us.fetch_latest_release(opener=_make_opener({}))

    oversized = _make_opener({url: b"{" + b" " * (us.MAX_JSON_BYTES + 10) + b"}"})
    with pytest.raises(UpdateError):
        us.fetch_latest_release(opener=oversized)


def test_download_verifies_sha256_sidecar_size_and_deletes_corrupt(tmp_path: Path) -> None:
    info = _info()
    progress: list[tuple[int, int]] = []
    result = us.download_installer(
        info, tmp_path, lambda done, total: progress.append((done, total)), _make_opener({info.download_url: PAYLOAD})
    )
    assert result.read_bytes() == PAYLOAD
    assert progress[-1] == (len(PAYLOAD), len(PAYLOAD))
    assert not list(tmp_path.glob("*.part"))

    bad_sha = _info(sha256="0" * 64)
    with pytest.raises(UpdateError, match="SHA-256"):
        us.download_installer(bad_sha, tmp_path, opener=_make_opener({bad_sha.download_url: PAYLOAD}))
    assert not list(tmp_path.glob("*.part"))

    no_sha = _info(sha256=None, sha256_url=None)
    with pytest.raises(UpdateError, match="SHA-256"):
        us.download_installer(no_sha, tmp_path, opener=_make_opener({no_sha.download_url: PAYLOAD}))

    sha_url = f"https://github.com/{REPO}/releases/download/v2.0.0/{APP_NAME}-Setup-2.0.0.exe.sha256"
    sidecar_info = _info(sha256=None, sha256_url=sha_url)
    sha_text = f"{PAYLOAD_SHA} *{APP_NAME}-Setup-2.0.0.exe\n".encode()
    downloaded = us.download_installer(
        sidecar_info, tmp_path / "sidecar", opener=_make_opener({sidecar_info.download_url: PAYLOAD, sha_url: sha_text})
    )
    assert downloaded.is_file()

    small = _info(size=10)
    with pytest.raises(UpdateError):
        us.download_installer(small, tmp_path / "small", opener=_make_opener({small.download_url: PAYLOAD}))


def test_redirect_handler_allows_only_github_hosts() -> None:
    handler = us._SafeRedirectHandler()
    request = urllib.request.Request("https://github.com/x")
    ok = handler.redirect_request(request, io.BytesIO(), 302, "Found", {}, "https://objects.githubusercontent.com/abc")  # type: ignore[arg-type]
    assert ok is not None
    with pytest.raises(urllib.error.URLError):
        handler.redirect_request(request, io.BytesIO(), 302, "Found", {}, "https://evil.example/abc")  # type: ignore[arg-type]
    with pytest.raises(urllib.error.URLError):
        handler.redirect_request(request, io.BytesIO(), 302, "Found", {}, "http://github.com/abc")  # type: ignore[arg-type]


def test_launch_installer_command_and_sac_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    installer = tmp_path / f"{APP_NAME}-Setup-2.0.0.exe"
    cmd = us.build_installer_command(installer, tmp_path)
    assert cmd[:5] == [str(installer), "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"]
    assert cmd[5] == f"/LOG={tmp_path / 'install.log'}"

    monkeypatch.setattr(us.os, "name", "nt")
    started: list[tuple[list[str], dict[str, object]]] = []
    us.launch_installer(installer, tmp_path, popen=lambda args, **kw: started.append((args, kw)))
    assert len(started) == 1
    assert int(started[0][1]["creationflags"]) & getattr(subprocess, "DETACHED_PROCESS", 0x8)  # type: ignore[arg-type]

    def blocked(*_a: object, **_k: object) -> None:
        exc = OSError("engellendi")
        exc.winerror = 4551  # type: ignore[attr-defined]
        raise exc

    executed: list[str] = []
    us.launch_installer(installer, tmp_path, popen=blocked, shell_execute=lambda p, _a: executed.append(p) or 42)
    assert executed == [str(installer)]

    with pytest.raises(InstallerBlockedError):
        us.launch_installer(installer, tmp_path, popen=blocked, shell_execute=lambda _p, _a: 5)
    with pytest.raises(UpdateError):
        us.launch_installer(tmp_path / "zararli.exe", tmp_path, popen=lambda *_a, **_k: None)


def test_preferences_roundtrip_skip_and_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prefs_file = tmp_path / "updates.json"
    monkeypatch.setattr(config, "UPDATE_PREFERENCES_PATH", prefs_file)
    monkeypatch.delenv(us.NO_UPDATE_CHECK_ENV, raising=False)

    assert us.load_preferences() == us.UpdatePreferences()
    assert us.update_check_allowed() is True

    svc = us.UpdateService("1.0.0", REPO, opener=_make_opener({
        f"https://api.github.com/repos/{REPO}/releases/latest": json.dumps(_release("2.0.0")).encode()
    }))
    svc.skip_version("2.0.0")
    assert svc.check_for_update(respect_skipped=True) is None
    assert svc.check_for_update(respect_skipped=False) is not None

    svc.set_check_on_startup(False)
    assert us.update_check_allowed() is False
    svc.set_check_on_startup(True)
    monkeypatch.setenv(us.NO_UPDATE_CHECK_ENV, "1")
    assert us.update_check_allowed() is False

    prefs_file.write_text("{bozuk", encoding="utf-8")
    assert us.load_preferences() == us.UpdatePreferences()


class _FakeService:
    def __init__(self) -> None:
        self.allowed = True
        self.info: us.UpdateInfo | None = _info()
        self.error: Exception | None = None
        self.launch_errors: list[Exception] = []
        self.launched: list[Path] = []
        self.skipped: list[str] = []
        self.check_calls: list[bool] = []

    def check_for_update(self, *, respect_skipped: bool = False) -> us.UpdateInfo | None:
        self.check_calls.append(respect_skipped)
        if self.error:
            raise self.error
        return self.info

    def download_installer(self, info: us.UpdateInfo, progress_callback: Any = None, dest_dir: Path | None = None) -> Path:
        if progress_callback:
            progress_callback(100)
        return Path(f"C:/gecici/{APP_NAME}-Setup-{info.version}.exe")

    def launch_installer(self, installer_path: Path) -> None:
        if self.launch_errors:
            raise self.launch_errors.pop(0)
        self.launched.append(installer_path)

    def update_check_allowed(self) -> bool:
        return self.allowed

    def set_check_on_startup(self, enabled: bool) -> None:
        self.allowed = enabled

    def skip_version(self, version: str) -> None:
        self.skipped.append(version)

    def release_page_url(self) -> str:
        return f"https://github.com/{REPO}/releases/latest"


def _wait_until(predicate: Any, timeout: float = 3.0) -> None:
    app = QCoreApplication.instance()
    assert app is not None
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        QThreadPool.globalInstance().waitForDone(20)
        app.processEvents()
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("Beklenen durum zamanında oluşmadı")


def _vm(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> tuple[uvm.UpdateViewModel, _FakeService]:
    monkeypatch.setattr(uvm, "RETRY_INTERVAL_MS", 20)
    monkeypatch.setattr(uvm, "QUIT_DELAY_MS", 10)
    svc = _FakeService()
    ctrl = UpdateController(svc)  # type: ignore[arg-type]
    vm = uvm.UpdateViewModel(SimpleNamespace(update_controller=ctrl), parent=qapp)  # type: ignore[arg-type]
    return vm, svc


def test_update_viewmodel_startup_and_manual_check_flow(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    vm, svc = _vm(qapp, monkeypatch)

    svc.allowed = False
    vm.checkForUpdates(True)
    assert svc.check_calls == []

    svc.allowed = True
    svc.info = None
    vm.checkForUpdates(True)
    _wait_until(lambda: vm.state == uvm.STATE_IDLE and len(svc.check_calls) == 1)
    assert not vm.isDialogOpen

    vm.checkForUpdates(False)
    _wait_until(lambda: vm.state == uvm.STATE_UP_TO_DATE)
    assert vm.isDialogOpen and "Güncelsiniz" in vm.statusMessage
    vm.dismiss()

    svc.info = _info()
    vm.checkForUpdates(True)
    _wait_until(lambda: vm.state == uvm.STATE_AVAILABLE)
    assert vm.isDialogOpen and vm.latestVersion == "2.0.0"

    vm.skipVersion()
    assert svc.skipped == ["2.0.0"] and not vm.isDialogOpen


def test_update_viewmodel_download_install_and_sac_retry(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    vm, svc = _vm(qapp, monkeypatch)
    quits: list[bool] = []
    vm.quitRequested.connect(lambda: quits.append(True))

    svc.launch_errors = [InstallerBlockedError("block1"), InstallerBlockedError("block2")]
    vm.checkForUpdates(False)
    _wait_until(lambda: vm.state == uvm.STATE_AVAILABLE)
    vm.startUpdate()

    _wait_until(lambda: vm.state == uvm.STATE_WAITING)
    assert "bekleniyor" in vm.statusMessage
    _wait_until(lambda: bool(svc.launched) and bool(quits), timeout=3.0)
    assert vm.state == uvm.STATE_INSTALLING
    assert vm.downloadProgress == 100

    revealed: list[bool] = []
    monkeypatch.setattr(vm, "_reveal_installer", lambda: revealed.append(True))
    vm._attempt = 0
    svc.launch_errors = [InstallerBlockedError("always")] * 5
    vm._launch_installer()
    assert vm.state == uvm.STATE_WAITING
    vm.stopWaitingForBlock()
    assert vm.state == uvm.STATE_BLOCKED and revealed and not vm._retry_timer.isActive()
