"""Güncelleme servisi (sürüm karşılaştırma, doğrulama, indirme) ve ViewModel akışı testleri."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

from controllers.update_controller import UpdateController
from core.exceptions.update_exceptions import UpdateError
from presentation.viewmodels.update_viewmodel import UpdateViewModel
from services.update_service import UpdateInfo, UpdateService, parse_version

REPO = "Owner/Repo"
ASSET = "Setup.exe"
PAYLOAD = b"kurulum-icerigi" * 100


class FakeResponse(io.BytesIO):
    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()


def _release(tag: str = "v0.2.0", url: str | None = None, digest: str | None = None) -> dict[str, Any]:
    asset: dict[str, Any] = {
        "name": ASSET,
        "browser_download_url": url or f"https://github.com/{REPO}/releases/download/{tag}/{ASSET}",
        "size": len(PAYLOAD),
    }
    if digest is not None:
        asset["digest"] = digest
    return {"tag_name": tag, "body": "Yenilikler", "assets": [asset]}


def _service(release: dict[str, Any] | None = None, current: str = "0.1.0", fail: bool = False) -> UpdateService:
    def opener(request: Any, timeout: int) -> FakeResponse:
        if fail:
            raise OSError("ağ yok")
        if request.full_url.endswith("/releases/latest"):
            return FakeResponse(json.dumps(release).encode())
        return FakeResponse(PAYLOAD)

    return UpdateService(current, REPO, ASSET, opener=opener)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("v1.2.3", (1, 2, 3)), ("0.10.0", (0, 10, 0)), (" v2.0.1 ", (2, 0, 1)), ("1.2", None), ("v1.2.3-beta", None), ("", None)],
)
def test_parse_version_when_various_formats_should_parse_or_return_none(text: str, expected: object) -> None:
    assert parse_version(text) == expected


def test_check_for_update_when_newer_release_should_return_info_with_digest() -> None:
    digest = "sha256:" + hashlib.sha256(PAYLOAD).hexdigest()

    info = _service(_release(digest=digest)).check_for_update()

    assert info is not None
    assert info.version == "0.2.0"
    assert info.notes == "Yenilikler"
    assert info.sha256 == digest.removeprefix("sha256:")


def test_check_for_update_when_same_or_older_release_should_return_none() -> None:
    assert _service(_release("v0.1.0")).check_for_update() is None
    assert _service(_release("v0.0.9")).check_for_update() is None


def test_check_for_update_when_version_compared_numerically_should_not_treat_0_10_as_older_than_0_9() -> None:
    assert _service(_release("v0.10.0"), current="0.9.0").check_for_update() is not None


def test_check_for_update_when_network_fails_should_raise_update_error() -> None:
    with pytest.raises(UpdateError):
        _service(fail=True).check_for_update()


def test_check_for_update_when_asset_missing_should_raise_update_error() -> None:
    release = _release()
    release["assets"] = []

    with pytest.raises(UpdateError):
        _service(release).check_for_update()


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/Owner/Repo/releases/download/v0.2.0/Setup.exe",
        "https://evil.example.com/Owner/Repo/releases/download/v0.2.0/Setup.exe",
        "https://github.com/Other/Repo/releases/download/v0.2.0/Setup.exe",
    ],
)
def test_check_for_update_when_download_url_untrusted_should_raise_update_error(url: str) -> None:
    with pytest.raises(UpdateError):
        _service(_release(url=url)).check_for_update()


def test_download_installer_when_digest_matches_should_save_file_and_report_progress() -> None:
    digest = "sha256:" + hashlib.sha256(PAYLOAD).hexdigest()
    service = _service(_release(digest=digest))
    info = service.check_for_update()
    assert info is not None
    progress: list[int] = []

    path = service.download_installer(info, progress.append)

    assert path.read_bytes() == PAYLOAD
    assert progress[-1] == 100
    path.unlink()


def test_download_installer_when_digest_mismatch_should_raise_and_delete_file() -> None:
    service = _service(_release(digest="sha256:" + "0" * 64))
    info = service.check_for_update()
    assert info is not None

    with pytest.raises(UpdateError):
        service.download_installer(info)

    assert not (Path(__import__("tempfile").gettempdir()) / "ProjeTakipUpdate" / ASSET).exists()


class _EventBus:
    def __init__(self) -> None:
        self.toasts: list[tuple[str, str]] = []

    def publish(self, name: str, **payload: Any) -> None:
        if name == "toast.show":
            self.toasts.append((payload["message"], payload["type_"]))


def _view_model(qapp: QApplication, service: UpdateService) -> tuple[UpdateViewModel, _EventBus]:
    bus = _EventBus()
    container = SimpleNamespace(update_controller=UpdateController(service), event_bus=bus)
    return UpdateViewModel(container, parent=qapp), bus  # type: ignore[arg-type]


def _settle(qapp: QApplication) -> None:
    QThreadPool.globalInstance().waitForDone(3000)
    qapp.processEvents()


def test_update_viewmodel_when_update_exists_should_open_dialog_and_dismiss(qapp: QApplication) -> None:
    vm, _ = _view_model(qapp, _service(_release()))

    vm.checkForUpdates()
    _settle(qapp)

    assert vm.isDialogOpen
    assert vm.latestVersion == "0.2.0"
    vm.dismiss()
    assert not vm.isDialogOpen


def test_update_viewmodel_when_manual_check_up_to_date_should_toast(qapp: QApplication) -> None:
    vm, bus = _view_model(qapp, _service(_release("v0.1.0")))

    vm.checkForUpdates()
    _settle(qapp)

    assert not vm.isDialogOpen
    assert [kind for _, kind in bus.toasts] == ["success"]


def test_update_viewmodel_when_startup_check_fails_should_stay_silent(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJE_TAKIP_UPDATE_CHECK", "1")
    vm, bus = _view_model(qapp, _service(fail=True))

    vm.checkOnStartup()
    _settle(qapp)

    assert bus.toasts == []
    assert not vm.isDialogOpen


def test_update_viewmodel_when_not_frozen_should_skip_startup_check(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PROJE_TAKIP_UPDATE_CHECK", raising=False)
    vm, _ = _view_model(qapp, _service(_release()))

    vm.checkOnStartup()
    _settle(qapp)

    assert not vm.isDialogOpen


def test_update_viewmodel_when_download_completes_should_launch_installer_and_request_quit(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    launched: list[Path] = []
    monkeypatch.setattr(UpdateService, "launch_installer", staticmethod(launched.append))
    digest = "sha256:" + hashlib.sha256(PAYLOAD).hexdigest()
    vm, _ = _view_model(qapp, _service(_release(digest=digest)))
    quits: list[bool] = []
    vm.quitRequested.connect(lambda: quits.append(True))

    vm.checkForUpdates()
    _settle(qapp)
    vm.startUpdate()
    _settle(qapp)

    assert quits == [True]
    assert len(launched) == 1 and launched[0].read_bytes() == PAYLOAD
    launched[0].unlink()


def test_update_viewmodel_when_download_fails_should_show_error_and_allow_retry(qapp: QApplication) -> None:
    vm, _ = _view_model(qapp, _service(_release(digest="sha256:" + "0" * 64)))

    vm.checkForUpdates()
    _settle(qapp)
    vm.startUpdate()
    _settle(qapp)

    assert vm.isDialogOpen
    assert not vm.isDownloading
    assert "doğrulanamadı" in vm.errorMessage


def test_update_info_is_immutable() -> None:
    info = UpdateInfo("0.2.0", "", "https://x", 1, None)

    with pytest.raises(AttributeError):
        info.version = "9"  # type: ignore[misc]


def test_set_version_when_run_should_update_all_four_files(tmp_path: Path) -> None:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from set_version import set_version

    root = Path(__file__).parent.parent
    for rel in ("app/config.py", "pyproject.toml", "installer/windows.iss", "packaging/version_info.txt"):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((root / rel).read_text(encoding="utf-8"), encoding="utf-8")

    set_version(tmp_path, "1.4.2")

    assert 'APP_VERSION = "1.4.2"' in (tmp_path / "app/config.py").read_text(encoding="utf-8")
    assert '\nversion = "1.4.2"' in (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert '#define MyAppVersion "1.4.2"' in (tmp_path / "installer/windows.iss").read_text(encoding="utf-8")
    info = (tmp_path / "packaging/version_info.txt").read_text(encoding="utf-8")
    assert "filevers=(1, 4, 2, 0)" in info and "u'ProductVersion', u'1.4.2.0'" in info


def test_set_version_when_version_invalid_should_exit(tmp_path: Path) -> None:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from set_version import set_version

    with pytest.raises(SystemExit):
        set_version(tmp_path, "1.4")
