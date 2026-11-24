"""Güncelleme güvenlik doğrulamaları, ağ açıcı ve kullanıcı tercihleri (`updates.json`)."""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, BinaryIO

from app import config
from core.exceptions.update_exceptions import UpdateError
from version import APP_NAME as EXE_APP_NAME
from version import RELEASE_REPO

logger = logging.getLogger(__name__)

NO_UPDATE_CHECK_ENV = "PROJE_TAKIP_NO_UPDATE_CHECK"
API_HOST = "api.github.com"
DOWNLOAD_HOST = "github.com"
CDN_HOST_SUFFIX = ".githubusercontent.com"
ALLOWED_REDIRECT_HOSTS = (DOWNLOAD_HOST, API_HOST)
MAX_SHA_FILE_BYTES = 4 * 1024
REQUEST_TIMEOUT_SEC = 15.0
SHA256_RE = re.compile(r"\b([0-9a-fA-F]{64})\b")

Response = BinaryIO
Opener = Callable[[urllib.request.Request], AbstractContextManager[Any]]


@dataclass
class UpdatePreferences:
    """Kullanıcı veri klasöründeki `updates.json`: açılış denetimi ve atlanan sürüm."""

    check_on_startup: bool = True
    skipped_version: str = ""


def _host_allowed(url: str, *, hosts: tuple[str, ...], allow_cdn: bool) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return False
    host = parsed.hostname.lower()
    return host in hosts or (allow_cdn and host.endswith(CDN_HOST_SUFFIX))


def validate_download_url(url: str, repo: str = RELEASE_REPO) -> None:
    """İndirme adresinin yalnızca bu deponun GitHub Releases yolu olduğunu doğrular."""
    parsed = urllib.parse.urlparse(url)
    prefix = f"/{repo}/releases/download/"
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host != DOWNLOAD_HOST or not parsed.path.startswith(prefix):
        raise UpdateError("Güncelleme adresi güvenilir değil; indirme reddedildi.")


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Yönlendirmeyi yalnızca github.com, api.github.com ve *.githubusercontent.com adreslerine kabul eder."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        if not _host_allowed(newurl, hosts=ALLOWED_REDIRECT_HOSTS, allow_cdn=True):
            raise urllib.error.URLError(f"Güvenilmeyen yönlendirme reddedildi: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def default_opener() -> Opener:
    """Güvenli yönlendirme denetçili varsayılan HTTP açıcısını döndürür."""
    director = urllib.request.build_opener(_SafeRedirectHandler)

    def _open(request: urllib.request.Request) -> AbstractContextManager[Any]:
        return director.open(request, timeout=REQUEST_TIMEOUT_SEC)  # type: ignore[no-any-return]

    return _open


def read_limited(response: Response, limit: int) -> bytes:
    """Sunucu yanıtını en fazla `limit` bayt okuyarak bellek aşımını engeller."""
    data = response.read(limit + 1)
    if len(data) > limit:
        raise UpdateError("Sunucu yanıtı beklenenden büyük; işlem durduruldu.")
    return data


def build_request(url: str, *, accept: str) -> urllib.request.Request:
    """Kimlik bilgisi içermeyen standart güncelleme HTTP isteği oluşturur."""
    return urllib.request.Request(url, headers={"User-Agent": f"{EXE_APP_NAME}-updater", "Accept": accept})


def parse_sha256_text(text: str) -> str | None:
    """`.sha256` yan dosya metninden 64 haneli SHA-256 özetini ayıklar."""
    match = SHA256_RE.search(text)
    return match.group(1).lower() if match else None


def resolve_sha256(sha256: str | None, sha256_url: str | None, opener: Opener | None = None) -> str:
    """Önce asset digest alanını, yoksa `.sha256` yan dosyasını çözer; ikisi de yoksa reddeder."""
    if sha256:
        return sha256
    if sha256_url:
        try:
            with (opener or default_opener())(build_request(sha256_url, accept="text/plain")) as response:
                text = read_limited(response, MAX_SHA_FILE_BYTES).decode("utf-8", errors="replace")
        except (urllib.error.URLError, OSError) as exc:
            raise UpdateError(f"Özet dosyası indirilemedi: {exc}") from exc
        parsed = parse_sha256_text(text)
        if parsed:
            return parsed
    raise UpdateError("Kurulum dosyasının SHA-256 özeti bulunamadı; güvenlik nedeniyle güncelleme reddedildi.")


def update_check_disabled_by_env() -> bool:
    """`PROJE_TAKIP_NO_UPDATE_CHECK` tanımlı ve 0 değilse True döner."""
    return os.environ.get(NO_UPDATE_CHECK_ENV, "").strip() not in ("", "0")


def preferences_path() -> Path:
    """`updates.json` tercih dosyasının aktif yolunu döndürür."""
    return config.UPDATE_PREFERENCES_PATH


def load_preferences() -> UpdatePreferences:
    """`updates.json` dosyasını okur; yoksa veya bozuksa varsayılan tercihleri döndürür."""
    path = preferences_path()
    if not path.is_file():
        return UpdatePreferences()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("Failed to read update preferences, using defaults: %s", exc)
        return UpdatePreferences()
    if not isinstance(raw, dict):
        return UpdatePreferences()
    return UpdatePreferences(
        check_on_startup=bool(raw.get("check_on_startup", True)),
        skipped_version=str(raw.get("skipped_version", "")),
    )


def save_preferences(prefs: UpdatePreferences) -> None:
    """Güncelleme tercihlerini `updates.json` dosyasına yazar."""
    path = preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(prefs), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_check_allowed() -> bool:
    """Açılış denetiminin hem kullanıcı tercihince hem ortam değişkenince izinli olup olmadığını döndürür."""
    return load_preferences().check_on_startup and not update_check_disabled_by_env()
