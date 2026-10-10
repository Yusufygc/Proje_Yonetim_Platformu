# Tema Sistemi

Arayüz yalnızca QML'dir; eski Qt Widgets arayüzü ve QSS altyapısı kaldırıldı (bkz. [[log]], 2026-10-07).

## Mekanizma
1. Palet: `resources/themes/*.json` (27+ anahtar: background, surface, accent_*, *_alpha, stage_*, sidebar_* ...). `ThemeManager(themes_dir)` aktif paleti yükler; eksik alpha ve türetilmiş token'lar `derive_alpha_tokens` ile üretilir.
2. `ThemeBridge` (`presentation/viewmodels/theme_bridge.py`) paleti QML'e açar: `themeBridge.surface`, `accentStart`, `textPrimary`, `border` gibi bildirimli property'ler. Tema değişince `theme_changed` sinyali bu property'leri kullanan QML bağlamalarını yeniler.
3. QML tarafında renk **asla sabit yazılmaz**; `themeBridge` veya `Theme.qml` yardımcıları kullanılır.
4. Tema kalıcılığı: bootstrap'te `prefs.load_theme()` → `switch_theme` ([[di-container]]).

## Sidebar token ailesi
Sidebar arka planı genel paletten **bağımsız** olduğu için ayrı token seti vardır:
- `sidebar_bg` — sidebar zemini (koyu tonda her temada).
- `sidebar_text` — pasif nav metni (zemin üstünde WCAG AA geçer).
- `sidebar_text_active` — aktif/hover nav metni.
- `sidebar_active` — aktif öğenin sol kenar rengi.
- `sidebar_hover_bg`, `sidebar_active_bg` — alpha tonları.

Aktif vurgu deseni: **transparent bg + sol border + opak metin rengi**. Alpha karışım koyu zemin altında kırmızımsı tonlar üretiyordu; bu desen sorunu kaldırır. Kural: sidebar dışında `text_secondary`, sidebar **içinde** `sidebar_text`.

### Desenli kenar çubuğu paketleri (Rose ve Ocean)
Rose (`rose_dark`, `rose_light`) ve Ocean (`ocean_dark`, `ocean_light`) tema paketleri seçildiğinde, `Sidebar.qml` kenar çubuğuna özel damask desenli arka plan görselleri dinamik olarak uygulanır:
- **Rose Teması:** `resources/images/rose_sidebar.jpg` damask gül deseni + koyu şarap/bordo karartma overlay'i + `#FFF0F3` yüksek kontrastlı metin rengi.
- **Ocean Teması:** `resources/images/ocean_sidebar.jpg` okyanus mavisi damask çiçek deseni + derin lacivert karartma overlay'i + `#F0F9FF` yüksek kontrastlı buz beyazı metin rengi.
- Sayfa navigasyon butonları (`navItem`) hafif yarı saydam koyu kapsül zemin (`Qt.rgba(0, 0, 0, 0.22)`) ve ince çerçeveyle render edilerek desen üzerinde kusursuz okunabilirlik sağlanır.

## Küratörlü tema paketleri
6 paket (Slate/Indigo/Emerald/Ocean/Rose/Violet) × 2 mod (Koyu/Açık) = 12 sabit builtin tema dosyası. Her paket nötr temanın (`dark.json`/`light.json`) birebir kopyası olup yalnızca `accent_start/accent_end` (+ sidebar alanları) değişir. Bilinçli tercih: dosyalar arası inheritance yok, her biri bağımsız flat JSON (küçük tekrar, "base+override" mekanizmasından daha az riskli). Renkler `success/warning/danger/stage_active/stage_done` ile çakışmayacak şekilde seçildi.

`presentation/viewmodels/settings_viewmodel.py` içindeki `_THEME_PACKAGES` listesi `(id, name, color, dark_stem, light_stem)` sözlükleridir; paket seçimi `PreferenceManager.save_dark_slot/save_light_slot` + `ThemeManager.switch_theme` çağırır, dosya oluşturmaz.

**Geçiş (migration):** `app/di_container.py::_migrate_legacy_theme_slots()` bootstrap'ta çalışır; eski `dark_vurgu_kopya`/`light_vurgu_kopya`/`old_dark`/`old_light`/`yedek_light` tercihlerini yeni paket stem'lerine çevirir (`_LEGACY_THEME_MAP`). Kullanıcı temaları `resources/themes/user/` altında aranır ve otomatik senkronlanmaz.

## QML'de renk kullanımı: iki tuzak
- **`themeBridge.color("key")` kullanılmaz.** Slot çağrısıdır; QML bağlaması tema değişimini izleyemez. Açık temadan koyu temaya geçince bu çağrıyla boyanan alanlar eski renkte kalır (beyaz zemin, koyu yazı, okunmayan başlık). Bildirimli property kullanılır (`themeBridge.textPrimary` vb.); testi `tests/test_theme_palette.py` içindedir.
- **Alfa sırası:** Palet CSS sırasıyla (`#RRGGBBAA`) yazılır; Qt `#AARRGGBB` okur. `ThemeManager.color()` çıkışta çevirir (`to_qt_color`). Çevrilmeseydi `hover_overlay` (`#FFFFFF0D`) opak sarı görünürdü.

## Font
Font **boyutu** ayarı kaldırıldı: `presentation/dimensions.py::FontFamily.DEFAULT_SIZE = 10` tek doğruluk kaynağı. Kullanıcı yalnızca aileyi seçer; liste 5 küratörlü isimdir (Plus Jakarta Sans, Inter, Roboto, Open Sans, Segoe UI). `FontManager` aile sabitlerini `FontFamily`'den okur. Roboto/Open Sans `scripts/download_fonts.py` ile google/fonts deposundaki tek dosyalık **değişken TTF**'lerden indirilir (woff2 dosyaları Qt'nin Windows DirectWrite arka ucunda reddedildi).

## Bilinen sınırlar
- `services/stage_service.py` DEFAULT_STAGES renkleri DB'ye yazılan seed verisi — tema dışı, bilinçli ([[veritabani-katmani]]).
- Grafik veri renkleri (analitik öncelik/pasta paleti) bilinçli olarak tema-bağımsızdır.

İlgili: [[ikon-yonetimi]], [[kurallar-ve-sozlesmeler]]
