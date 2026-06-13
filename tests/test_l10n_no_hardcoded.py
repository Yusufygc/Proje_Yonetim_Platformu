"""
L10N regresyon kontrolü: presentation katmanında hardcoded Türkçe metin avcısı.

Kural: UI metinleri StringManager üzerinden (tr / _tr / StringManager.get)
çekilir; bu çağrıların default argümanları ve docstring/yorumlar muaftır.

Ratchet mantığı:
- ALLOWLIST dışındaki bir dosyada Türkçe literal bulunursa test FAIL olur
  (yeni kod temiz kalmak zorunda).
- ALLOWLIST'teki bir dosya tamamen temizlenmişse test yine FAIL olur ve
  listeden çıkarılması istenir (geri kayma kapısı kapanır).
Migrasyon ilerledikçe ALLOWLIST küçülür ve sonunda silinir.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIR = PROJECT_ROOT / "presentation"
TURKISH_CHARS = re.compile(r"[çğıöşüÇĞİÖŞÜ]")

# tr()/_tr()/StringManager.get() — bilinçli default'lar muaf tutulur.
_TRANSLATION_FUNCS = {"tr", "_tr", "get"}

# Henüz StringManager'a taşınmamış dosyalar. YENİ DOSYA EKLENMEZ;
# bir dosya migrate edilince buradan silinir (test temiz dosyayı raporlar).
ALLOWLIST: set[str] = set()  # Migrasyon tamamlandı (2026-06-13) — liste boş kalmalı.


def _hardcoded_turkish_lines(path: Path) -> list[int]:
    """Dosyadaki muaf olmayan Türkçe string literal'lerin satır numaraları."""
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    exempt: set[int] = set()

    # "# l10n: ..." pragma'lı satırlar muaf:
    #   data → saklanan veri değeri (örn. DB'deki project_type)
    #   log  → geliştiriciye dönük log mesajı, UI metni değil
    pragma_lines = {
        lineno
        for lineno, line in enumerate(source.splitlines(), start=1)
        if "# l10n: data" in line or "# l10n: log" in line
    }

    # Çeviri çağrılarının argümanları muaf
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name in _TRANSLATION_FUNCS:
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, str):
                        exempt.add(id(child))

    # Docstring'ler muaf
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
            ):
                exempt.add(id(node.body[0].value))

    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in exempt
        and node.lineno not in pragma_lines
        and TURKISH_CHARS.search(node.value)
    ]


def _scan() -> dict[str, list[int]]:
    findings: dict[str, list[int]] = {}
    for path in sorted(SCAN_DIR.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        lines = _hardcoded_turkish_lines(path)
        if lines:
            findings[rel] = lines
    return findings


def test_no_new_hardcoded_turkish_strings() -> None:
    findings = _scan()

    violators = {rel: lines for rel, lines in findings.items() if rel not in ALLOWLIST}
    assert not violators, (
        "Allowlist dışı dosyalarda hardcoded Türkçe metin bulundu. "
        "Metinleri presentation.utils.i18n.tr ile strings.tr.json'a taşıyın:\n"
        + "\n".join(f"  {rel}: satır {lines}" for rel, lines in violators.items())
    )

    cleaned = ALLOWLIST - set(findings)
    assert not cleaned, (
        "Şu dosyalar artık temiz; ALLOWLIST'ten çıkarın (ratchet ilerlesin):\n"
        + "\n".join(f"  {rel}" for rel in sorted(cleaned))
    )


def test_locale_files_have_matching_keys_and_placeholders() -> None:
    """Tüm dil dosyaları aynı anahtar setini ve format alanlarını içermeli.

    Eksik anahtar çalışma zamanında default'a düşer (sessiz regresyon);
    placeholder uyumsuzluğu ise .format() çağrısında KeyError üretir.
    """
    import json
    import string

    locales_dir = PROJECT_ROOT / "resources" / "locales"
    files = sorted(locales_dir.glob("strings.*.json"))
    assert len(files) >= 2, "En az tr ve en dil dosyası beklenir."

    data = {f.name: json.loads(f.read_text(encoding="utf-8")) for f in files}
    reference_name, reference = next(iter(data.items()))

    formatter = string.Formatter()

    def placeholders(text: str) -> set[str]:
        return {field for _, field, _, _ in formatter.parse(text) if field}

    for name, strings in data.items():
        missing = reference.keys() - strings.keys()
        extra = strings.keys() - reference.keys()
        assert not missing and not extra, (
            f"{name} ile {reference_name} anahtarları uyuşmuyor.\n"
            f"  Eksik: {sorted(missing)}\n  Fazla: {sorted(extra)}"
        )
        for key in reference:
            ref_ph = placeholders(reference[key])
            cur_ph = placeholders(strings[key])
            assert ref_ph == cur_ph, (
                f"{name}:{key} format alanları uyuşmuyor: {sorted(cur_ph)} != {sorted(ref_ph)}"
            )
