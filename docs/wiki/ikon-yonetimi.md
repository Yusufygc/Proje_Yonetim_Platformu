# İkon Yönetimi

## IconManager (`core/managers/icon_manager.py`)
- Singleton; `resources/icons/*.svg` okur.
- `get_icon(name, color)` — SVG içinde `fill/stroke="currentColor"` → verilen hex; `QPixmap.loadFromData` ile QIcon üretir; `name_color` anahtarıyla cache'ler.
- `get_svg_content(name, color)` — renklendirilmiş ham SVG metni (QSS ok ikonları için).

## ThemeManager entegrasyonu
`ThemeManager._generate_icon_tokens()` chevron up/down ikonlarını aktif `text_secondary` rengiyle üretip `resources/styles/_cache/` dizinine yazar; `@icon_chevron_down` token'ı QSS'te `image: url(...)` olarak çözülür ([[tema-sistemi]]).

## 2026-06-12 iyileştirmeleri (P3)
- `get_icon` renklendirmeyi `get_svg_content` üzerinden yapar (tek renklendirme yolu, DRY).
- Render `QSvgRenderer` ile 64×64 şeffaf pixmap'e yapılır (`_render_svg`) — yüksek DPI'da keskin; render başarısızsa renksiz dosya ikonuna düşer.
- `Icons` sabit sınıfı eklendi (`Icons.MENU`, `Icons.CHEVRON_DOWN`...); UI kodunda çıplak ikon string'i yazılmaz.
- `IconManager.try_instance()` public API'si: `theme_manager` artık `_instance` private alanına dokunmuyor; cache SVG dosyası varsa yeniden yazılmıyor (gereksiz disk I/O kalktı).

İlgili: [[mimari-genel-bakis]], [[di-container]]
