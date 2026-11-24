"""Uygulama içi güncelleme servisi: GitHub Releases denetimi, SHA-256 doğrulamalı indirme ve sessiz kurulum."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.exceptions.update_exceptions import InstallerBlockedError, UpdateError
from services.update_security import (
    API_HOST,
    NO_UPDATE_CHECK_ENV,
    SHA256_RE,
    Opener,
    UpdatePreferences,
    _SafeRedirectHandler,
    build_request,
    default_opener,
    load_preferences,
    parse_sha256_text,
    preferences_path,
    read_limited,
    save_preferences,
    update_check_allowed,
    update_check_disabled_by_env,
    validate_download_url,
)
from services.update_security import (
    resolve_sha256 as _resolve_sha256_values,
)
from version import APP_NAME as EXE_APP_NAME
from version import RELEASE_REPO, __version__

logger = logging.getLogger(__name__)

MAX_INSTALLER_BYTES = 400 * 1024 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_NOTES_CHARS = 4000
CHUNK_BYTES = 64 * 1024
WINERROR_BLOCKED = (4551, 1260)

_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
ASSET_NAME_RE = re.compile(rf"^{re.escape(EXE_APP_NAME)}-Setup-\d+\.\d+\.\d+\.exe$")

ProgressCallback = Callable[[int], None]
ByteProgressCallback = Callable[[int, int], None]

__all__ = [
    "ASSET_NAME_RE", "InstallerBlockedError", "MAX_INSTALLER_BYTES", "MAX_JSON_BYTES",
    "MAX_NOTES_CHARS", "NO_UPDATE_CHECK_ENV", "Opener", "ProgressCallback", "UpdateError",
    "UpdateInfo", "UpdatePreferences", "UpdateService", "_SafeRedirectHandler",
    "build_installer_command", "check_for_update", "download_installer",
    "fetch_latest_release", "installer_asset_name", "is_newer_version",
    "launch_installer", "load_preferences", "parse_sha256_text", "parse_version",
    "preferences_path", "release_page_url", "release_to_update", "resolve_sha256",
    "save_preferences", "select_installer_asset", "update_check_allowed",
    "update_check_disabled_by_env", "validate_download_url",
]


@dataclass(frozen=True)
class UpdateInfo:
    """Yüklü sürümden yeni, doğrulanabilir bir yayının özeti."""

    version: str
    tag: str
    asset_name: str
    download_url: str
    size: int
    sha256: str | None = None
    sha256_url: str | None = None
    notes: str = ""
    html_url: str = ""
    published_at: str = ""


def parse_version(text: str) -> tuple[int, int, int] | None:
    """`2.1.5` / `v2.1.5` -> `(2, 1, 5)`; ön sürüm (`-rc1`) veya bozuk biçim için `None`."""
    match = _VERSION_RE.match(text.strip())
    if not match:
        return None
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def is_newer_version(candidate: str, current: str) -> bool:
    """Sayısal sürüm karşılaştırması (`2.10.0 > 2.9.0`); tanınmayan biçim yeni sayılmaz."""
    cand, cur = parse_version(candidate), parse_version(current)
    return cand is not None and cur is not None and cand > cur


def installer_asset_name(version: str) -> str:
    """Verilen sürüm için beklenen kurulum dosyası adını döndürür."""
    return f"{EXE_APP_NAME}-Setup-{version}.exe"


def fetch_latest_release(repo: str = RELEASE_REPO, opener: Opener | None = None) -> dict[str, Any]:
    """`GET /repos/<depo>/releases/latest` (tek istek, kimlik bilgisi yok; 404 hata sayılmaz)."""
    url = f"https://{API_HOST}/repos/{repo}/releases/latest"
    try:
        with (opener or default_opener())(build_request(url, accept="application/vnd.github+json")) as response:
            payload = json.loads(read_limited(response, MAX_JSON_BYTES).decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {}
        raise UpdateError(f"Güncelleme sunucusuna ulaşılamadı: {exc}") from exc
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise UpdateError(f"Güncelleme sunucusuna ulaşılamadı: {exc}") from exc
    if not isinstance(payload, dict):
        raise UpdateError("Güncelleme sunucusu beklenmeyen bir yanıt verdi.")
    return payload


def select_installer_asset(
    assets: list[Any], version: str, repo: str = RELEASE_REPO
) -> tuple[dict[str, Any], str | None] | None:
    """Release varlıkları arasından sürüm kurulum dosyasını ve opsiyonel `.sha256` URL'sini seçer."""
    expected = installer_asset_name(version)
    if not ASSET_NAME_RE.match(expected):
        return None
    installer: dict[str, Any] | None = None
    sha_asset: dict[str, Any] | None = None
    for item in assets:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if name == expected:
            installer = item
        elif name == f"{expected}.sha256":
            sha_asset = item
    if installer is None:
        return None
    sha_url = str(sha_asset.get("browser_download_url", "")) if sha_asset else None
    if sha_url:
        validate_download_url(sha_url, repo)
    return installer, sha_url


