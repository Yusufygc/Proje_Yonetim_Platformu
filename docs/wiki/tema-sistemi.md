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

## Flat tasarım geçişi ve dolgusuz rozet dili (2026-07-02)
Light temadaki bej/krem tonlar (`background`, `border`, `scrollbar_bg`, `sidebar_active`,
`h-sidebar_bg`) nötr gri/slate palete çevrildi; `resources/themes/user/` altındaki
kullanıcı temaları (örn. `light_vurgu_kopya.json`) da **aktif temaysa** aynı düzeltme
elle uygulanmalı — `ThemeManager` bunları otomatik senkronlamaz, her biri bağımsız JSON.

Rozet dili değişti — artık iki farklı sinyal kanalı var:
- **Durum**: dolgulu etiket yerine tek renkli nokta (`QFrame#status_dot`,
  `resources/styles/widgets/badges.qss`). Aynı aileden durumlar (Aktif/Tamamlandı ikisi de
  eskiden `success` yeşiliydi) artık ayrık renklerle ayrışır. Kullanım noktaları:
  `ProjectListItem` (satır sonu), `ProjectDetailPanel` (başlık altı).
- **Öncelik**: `ProjectListItem` çerçevesinin `card-priority` property'sine kodlanır
  (`resources/styles/widgets/project_list_item.qss`) — Düşük/Orta nötr, Yüksek turuncu,
  Kritik kırmızı kenarlık. Seçim durumu (`selected="true"`) öncelik kenarlığını ezer (QSS
  sırası: öncelik kuralları önce, `[selected="true"]` sonra tanımlı).
- Metin kalktığı için **erişilebilirlik**: her iki bilgi de `setToolTip()` ile korunur.
- İstisna — proje detay panelindeki `proj-status`/`proj-priority` rozetleri (tek kayıt,
  yer bol) hâlâ dolgusuz ama **metinli** kalıyor: `color: @renk;` (arka plan yok).
- Kritik/tehlike anlamlı **diğer** rozetler (idea-status REJECTED, task-priority HIGH/
  CRITICAL, inline-status BLOCKED/CANCELLED) solid arka plan + `@icon_on_accent` (beyaz)
  metin kullanır — nötr değerler (LOW/MEDIUM/PLANNED/ACTIVE/TODO) soft pill'de kalır. Bu
  ayrım bilinçli: "nötr = soft pill, kritik = solid alert chip".

