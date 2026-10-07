# İkon Yönetimi

## IconManager (`core/managers/icon_manager.py`)
- Singleton; `resources/icons/*.svg` okur.
- `get_icon(name, color)` — SVG içinde `fill/stroke="currentColor"` → verilen hex; `QPixmap.loadFromData` ile QIcon üretir; `name_color` anahtarıyla cache'ler.
- `get_svg_content(name, color)` — renklendirilmiş ham SVG metni.

## QML entegrasyonu
`presentation/viewmodels/icon_provider.py::IconImageProvider` (`image://icons/<ad>?color=<hex>`) ikonları `IconManager` üzerinden renklendirip QML `AppIcon` bileşenine sunar ([[tema-sistemi]]).

## 2026-06-12 iyileştirmeleri (P3)
- `get_icon` renklendirmeyi `get_svg_content` üzerinden yapar (tek renklendirme yolu, DRY).
- Render `QSvgRenderer` ile 64×64 şeffaf pixmap'e yapılır (`_render_svg`) — yüksek DPI'da keskin; render başarısızsa renksiz dosya ikonuna düşer.
- `Icons` sabit sınıfı eklendi (`Icons.MENU`, `Icons.CHEVRON_DOWN`...); UI kodunda çıplak ikon string'i yazılmaz.
- `IconManager.try_instance()` public API'si: bootstrap edilmemiş ortamda `None` döner.

İlgili: [[mimari-genel-bakis]], [[di-container]]
