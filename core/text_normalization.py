"""Arama için Türkçe uyumlu metin normalleştirme yardımcıları."""
from __future__ import annotations

SQL_FOLD_FUNCTION = "tr_fold"
LIKE_ESCAPE = "\\"


def normalize_search_text(text: str | None) -> str:
    """Büyük/küçük harf ve noktalı/noktasız i farkını yok sayan karşılaştırma anahtarı üretir.

    Python'un `lower()` metodu `İ` harfini iki karaktere böler ve `I` harfini `ı` yerine `i`
    yapar; SQLite'ın LIKE işleci ise yalnızca ASCII harflerde büyük/küçük harf duyarsızdır.
    """
    if not text:
        return ""
    return text.replace("İ", "i").replace("I", "ı").lower().replace("ı", "i")


def escape_like(text: str) -> str:
    """Kullanıcı girdisindeki LIKE jokerlerini (`%`, `_`) düz karakter olarak işaretler."""
    return (
        text.replace(LIKE_ESCAPE, LIKE_ESCAPE * 2)
        .replace("%", f"{LIKE_ESCAPE}%")
        .replace("_", f"{LIKE_ESCAPE}_")
    )