def _extract_digest(installer: dict[str, Any]) -> str | None:
    digest = str(installer.get("digest") or "")
    if digest.lower().startswith("sha256:") and SHA256_RE.search(digest):
        return digest.split(":", 1)[1].lower()
    return None


def _build_update_info(
    release: dict[str, Any],
    installer: dict[str, Any],
    sha_url: str | None,
    version: str,
    tag: str,
    repo: str,
) -> UpdateInfo:
    url = str(installer.get("browser_download_url", ""))
    validate_download_url(url, repo)
    size = int(installer.get("size", 0) or 0)
    if size <= 0 or size > MAX_INSTALLER_BYTES:
        raise UpdateError("Kurulum dosyasının boyutu geçersiz; güncelleme reddedildi.")
    return UpdateInfo(
        version=version,
        tag=tag,
        asset_name=installer_asset_name(version),
        download_url=url,
        size=size,
        sha256=_extract_digest(installer),
        sha256_url=sha_url,
        notes=str(release.get("body") or "")[:MAX_NOTES_CHARS],
        html_url=str(release.get("html_url") or f"https://github.com/{repo}/releases/tag/{tag}"),
        published_at=str(release.get("published_at") or ""),
    )


def release_to_update(release: dict[str, Any], current_version: str, repo: str = RELEASE_REPO) -> UpdateInfo | None:
    """Yayın JSON'unu yüklü sürümle kıyaslar; taslak, ön sürüm, eski sürüm ve uygunsuz varlıkta `None`."""
    if release.get("draft") or release.get("prerelease"):
        return None
    tag = str(release.get("tag_name", ""))
    parsed = parse_version(tag)
    if parsed is None or not is_newer_version(tag, current_version):
        return None
    version = ".".join(str(part) for part in parsed)
    assets = release.get("assets")
    if not isinstance(assets, list):
        return None
    selected = select_installer_asset(assets, version, repo)
    if selected is None:
        return None
    installer, sha_url = selected
    return _build_update_info(release, installer, sha_url, version, tag, repo)


def check_for_update(current_version: str, repo: str = RELEASE_REPO, opener: Opener | None = None) -> UpdateInfo | None:
    """GitHub Releases'teki son sürümü denetler."""
    return release_to_update(fetch_latest_release(repo, opener), current_version, repo)


def resolve_sha256(info: UpdateInfo, opener: Opener | None = None) -> str:
    """`UpdateInfo` için zorunlu SHA-256 özetini döndürür; yoksa `UpdateError` fırlatır."""
    return _resolve_sha256_values(info.sha256, info.sha256_url, opener)


def update_download_dir() -> Path:
    """İndirilen kurulum dosyasının geçici klasörünü döndürür."""
    return Path(tempfile.gettempdir()) / f"{EXE_APP_NAME}Update"


def _stream_to_partial(
    info: UpdateInfo,
    partial: Path,
    progress: ByteProgressCallback | None,
    opener: Opener | None,
) -> tuple[int, str]:
    hasher = hashlib.sha256()
    received = 0
    with (opener or default_opener())(build_request(info.download_url, accept="application/octet-stream")) as response:
        with partial.open("wb") as out:
            while chunk := response.read(CHUNK_BYTES):
                received += len(chunk)
                if received > min(info.size, MAX_INSTALLER_BYTES):
                    raise UpdateError("İndirilen dosya beklenenden büyük; işlem durduruldu.")
                hasher.update(chunk)
                out.write(chunk)
                if progress is not None:
                    progress(received, info.size)
    return received, hasher.hexdigest()


def _finalize_download(
    partial: Path,
    target: Path,
    received: int,
    expected_size: int,
    actual_sha: str,
    expected_sha: str,
) -> Path:
    if received != expected_size:
        partial.unlink(missing_ok=True)
        raise UpdateError("İndirilen dosyanın boyutu Release ile uyuşmuyor; dosya silindi.")
    if actual_sha.lower() != expected_sha.lower():
        partial.unlink(missing_ok=True)
        raise UpdateError("SHA-256 özeti uyuşmuyor; dosya silindi ve güncelleme iptal edildi.")
    target.unlink(missing_ok=True)
    partial.replace(target)
    return target


def download_installer(
    info: UpdateInfo,
    dest_dir: Path | None = None,
    progress: ByteProgressCallback | None = None,
    opener: Opener | None = None,
    repo: str = RELEASE_REPO,
) -> Path:
    """Kurulum dosyasını `.exe.part` olarak indirir, boyut ve SHA-256 doğrular, hatada siler."""
    validate_download_url(info.download_url, repo)
    if not ASSET_NAME_RE.match(info.asset_name) or info.asset_name != installer_asset_name(info.version):
        raise UpdateError("Kurulum dosyası adı beklenen desene uymuyor; indirme reddedildi.")
    expected_sha = resolve_sha256(info, opener)
    target_dir = dest_dir or update_download_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / info.asset_name
    partial = target.with_suffix(".exe.part")
    try:
        received, actual_sha = _stream_to_partial(info, partial, progress, opener)
    except (urllib.error.URLError, OSError, UpdateError) as exc:
        partial.unlink(missing_ok=True)
        raise exc if isinstance(exc, UpdateError) else UpdateError(f"İndirme başarısız: {exc}") from exc
    return _finalize_download(partial, target, received, info.size, actual_sha, expected_sha)


