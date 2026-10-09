"""Uygulama güncelleme servisi: GitHub Releases'te yeni sürüm arar, kurulum dosyasını indirir ve başlatır."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from core.exceptions.update_exceptions import UpdateError

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 10
_CHUNK_BYTES = 64 * 1024
_VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")

ProgressCallback = Callable[[int], None]


@dataclass(frozen=True)
class UpdateInfo:
    """Yayınlanmış yeni sürümün kullanıcıya gösterilen ve indirmek için gereken bilgileri."""

    version: str
    notes: str
    download_url: str
    size: int
    sha256: str | None


def parse_version(text: str) -> tuple[int, int, int] | None:
    """`v1.2.3` ya da `1.2.3` biçimini sayı üçlüsüne çevirir; ön sürüm gibi diğer biçimler None döner."""
    match = _VERSION_PATTERN.match(text.strip())
    if match is None:
        return None
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


class UpdateService:
    """Güncelleme denetimi ve kurulumu; ağ erişimi `opener` ile değiştirilebilir (test için)."""

    def __init__(
        self,
        current_version: str,
        repository: str,
        asset_name: str,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        self._current_version = current_version
        self._repository = repository
        self._asset_name = asset_name
        self._opener = opener

    def check_for_update(self) -> UpdateInfo | None:
        """Yeni sürüm varsa bilgisini, yoksa None döner; ağ ve ayrıştırma hataları UpdateError olur."""
        release = self._fetch_latest_release()
        latest = parse_version(str(release.get("tag_name", "")))
        current = parse_version(self._current_version)
        if latest is None or current is None or latest <= current:
            return None
        asset = self._find_asset(release)
        digest = str(asset.get("digest") or "")
        return UpdateInfo(
            version=".".join(str(n) for n in latest),
            notes=str(release.get("body") or ""),
            download_url=self._validated_download_url(str(asset.get("browser_download_url", ""))),
            size=int(asset.get("size") or 0),
            sha256=digest.removeprefix("sha256:") if digest.startswith("sha256:") else None,
        )

    def download_installer(self, info: UpdateInfo, progress_callback: ProgressCallback | None = None) -> Path:
        """Kurulum dosyasını geçici klasöre indirir; boyut veya özet uyuşmazsa dosyayı silip hata verir."""
        target_dir = Path(tempfile.gettempdir()) / "ProjeTakipUpdate"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / self._asset_name
        try:
            received, sha256 = self._download_to(info, target, progress_callback)
            self._verify(info, received, sha256)
        except UpdateError:
            target.unlink(missing_ok=True)
            raise
        except OSError as exc:
            target.unlink(missing_ok=True)
            raise UpdateError(f"Güncelleme indirilemedi: {exc}") from exc
        return target

    @staticmethod
    def launch_installer(installer: Path) -> None:
        """Kurulumu uygulamadan bağımsız bir süreç olarak başlatır; çağıran uygulamayı kapatmalıdır."""
        if os.name != "nt":
            raise UpdateError("Otomatik kurulum yalnızca Windows'ta desteklenir.")
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        # SILENT: sihirbaz sormadan ilerleme penceresiyle kurar; kurulum sonrası uygulama kendiliğinden açılır.
        # Sessiz kurulum hata penceresi göstermez; başarısız olursa nedenini bu log anlatır.
        log_path = installer.with_name("install.log")
        subprocess.Popen(
            [str(installer), "/SILENT", "/SUPPRESSMSGBOXES", "/CLOSEAPPLICATIONS", f"/LOG={log_path}"],
            close_fds=True,
            creationflags=flags,
        )

    # ── Yardımcılar ─────────────────────────────────────────────────────────

    def _open(self, url: str) -> Any:
        request = Request(url, headers={"User-Agent": "ProjeTakipPlatformu", "Accept": "application/vnd.github+json"})
        try:
            return self._opener(request, timeout=_TIMEOUT_SECONDS)
        except OSError as exc:
            raise UpdateError(f"Güncelleme sunucusuna ulaşılamadı: {exc}") from exc

    def _download_to(self, info: UpdateInfo, target: Path, progress_callback: ProgressCallback | None) -> tuple[int, str]:
        digest = hashlib.sha256()
        received = 0
        with self._open(info.download_url) as response, target.open("wb") as out:
            while chunk := response.read(_CHUNK_BYTES):
                out.write(chunk)
                digest.update(chunk)
                received += len(chunk)
                if progress_callback is not None and info.size > 0:
                    progress_callback(min(100, received * 100 // info.size))
        return received, digest.hexdigest()

    def _fetch_latest_release(self) -> dict[str, Any]:
        url = f"https://api.github.com/repos/{self._repository}/releases/latest"
        try:
            with self._open(url) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, ValueError) as exc:
            raise UpdateError(f"Sürüm bilgisi okunamadı: {exc}") from exc
        if not isinstance(payload, dict):
            raise UpdateError("Sürüm bilgisi beklenmeyen biçimde.")
        return payload

    def _find_asset(self, release: dict[str, Any]) -> dict[str, Any]:
        for asset in release.get("assets") or []:
            if isinstance(asset, dict) and asset.get("name") == self._asset_name:
                return asset
        raise UpdateError(f"Sürümde {self._asset_name} dosyası yok.")

    def _validated_download_url(self, url: str) -> str:
        """Yalnızca bu deponun GitHub sürüm dosyalarına izin verir; başka adres indirilmez."""
        parsed = urlparse(url)
        expected_prefix = f"/{self._repository}/releases/download/"
        if parsed.scheme != "https" or parsed.netloc != "github.com" or not parsed.path.startswith(expected_prefix):
            raise UpdateError("Güncelleme adresi güvenilir değil.")
        return url

    @staticmethod
    def _verify(info: UpdateInfo, received: int, sha256: str) -> None:
        if info.size and received != info.size:
            raise UpdateError("İndirilen dosya eksik; boyut uyuşmuyor.")
        if info.sha256 and sha256.lower() != info.sha256.lower():
            raise UpdateError("İndirilen dosya doğrulanamadı; özet uyuşmuyor.")
