# Tema Sistemi

## Mekanizma
1. Palet: `resources/themes/dark.json` / `light.json` (27 anahtar: background, surface, accent_*, *_alpha, stage_*...).
2. QSS dosyaları `@token_name` yer tutucuları kullanır; `ThemeManager.build_global_qss()` tüm `.qss` dosyalarını **alfabetik** (`rglob` sıralı) okuyup token'ları aktif paletle değiştirir.
3. `main_window` global QSS'i uygular; `theme_changed` sinyalinde yeniden uygular.
4. Tema kalıcılığı: bootstrap'te `prefs.load_theme()` → `switch_theme` ([[di-container]]).

## Modüler QSS yapısı (2026-06-12'de bölündü)
```
resources/styles/
  base/00_reset → 10_buttons → 20_inputs → 30_views → 40_scrollbar
       → 50_menu → 60_calendar → 70_css_classes   (sayısal önek = yükleme sırası)
  components/  sidebar.qss, toast.qss
  dialogs/     base_dialog.qss, search_dialog.qss
  pages/       base_page.qss, info_browser.css (QSS değil; resolve_tokens ile)
  widgets/     badges, stage_timeline, task_list, project_list_item
  _cache/      tema renkli SVG ok ikonları (üretilen, commit edilmez mantığında)
```
Kural: yeni stil ilgili modül dosyasına yazılır; Python içinde `setStyleSheet` YASAK (tek istisna: main_window global uygulaması). Renk daima `@token`.

## Sidebar token ailesi (2026-06-13)
Sidebar arka planı genel paletten **bağımsız** olduğu için ayrı token seti vardır:
- `sidebar_bg` — sidebar zemini (koyu tonda her temada).
- `sidebar_text` — pasif nav metni (zemin üstünde WCAG AA geçer).
- `sidebar_text_active` — aktif/hover nav metni.
- `sidebar_active` — aktif öğenin 3px sol kenar rengi.
- `sidebar_hover_bg`, `sidebar_active_bg` — alpha tonları (gerekirse).

Aktif vurgu deseni: **transparent bg + 3px sol border + opak metin rengi**. Alpha karışım Qt'de koyu zemin altında kırmızımsı tonlar üretiyordu; bu desen sorunu tamamen kaldırır.

Genel kural: sidebar dışında `text_secondary` kullan, sidebar **içinde** `sidebar_text` kullan. QSS'te `QFrame#sidebar QLabel` seçicisi sidebar etiketlerini otomatik bu token'a bağlar.

## Tema Sözleşmesi (programatik renk)
QSS ile verilemeyen renkler (`setForeground` vb.) `ThemeManager.color(key)` ile çözülür ve **o widget `theme_changed`'e abone olmak zorundadır**. Uygulayanlar: `pages/tasks` (ağaç), `dashboard_page`, `resource_list_widget`, `sidebar`, `stage_timeline_widget`, `info_page`. `skeleton_loader` her `showEvent`'te çözdüğü için muaf.

## cssClass utility sistemi
`widget.setProperty("cssClass", "title-medium")` → `base/70_css_classes.qss` eşleşir. Mevcut sınıflar: text-*, title-*, section-header, field-label, panel(-raised), divider, btn-primary/secondary/danger, chk-*, transparent-bg.

## Bilinen sınırlar
- `services/stage_service.py` DEFAULT_STAGES renkleri DB'ye yazılan seed verisi — tema dışı, bilinçli ([[veritabani-katmani]]).
- Boyut/spacing QSS'te değil `presentation/dimensions.py` sabitlerinde (Spacing, Size, Shadow).

İlgili: [[ikon-yonetimi]], [[kurallar-ve-sozlesmeler]]