def build_installer_command(installer_path: Path, log_dir: Path | None = None) -> list[str]:
    """Sessiz kurulum ve günlük kaydı için sabit argüman listesini döndürür."""
    log_path = (log_dir or installer_path.parent) / "install.log"
    return [
        str(installer_path),
        "/SILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/CLOSEAPPLICATIONS",
        f"/LOG={log_path}",
    ]


def _shell_execute(path: str, params: str) -> int:
    import ctypes

    return int(ctypes.windll.shell32.ShellExecuteW(None, "open", path, params, None, 1))


def launch_installer(
    installer_path: Path,
    log_dir: Path | None = None,
    popen: Callable[..., Any] = subprocess.Popen,
    shell_execute: Callable[[str, str], int] | None = None,
) -> None:
    """Kurulum dosyasını bağımsız süreç olarak başlatır; SAC engelinde ShellExecute yolunu dener."""
    if os.name != "nt" and popen is subprocess.Popen:
        raise UpdateError("Otomatik kurulum yalnızca Windows'ta desteklenir.")
    if not ASSET_NAME_RE.match(installer_path.name):
        raise UpdateError("Kurulum dosyası adı beklenen desene uymuyor; başlatılmadı.")
    args = build_installer_command(installer_path, log_dir)
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    try:
        popen(args, creationflags=flags, close_fds=True)
        return
    except OSError as exc:
        if getattr(exc, "winerror", None) not in WINERROR_BLOCKED:
            raise UpdateError(f"Kurulum başlatılamadı: {exc}") from exc
        logger.warning("Installer direct launch blocked (WinError %s); trying ShellExecute", exc.winerror)

    execute = shell_execute or _shell_execute
    params = " ".join(f'"{a}"' if " " in a else a for a in args[1:])
    if execute(str(installer_path), params) <= 32:
        raise InstallerBlockedError("Windows kurulum dosyasını şimdilik engelledi.")


def release_page_url(repo: str = RELEASE_REPO) -> str:
    """GitHub Releases son sürüm sayfası URL'sini döndürür."""
    return f"https://github.com/{repo}/releases/latest"


class UpdateService:
    """DI uyumlu güncelleme servisi cephesi."""

    def __init__(
        self,
        current_version: str = __version__,
        repository: str = RELEASE_REPO,
        opener: Opener | None = None,
    ) -> None:
        self._current_version = current_version
        self._repository = repository
        self._opener = opener

    def check_for_update(self, *, respect_skipped: bool = False) -> UpdateInfo | None:
        """Yeni sürüm varsa bilgisini döndürür; `respect_skipped=True` ise atlanan sürümü gizler."""
        info = check_for_update(self._current_version, self._repository, self._opener)
        if info is None:
            return None
        if respect_skipped and load_preferences().skipped_version == info.version:
            return None
        return info

    def download_installer(
        self,
        info: UpdateInfo,
        progress_callback: ProgressCallback | None = None,
        dest_dir: Path | None = None,
    ) -> Path:
        """Kurulum dosyasını yüzde ilerleme bildirimiyle indirir ve doğrular."""
        def _on_bytes(done: int, total: int) -> None:
            if progress_callback is not None and total > 0:
                progress_callback(min(100, done * 100 // total))

        return download_installer(
            info,
            dest_dir=dest_dir,
            progress=_on_bytes if progress_callback else None,
            opener=self._opener,
            repo=self._repository,
        )

    @staticmethod
    def launch_installer(installer_path: Path) -> None:
        """İndirilen kurulum dosyasını bağımsız süreç olarak başlatır."""
        launch_installer(installer_path, log_dir=installer_path.parent)

    def update_check_allowed(self) -> bool:
        """Açılış denetiminin izinli olup olmadığını döndürür."""
        return update_check_allowed()

    def set_check_on_startup(self, enabled: bool) -> None:
        """Açılışta otomatik güncelleme kontrolü tercihini kaydeder."""
        prefs = load_preferences()
        prefs.check_on_startup = bool(enabled)
        save_preferences(prefs)

    def skip_version(self, version: str) -> None:
        """Belirtilen sürümü açılış bildirimlerinde atlanacak olarak kaydeder."""
        prefs = load_preferences()
        prefs.skipped_version = version
        save_preferences(prefs)

    def release_page_url(self) -> str:
        """GitHub Releases sayfasının URL'sini döndürür."""
        return release_page_url(self._repository)
