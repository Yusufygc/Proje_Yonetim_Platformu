"""
UI metinleri için ortak çeviri yardımcısı.

Sayfa/widget dosyalarının her birinde ayrı `_tr` tanımlamak yerine tek erişim
noktası sunar; ileride dil değişimi sinyali eklendiğinde tek yerden genişler.
"""
from core.managers.string_manager import StringManager


def tr(key: str, default: str = "") -> str:
    """Anahtara karşılık gelen yerelleştirilmiş metni döndürür."""
    return StringManager.get(key, default)
