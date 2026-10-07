"""Uygulama sürümünü dört dosyada birden günceller: config, pyproject, exe sürüm bilgisi, installer.

Kullanım:  python scripts/set_version.py 0.2.0
Sonra:     git commit -am "chore(surum): v0.2.0" && git tag v0.2.0 && git push origin <dal> v0.2.0
Release iş akışı etiket ile app/config.py sürümünün aynı olduğunu doğrular; farklıysa yayın yapmaz.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _replace_once(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"{path.name}: sürüm satırı bulunamadı")
    path.write_text(new_text, encoding="utf-8", newline="")


def set_version(root: Path, version: str) -> None:
    match = _SEMVER.match(version)
    if match is None:
        raise SystemExit(f"Geçersiz sürüm: {version!r} (örnek: 0.2.0)")
    major, minor, patch = match.groups()
    quad = f"{major}, {minor}, {patch}, 0"

    _replace_once(root / "app" / "config.py", r'^APP_VERSION = ".*"$', f'APP_VERSION = "{version}"')
    _replace_once(root / "pyproject.toml", r'^version = ".*"$', f'version = "{version}"')
    _replace_once(root / "installer" / "windows.iss", r'^#define MyAppVersion ".*"$', f'#define MyAppVersion "{version}"')
    info = root / "packaging" / "version_info.txt"
    _replace_once(info, r"filevers=\(.*\)", f"filevers=({quad})")
    _replace_once(info, r"prodvers=\(.*\)", f"prodvers=({quad})")
    _replace_once(info, r"u'FileVersion', u'.*?'", f"u'FileVersion', u'{version}.0'")
    _replace_once(info, r"u'ProductVersion', u'.*?'", f"u'ProductVersion', u'{version}.0'")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    set_version(_ROOT, argv[1])
    print(f"Sürüm {argv[1]} olarak ayarlandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
