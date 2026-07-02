"""
Premium font dosyalarını GitHub üzerinden resources/fonts/ dizinine indirir.

Kullanım:
    python scripts/download_fonts.py           # eksik fontları indir
    python scripts/download_fonts.py --force   # var olanları da yeniden indir

Dış bağımlılık yok; yalnızca stdlib kullanılır.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

# Proje kökü bu scriptin bir üst dizinidir
_ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = _ROOT / "resources" / "fonts"

_PJS_BASE = (
    "https://raw.githubusercontent.com/tokotype/PlusJakartaSans/master/fonts/ttf/"
)
_JBM_BASE = (
    "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/ttf/"
)
# jsDelivr @fontsource CDN — resmi font repolarının aksine sürümlü/stabil
# static per-weight dosya sunar (Roboto/Open Sans'ın kendi repoları değişken
# font formatına geçtiği için ham GitHub yolu güvenilir değil).
_FONTSOURCE_BASE = "https://cdn.jsdelivr.net/npm/@fontsource"

# filename → download URL
FONT_MANIFEST: dict[str, str] = {
    "PlusJakartaSans-Light.ttf":     _PJS_BASE + "PlusJakartaSans-Light.ttf",
    "PlusJakartaSans-Regular.ttf":   _PJS_BASE + "PlusJakartaSans-Regular.ttf",
    "PlusJakartaSans-Medium.ttf":    _PJS_BASE + "PlusJakartaSans-Medium.ttf",
    "PlusJakartaSans-SemiBold.ttf":  _PJS_BASE + "PlusJakartaSans-SemiBold.ttf",
    "PlusJakartaSans-Bold.ttf":      _PJS_BASE + "PlusJakartaSans-Bold.ttf",
    "PlusJakartaSans-ExtraBold.ttf": _PJS_BASE + "PlusJakartaSans-ExtraBold.ttf",
    "JetBrainsMono-Regular.ttf":     _JBM_BASE + "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Medium.ttf":      _JBM_BASE + "JetBrainsMono-Medium.ttf",
    "roboto-latin-400-normal.woff2":    f"{_FONTSOURCE_BASE}/roboto@latest/files/roboto-latin-400-normal.woff2",
    "roboto-latin-500-normal.woff2":    f"{_FONTSOURCE_BASE}/roboto@latest/files/roboto-latin-500-normal.woff2",
    "roboto-latin-700-normal.woff2":    f"{_FONTSOURCE_BASE}/roboto@latest/files/roboto-latin-700-normal.woff2",
    "open-sans-latin-400-normal.woff2": f"{_FONTSOURCE_BASE}/open-sans@latest/files/open-sans-latin-400-normal.woff2",
    "open-sans-latin-600-normal.woff2": f"{_FONTSOURCE_BASE}/open-sans@latest/files/open-sans-latin-600-normal.woff2",
    "open-sans-latin-700-normal.woff2": f"{_FONTSOURCE_BASE}/open-sans@latest/files/open-sans-latin-700-normal.woff2",
}


def download_all(force: bool = False) -> dict[str, bool]:
    """
    Manifest'teki her fontu indirir.

    Returns:
        {filename: True (başarılı) | False (hata/atlandı)} sözlüğü.
    """
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, bool] = {}

    for filename, url in FONT_MANIFEST.items():
        dest = FONTS_DIR / filename
        if dest.exists() and not force:
            print(f"  atlandı (zaten mevcut): {filename}")
            results[filename] = True
            continue

        try:
            print(f"  indiriliyor: {filename} ...", end="", flush=True)
            urllib.request.urlretrieve(url, dest)
            size_kb = dest.stat().st_size // 1024
            print(f" OK ({size_kb} KB)")
            results[filename] = True
        except Exception as exc:  # noqa: BLE001
            print(f" HATA: {exc}")
            dest.unlink(missing_ok=True)
            results[filename] = False

    return results


def _premium_fonts_present() -> bool:
    """Manifest'teki her dosya diskte mevcutsa True döner (ilk yükleme kontrolü için).

    Sadece PJS+JBM kontrol edilseydi, bunlar zaten kurulu olan mevcut bir
    kurulumda yeni eklenen fontlar (örn. Roboto/Open Sans) hiç indirilmezdi.
    """
    return all((FONTS_DIR / filename).exists() for filename in FONT_MANIFEST)


def ensure_fonts() -> None:
    """
    main.py tarafından çağrılır. Eksik premium fontlar varsa sessizce indirir.
    İndirme başarısız olursa uygulama fallback fontlarla devam eder.
    """
    if _premium_fonts_present():
        return
    print("Premium fontlar eksik, indiriliyor...")
    download_all()


if __name__ == "__main__":
    force = "--force" in sys.argv
    print(f"Font dizini: {FONTS_DIR}")
    print(f"Mod: {'zorla yeniden indir' if force else 'eksikleri indir'}\n")
    results = download_all(force=force)
    success = sum(v for v in results.values())
    print(f"\nTamamlandı: {success}/{len(results)} font hazır.")
    sys.exit(0 if success == len(results) else 1)