Diğer flat-tasarım değişiklikleri: `QComboBox`'a `:on`/`:disabled`/`::drop-down:hover`/
`QAbstractItemView::item:hover,:selected` eklendi; `QPushButton`/`btn-primary`/
`btn-secondary`'ye `:pressed` durumu eklendi (`@accent_end`'e geçiş, yeni token yok);
`ProjectTabButton` (proje detay sekme çubuğu, sidebar'dan **ayrı** bileşen) checked
durumunda artık CTA butonlarıyla (`btn-primary`) aynı accent gradyanı kullanıyor — kutu
modeli asimetrisi (`border` kalınlığı checked/unchecked arası farklıydı) da giderildi,
her durumda `border: 2px solid transparent` sabit.

## Süreç aşamaları (StageTimelineWidget) — tik/glow ve analitik grafik tema senkronu (2026-07-02)
`presentation/widgets/stage_timeline_widget.py`: DONE durumundaki aşama artık
`QFrame#stage_dot` yerine `IconManager.get_icon(Icons.SQUARE_CHECK, ...)` ile tik ikonu
gösterir (`IconManager.try_instance()` None dönerse — bootstrap edilmemiş/headless ortam —
daireye düşülür, testler kırılmaz). ACTIVE karta `stage_active` renginde
`apply_shadow(..., color=QColor(...))` ile glow uygulanır; bunun için
`presentation/utils/ui_utils.apply_shadow`'a opsiyonel `color` parametresi eklendi
(verilmezse eski siyah gölge davranışı korunur). Ayrı metin durum rozeti (`stage_badge`)
tamamen kaldırıldı — tik + nokta + sol kenarlık + glow zaten yeterli. `update_stages()`
artık `setUpdatesEnabled(False/True)` ile sarmalı (rebuild flicker azaltma).

`AnalyticsChartWidget` (QtCharts, matplotlib **değil**) `apply_theme(dark, surface_color,
text_color)` imzasına geçti: `QChart.setTheme()` (Qt'nin sabit koyu/açık paleti) tek
başına yeterli değildi, dark modda grafik arka planı beyaz kalıyordu — artık
`setBackgroundBrush`/`setBackgroundPen`/`setTitleBrush`/eksen `setLabelsColor` gerçek
`ThemeManager` token'larıyla (`surface`, `text_primary`) senkronlanıyor. Bar/pasta veri
renkleri (`_PRIORITY_COLORS`, `_PIE_PALETTE`) bilinçli olarak tema-bağımsız kalıyor.

## Tema Sözleşmesi (programatik renk)
QSS ile verilemeyen renkler (`setForeground` vb.) `ThemeManager.color(key)` ile çözülür ve **o widget `theme_changed`'e abone olmak zorundadır**. Uygulayanlar: `pages/tasks` (ağaç), `dashboard_page`, `resource_list_widget`, `sidebar`, `stage_timeline_widget`, `info_page`, `analytics_page`/`analytics_chart_widget` (QtCharts arka plan/eksen renkleri). `skeleton_loader` her `showEvent`'te çözdüğü için muaf.

## cssClass utility sistemi
`widget.setProperty("cssClass", "title-medium")` → `base/70_css_classes.qss` eşleşir. Mevcut sınıflar: text-*, title-*, section-header, field-label, panel(-raised), divider, btn-primary/secondary/danger, btn-toggle, chk-*, transparent-bg.

## Küratörlü tema paketleri ve ayarlar sayfası sadeleştirmesi (2026-07-02)
Ayarlar sayfasındaki "esneklik ne kadar kullanışlı" tartışması sonucu tema sistemi
kökten sadeleştirildi. Kaldırılanlar:
- **24 alanlı manuel `ThemeEditorDialog`** (+ `ColorPickerButton` widget'ı) — dosyalar
  tamamen silindi. `ThemeManager`'daki karşılık gelen CRUD metodları
  (`is_builtin/list_themes/create_theme/update_theme/delete_theme/duplicate_theme/
  export_theme/import_theme/get_palette_copy/preview_palette/restore_preview`) da
  silindi — grep ile doğrulanan tek çağıranları bu dialog + ayarlar sayfasıydı.
- **"Hızlı Vurgu" gizli kopya mekanizması** (`SettingsPage._on_accent_quick_change`) —
  built-in bir temadayken accent chip'ine tıklamak sessizce `{isim}_vurgu_kopya`
  adlı yeni bir `user/` teması oluşturup slotu ona çeviriyordu. Bu, `light_vurgu_kopya`/
  `dark_vurgu_kopya` karmaşasının kök nedeniydi.
- Ölü/parçalı tema dosyaları: `old_dark.json`/`old_light.json` (kod tarafından
  erişilemeyen orphan dosyalar), `yedek_light.json` (light.json'ın bej kopyası).

Yerine gelen: **4 küratörlü paket** (Slate/Indigo/Emerald/Ocean) × 2 mod (Koyu/Açık) =
8 sabit builtin tema dosyası. Her paket ilgili nötr temanın (`dark.json`/`light.json`)
birebir kopyası olup sadece `accent_start/accent_end` (+ dark'ta `sidebar_active`,
light'ta `sidebar_bg/sidebar_active_bg/sidebar_hover_bg`) değişir — nötr renkler,
`stage_active/stage_done`, `success/warning/danger` tüm paketlerde aynı kalır
(bilinçli tercih: tema dosyaları arasında inheritance yok, her biri bağımsız flat
JSON; küçük bir kod tekrarı, yeni bir "base+override" mekanizması icat etmekten
daha az riskli).

`presentation/pages/settings_page.py` içindeki `_THEME_PACKAGES` sabiti
`(id, i18n_key, default_label, dark_stem, light_stem, swatch_hex)` tuple listesi —
paket kartına tıklamak `PreferenceManager.save_dark_slot/save_light_slot` +
`ThemeManager.switch_theme`'i doğrudan çağırır (eski `_on_slot_changed` ile aynı
mekanizma), hiçbir dosya oluşturmaz.

**Geçiş (migration):** `app/di_container.py` içindeki `_migrate_legacy_theme_slots()`
bootstrap'ta bir kerelik çalışır; `dark_vurgu_kopya`/`light_vurgu_kopya`/`old_dark`/
`old_light`/`yedek_light` tercihlerini yeni paket stem'lerine sessizce çevirir
(`_LEGACY_THEME_MAP`). Bu sayede önceden `light_vurgu_kopya` aktif olan bir kurulum
otomatik olarak Slate'e döner, kullanıcı hiçbir şey yapmaz.

## Font boyutu kaldırıldı (2026-07-02)
Font boyutu ayarı fiilen ölüydü: 56+ QSS dosyasında sabit `font-size: Npx` kuralı
`QApplication.setFont()` boyutunu her zaman eziyordu — kullanıcı boyutu değiştirse
de arayüzün büyük kısmı değişmiyordu. Çözüm mimariyi düzeltmek değil, kırık kontrolü
kaldırmak: `presentation/dimensions.py` → `FontFamily.DEFAULT_SIZE = 10` (tek
doğruluk kaynağı), `PreferenceManager.save_font_size/load_font_size` silindi.
Kullanıcı artık sadece font AİLESİ seçiyor — liste de `QFontDatabase.families()`
(tüm sistem fontları, Wingdings dahil) yerine 5 küratörlü isme indirildi: Plus
Jakarta Sans, Inter, Roboto, Open Sans, Segoe UI. `core/managers/font_manager.py`
artık kendi özel `_UI_FAMILY`/`_MONO_FAMILY` sabitlerini değil
`presentation.dimensions.FontFamily`'yi kullanıyor (önceden iki ayrı yerde
duplicate tanımlıydı). Roboto/Open Sans `scripts/download_fonts.py`'ye jsDelivr
`@fontsource` CDN üzerinden (woff2, versiyonlu/stabil) eklendi;
`FontManager.load_all()` artık `*.woff2` da glob'luyor.

## Bilinen sınırlar
- `services/stage_service.py` DEFAULT_STAGES renkleri DB'ye yazılan seed verisi — tema dışı, bilinçli ([[veritabani-katmani]]).
- Boyut/spacing QSS'te değil `presentation/dimensions.py` sabitlerinde (Spacing, Size, Shadow).

İlgili: [[ikon-yonetimi]], [[kurallar-ve-sozlesmeler]]
