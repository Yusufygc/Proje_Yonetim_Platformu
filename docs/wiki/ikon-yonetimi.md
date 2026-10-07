# İkon Yönetimi

## IconManager (`core/managers/icon_manager.py`)
- Singleton; `resources/icons/*.svg` dosyalarını okur.
- `get_svg_content(name, color)` — SVG içinde `fill/stroke="currentColor"` değerlerini verilen hex ile değiştirip ham SVG metnini döndürür; dosya yoksa boş string ve uyarı logu.

## QML entegrasyonu
`presentation/viewmodels/icon_provider.py::IconImageProvider` (`image://icons/<ad>?color=<hex>`) ikonları `IconManager` üzerinden renklendirip QML `AppIcon` bileşenine sunar. Küçük ikonlar (`plus`, `x`, `eye` vb.) sağlayıcı içinde gömülü SVG olarak tanımlıdır; `edit`, `trash-2`, `home` gibi takma adlar `_ICON_ALIASES` ile dosya adlarına çevrilir ([[tema-sistemi]]).

Yeni ikon eklemek: `resources/icons/<ad>.svg` dosyası ekle (tek renkli, `currentColor` kullanan çizgi/dolgu). Eksik ikon QML'de görünmez ve log'a `İkon bulunamadı` uyarısı düşer.

## Emoji yerine SVG ikon
Arayüzde emoji kullanılmaz; ikon gereken yerde `AppIcon`/`AppButton.iconName` ve `resources/icons/*.svg` kullanılır (emoji temayla boyanamaz, platforma göre farklı görünür). Çizim araç çubukları için çizgi ikonlar eklendi: `pencil`, `minus`, `arrow-right`, `square`, `square-fill`, `square-round`, `circle`, `eraser`, `capsule`, `diamond`, `parallelogram`, `workflow`, `clipboard`, `undo`, `redo`, `image`; ayrıca `check`, `triangle-alert`, `paperclip`, `upload`, `circle-check`, `circle-x`. Yerelleştirme metinlerine emoji yazılmaz (ikon QML tarafında verilir).
Açılır liste ve ağaç okları `chevron-down/up/right`, alt görev işareti `corner-down-right`, Enter ipucu `corner-down-left` ikonlarıdır. İkon rengi her zaman bildirimli `themeBridge` özelliğinden verilir (`color: themeBridge.textMuted`); sabit renk kodu yazılırsa tema değişince ikon eski renkte kalır. Sağlayıcı önbelleği renk kodunu anahtara kattığı için yeni renk yeniden boyanır. `tests/test_theme_palette.py` QML'de emoji ve sembol karakterleri taramasıyla bunu korur (düz yazıdaki `→` serbest).
Tema geçiş düğmeleri `moon`/`sun` ikonlarını kullanır (Ayarlar'da "Koyu"/"Açık" yazısıyla, daraltılmış kenar çubuğunda yalnızca ikon).

## Geçmiş
- 2026-10-07: Eski Widgets arayüzünün `get_icon` (QIcon üretimi), `Icons` sabit sınıfı, `try_instance()` ve QSS ok ikonu üretimi kaldırıldı; yalnızca QML'in kullandığı `get_svg_content` kaldı. `chevron-right.svg` eklendi (aşama kartı).

İlgili: [[mimari-genel-bakis]], [[di-container]]
