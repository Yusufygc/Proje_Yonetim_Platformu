# Wiki Kayıt Defteri

## [2026-07-02] PERF+FIX | Üretim öncesi denetim: lazy sayfa inşası, sessiz not hatası, Worker tutarlılığı
EXE paketlemeden önce başlangıç performansı + mimari/kod kalitesi denetimi yapıldı (3 paralel
keşif ajanı: başlangıç, mimari/kod kalitesi, algoritma/sorgu — algoritma tarafında gerçek sorun
bulunmadı, dokunulmadı). Bulunan ve düzeltilen gerçek sorunlar:
- **[EN BÜYÜK ETKİ] `MainWindow._setup_ui`** artık kayıtlı 9 sayfanın (Dashboard/Projeler/
  Fikirler/Görevler/Notlarım/Analitik/Arşiv/Bilgi/Ayarlar) TAMAMINI `window.show()`'dan önce
  inşa etmiyor — her biri kendi DB sorgusunu (`load_*`) tetikliyordu, kullanıcı aynı anda sadece
  1 sayfa görüyor. `_navigate_to` artık sayfayı yalnızca ilk ziyarette (`_build_and_register_page`)
  kuruyor, `ModuleRegistry.instance().plugins()` üzerinden `page_key` eşleşmesiyle buluyor.
- **[BLOCKER] `NoteController.error_occurred`** hiçbir yere bağlı değildi — not kaydetme/
  güncelleme/silme hatası kullanıcıya tamamen sessizce kayboluyordu. `NoteListWidget`'a
  `ideas_page.py`'deki mevcut desenle (`QMessageBox.critical`) bağlandı; regresyon testi eklendi.
- `project_list_item.py`'deki 2 `except Exception: pass` (sessiz hata yutma, CLAUDE.md ihlali)
  `logger.debug` ile görünür yapıldı.
- `alembic_runner.py::HEAD_REVISION` sabiti eskiydi (`0004`), gerçek head `0007_add_memo_sort_order`
  olarak düzeltildi (migration zinciri: 0001→...→0007).
- `note_service.py` artık plain `ValueError` yerine yeni `core/exceptions/note_exceptions.py`
  (`NoteValidationError`, `NoteNotFoundError`) fırlatıyor — Proje/Görev servisleriyle tutarlı.
- Not/Memo/Dashboard/Analitik controller'larının `load_*` metodları Worker'a taşındı
  ([[worker-altyapisi]]) — artık projenin kendi standardıyla tam tutarlı.

**Bilinçli olarak dokunulmayanlar:** `project_detail_panel.py`(441)/`settings_page.py`(433)/
`info_page.py`(413) satır sınırını hafif aşıyor, `PreferenceManager` 19 public metod (limit 15) —
çalışıyor/test edilmiş, bölünmesi gerçek fayda sağlamadan risk/süre maliyeti taşıyor, kullanıcı
kararıyla sadece not düşüldü. DEBUG log seviyesi, font/tema yükleme maliyeti, `OnboardingService`
tam tablo okuması — negligible.

## [2026-07-02] FEATURE | Yeni görev artık kardeş grubunun başına ekleniyor
`TaskService.create_task`, `order_index` belirtilmediğinde artık
`TaskRepository.first_order_index()` (yeni metod: en küçük `order_index - 1`, grup
boşsa `0`) çağırıyor — önceden `next_order_index()` (en büyük `order_index + 1`,
sona ekler) kullanılıyordu. WBS ağacında yeni görev artık en üstte görünüyor.
DONE'a geçen görevi kardeş grubunun sonuna alan `_apply_status_side_effects`
davranışı (aynı `next_order_index` metodunu kullanır) kasıtlı olarak
DEĞİŞTİRİLMEDİ — iki farklı semantik ("başa ekle" / "sona ekle") artık iki ayrı
repository metoduna ayrıldı, tek bir metodu iki amaç için paylaştırmak yerine.
`tests/test_mvp_core.py`'deki sıra testleri yeni beklenen değerlere (azalan/negatif
`order_index`) güncellendi.

## [2026-07-02] FEATURE | Rose+Violet tema paketleri, liste sıralama animasyonu, font buton grubu
`_THEME_PACKAGES`'e Rose (`#F43F5E`/`#E11D48`) ve Violet (`#8B5CF6`/`#7C3AED`)
eklendi (toplam 6 paket) — `resources/themes/{rose,violet}_{dark,light}.json`
`indigo_*` şablonunun kopyası, sadece accent+sidebar alanları farklı.
Notlar/Fikirler/Projeler/Notlarım listelerindeki sürükle-bırak sıralamaya
yumuşak geçiş eklendi: `DragReorderController._move_row` artık FLIP tekniğiyle
(`_capture_positions`/`_animate_shifted_rows`) konum değiştiren satırları
`QPropertyAnimation(b"pos")` ile 200ms'de kaydırıyor (önceden anlık zıplama
vardı). Native `QListWidget` kullanan Fikirler/Notlarım için önce `setAnimated(True)`
denendi, ama bu özellik PySide6 6.11'de `QListView`'da mevcut değilmiş
(`AttributeError`, üretimde yakalandı) — kaldırılıp yerine bırakma sonrası
taşınan satıra `fade_in_current_item()` ile opacity fade-in (0.4→1.0, 150ms)
eklendi. `DragReorderController._stop_existing_anim` içinde `shiboken6.isValid()`
kontrolü eklendi — `DeleteWhenStopped` politikasıyla doğal biten bir animasyona
tekrar `.stop()` çağrısı `RuntimeError` ile çöküyordu (üretimde yakalandı,
düzeltildi). Yeni `presentation/dimensions.py::Duration` sabiti
(`FAST/REFLOW/SLOW`) sadece yeni kodda kullanılıyor, mevcut animasyon kodu
(sidebar/toast/wbs_tree) dokunulmadı. Ayrıca: Roboto/Open Sans font kaynağı
jsDelivr `@fontsource` woff2'den google/fonts değişken (variable) TTF'lerine
çevrildi — woff2 dosyaları Qt'nin Windows DirectWrite arka ucunda yükleme
hatası veriyordu (`Failed to create DirectWrite face`, üretimde yakalandı).
Ayarlar sayfasında font "Uygula" butonu önizleme kutusuyla sıkı gruplandı
(`preview_group`, `Spacing.SM`).

## [2026-07-02] REFACTOR | Ayarlar sayfası: küratörlü tema paketleri + font boyutu kaldırma
"Ayarlar sayfasının esnekliği kullanışlı mı" tartışması sonucu tema/font sistemi
sadeleştirildi. 24 alanlı manuel `ThemeEditorDialog` + `ColorPickerButton` tamamen
silindi; `ThemeManager`'daki karşılıksız kalan CRUD metodları
(`is_builtin/list_themes/create_theme/update_theme/delete_theme/duplicate_theme/
export_theme/import_theme/get_palette_copy/preview_palette/restore_preview`)
kaldırıldı. "Hızlı Vurgu" gizli kopya mekanizması (`{isim}_vurgu_kopya` üreten
`_on_accent_quick_change`) kaldırıldı — bu, `light_vurgu_kopya`/`dark_vurgu_kopya`
karmaşasının kök nedeniydi. Yerine 4 küratörlü paket geldi: Slate/Indigo/Emerald/
Ocean × Koyu/Açık = 8 sabit builtin tema dosyası
(`resources/themes/{indigo,emerald,ocean}_{dark,light}.json`, yeni). Ölü/parçalı
dosyalar (`old_dark.json`, `old_light.json`, `yedek_light.json`,
`user/dark_vurgu_kopya.json`, `user/light_vurgu_kopya.json`) silindi;
`app/di_container.py`'deki tek seferlik `_migrate_legacy_theme_slots()` mevcut
kullanıcıların tercihlerini yeni paketlere sessizce taşıyor. Font boyutu ayarı
(fiilen ölüydü — 56+ QSS dosyasında sabit `font-size` px kuralı zaten
`QApplication.setFont()` boyutunu eziyordu) tamamen kaldırıldı; kullanıcı sadece
5 küratörlü aileden (Plus Jakarta Sans, Inter, Roboto, Open Sans, Segoe UI) seçim
yapıyor. Detay: [[tema-sistemi]].

## [2026-07-02] REFACTOR | Analitik KPI sadeleştirme ve görev tamamlanınca sıralama düzeltmesi
`AnalyticsService`'teki kullanılmayan tahmini/harcanan süre toplamları (`_time_total`,
`estimated_minutes_total`/`spent_minutes_total`) ve `analytics_page.py`'deki karşılık gelen
bant + `_fmt_minutes` yardımcı fonksiyonu kaldırıldı. `TaskService`: bir görev DONE
durumuna geçtiğinde `order_index`'i kardeş grubunun sonuna taşınıyor (WBS listesinde en
alta iner) — 2026-07-01'deki "Hızlı Görev Ekle" düzeltmesinin tamamlama akışına
genişletilmiş hali. `CLAUDE.md`'ye değişiklik sonrası `pytest` çalıştırma zorunluluğu
kural olarak eklendi.

## [2026-07-02] FIX + UX | Aşama tamamlama titremesi, rozet sadeleştirme, analitik tema senkronu
`ProjectsPage._on_stage_updated` bir aşama tamamlandığında tüm proje listesini ve detay
panelinin dört alt sekmesini (Görevler/Kararlar/Notlar/Kaynaklar) gereksiz yere yeniden
yüklüyordu — tıklamada tüm sayfa yenileniyormuş gibi titremeye yol açıyordu. Artık sadece
ilgili proje çekilip `ProjectListItem.update_project()` / `ProjectDetailPanel.refresh_header()`
ile yerinde güncelleniyor. Süreç aşamaları listesindeki ayrı durum rozeti (Tamamlandı/
Aktif/Bekliyor metni) kaldırıldı; tik ikonu + renkli nokta + glow zaten yeterli sinyal
veriyordu. Proje durum/öncelik rozetlerindeki dolgulu arka planlar kaldırıldı: durum artık
tek renkli nokta (`#status_dot`), öncelik kart çerçevesi rengiyle taşınıyor
(`card-priority`); erişilebilirlik için ikisi de tooltip'te metin olarak kalıyor. Proje
detay sekme çubuğunun seçili rengi "+ Ana Görev Ekle" ile aynı accent gradyana çekildi,
süreç aşamaları ile sekme çubuğu arasına ayraç çizgi eklendi. Analitik grafiklerinin arka
planı artık Qt'nin sabit koyu/açık temasına değil uygulamanın gerçek tema paletine bağlı
(dark modda beyaz kalma sorunu giderildi); grafik yükseklikleri ve panel boşlukları
daraltılarak sayfa scrollbar ihtiyacı azaltıldı; dönem butonlarının tanımsız `btn-toggle`
sınıfına stil eklendi. Detay: [[tema-sistemi]].

## [2026-07-02] FEATURE | Süreç aşamalarında tamamlanan aşamaya tik ikonu, aktif aşamaya glow
`StageTimelineWidget`: DONE durumundaki aşamalar artık daire yerine tik (checkmark) ikonu
gösteriyor (`IconManager.get_icon`, `try_instance()` ile headless/test ortamında güvenli
daireye düşüş); ACTIVE aşama kartına `stage_active` renginde accent glow
(`QGraphicsDropShadowEffect`) eklendi. `presentation/utils/ui_utils.apply_shadow`'a
opsiyonel `color` parametresi eklendi (varsayılan siyah gölge davranışı korunur).

## [2026-07-02] STYLE | Flat tasarım geçişi: renk paleti, rozetler, sidebar, buton/combobox durumları
Light temadaki bej/krem tonlar (`background`, `border`, `scrollbar_bg`, `sidebar_active`,
`h-sidebar_bg`) nötr gri palete çevrildi (kullanıcının aktif özel teması
`light_vurgu_kopya.json`'a da aynı düzeltme uygulandı). Kritik rozetler (Yüksek/Kritik
öncelik, Engellendi/İptal/Reddedildi durum) soluk alfa zeminden solid renk + beyaz metne
geçti. Sidebar aktif sekme sert çok duraklı gradyandan düz zemin + sol vurgu çubuğuna
geçti. `QComboBox`'a açık/kapalı/disabled/dropdown-item hover durumları, butonlara
`:pressed` durumu eklendi. Proje sekme çubuğundaki kutu modeli asimetrisi (checked/
unchecked arası border kalınlık farkı, dikey hizalama hatasına yol açıyordu) giderildi.
`section-header` tipografisi büyütüldü/koyulaştırıldı. WBS tablo başlığı font boyutu
artırıldı. Detay: [[tema-sistemi]].

## [2026-07-01] FIX | Notlarım (memo) sayfasında sürükle-sırala eksikti
Kullanıcı "Notlarım sayfasında sıralama çalışmıyor" diye bildirdi; incelemede
`MemoPage`'in hiç sıralama mekanizması olmadığı görüldü (önceki liste-sıralama
işi yalnızca Notlar/Fikirler/Projeler'i kapsamıştı). `Memo.sort_order` kolonu
eklendi (migration `007_add_memo_sort_order`, `updated_at` sırasına göre
backfill), `MemoRepository`/`MemoService`/`MemoController.reorder` zinciri ve
`MemoPage`'te `QListWidget.setDragDropMode(InternalMove)` + `model().rowsMoved`
(Fikirler ile aynı desen) eklendi. Detay: [[liste-siralama]].

## [2026-07-01] FEATURE + FIX | Liste sıralama, soluk proje kartı, hızlı ekle sıra düzeltmesi
Notlar/Fikirler/Projeler listelerinde sürükle-bırak sıralama: `Note`/`Idea` modellerine
`sort_order` kolonu (migration `006_add_list_sort_order`, backfill dahil), `Project`
zaten sahip olduğu `display_order`'ı kullanıyor. UI: manuel `QVBoxLayout` listeleri
(Notlar, Projeler) için yeniden kullanılabilir `DragReorderController`
(`presentation/widgets/drag_reorder.py`); Fikirler zaten `QListWidget` olduğundan
`InternalMove` moduyla çözüldü. Detay: [[liste-siralama]]. Ayrıca: Projeler sayfası kart
görünümü artık soluk dolgu zeminli (`project_list_item.qss`) — kartlar birbirinden
görsel olarak ayrışıyor. Bugfix: "Hızlı Görev Ekle" ile eklenen görev artık her zaman
kardeş grubunun sonuna ekleniyor (`TaskRepository.next_order_index`,
`TaskService.create_task` artık `order_index`'i hiç boş bırakmıyor); önceden hesaplanmadığı
için varsayılan `0` kalıp listenin başına/ortasına düşüyordu.

## [2026-06-30] FEATURE | Sesli komut (speech-to-text)
Vosk çevrimdışı motoru ile mikrofon dikteleme: `SpeechToTextService` (lazy model yükleme) →
`TranscriptionWorker` (`QThreadPool`, [[worker-altyapisi]] deseni, sürekli döngü + `stop()`) →
`VoiceInputButton`/`attach_voice_button` (`QLineEdit` + `QTextEdit` ortak destek). Görev/fikir
başlığı, hızlı görev ekle ve tüm uzun açıklama/not alanlarına 🎤 eklendi. Model
(`vosk-model-small-tr-0.3`, ~35 MB) `resources/models/` altında, repoya dahil değil. Hata
yolları (`SpeechModelNotFoundError`, `MicrophoneUnavailableError`) toast'a bağlandı, UI
bloklanmıyor. Detay: [[sesli-komut]].

## [2026-06-13] UX | Palet geçişi sonrası kontrast ve hiyerarşi onarımı
Sidebar yeni token seti (`sidebar_text`, `sidebar_text_active`, `sidebar_hover_bg`, `sidebar_active_bg`); aktif öğe 3px sol kenar + opak metin desenine geçti (alpha blend kaldırıldı). Koyu temada `text_secondary` lavanta, `border` ayrı ton, `stage_done` success yeşili. Stat kart KPI değeri primary + büyük punto. Stage row 36px sabit (`Size.STAGE_ROW_H`). Tab stili browser-tab desenine geçti. Stage butonları StringManager'a taşındı. Detay: [[tema-sistemi]], `Project_docs/UX_TEMA_GERI_BILDIRIMI_2026-06-13.md`.

## [2026-06-13] REFACTOR | Constructor injection UI'da tamamlandı
9 widget/sayfa + `Sidebar` + `Toast` + `SettingsPage` artık `theme/icons/strings/prefs/event_bus`'ı constructor parametresinden alıyor; modules.py factory'leri DI'den besler. `DIContainer`'a `strings` ve `icons` public property'leri eklendi. Sadece `MainWindow` (kompozisyon kökü) `getattr(di) or instance()` fallback'i tutuyor. Detay: [[di-container]], [[yol-haritasi]].

## [2026-06-13] FEATURE | Dil seçici ve İngilizce çeviri
`strings.en.json` (249 anahtar) + ayarlar sayfasında dil combobox'ı + `PreferenceManager.save/load_language` + bootstrap'te kalıcı dil uygulama. Locale parite testi eklendi (anahtar + placeholder eşleşmesi). Karar: canlı retranslate yerine yeniden başlatma. Detay: [[l10n-string-yonetimi]].

## [2026-06-13] UPDATE | L10N migrasyonu TAMAMLANDI
Kalan 16 dosya (3 küçük dialog, 4 liste widget'ı, dashboard/ideas/projects/info sayfaları, search, stage_timeline, project_list_item, main_window, modules) StringManager'a taşındı. Ratchet ALLOWLIST boşaldı; `strings.tr.json` 247 anahtar. SearchDialog sinyali dilden bağımsız tip koduna geçti; idea_dialog'daki sözlük→fonksiyon dönüşümünün ideas_page'de kırdığı import onarıldı. `# l10n: log` pragma'sı eklendi. Detay: [[l10n-string-yonetimi]].

## [2026-06-12] UPDATE | L10N migrasyonu 2. dalga
`project_detail_panel`, `idea_dialog`, `task_dialog`, `settings_page` StringManager'a taşındı; dialoglar `form_utils` (make_combo_column, select_combo_data, set_field_error) kullanacak şekilde sadeleştirildi. Ratchet allowlist 21→17. Detay: [[l10n-string-yonetimi]].

## [2026-06-12] UPDATE | P3 tamamlandı
DIContainer üç registry'ye bölündü (`di_registries.py`, `__getattr__` ile geriye dönük uyum); IconManager `QSvgRenderer` + `Icons` sabitleri + `try_instance()` aldı; `commit_all.py`/`download_assets.py` `scripts/` altına taşındı. Detay: [[di-container]], [[ikon-yonetimi]], [[yol-haritasi]].

## [2026-06-12] INGEST | Wiki bilgi tabanı kuruldu
İlk 11 sayfa oluşturuldu: mimari, DI, EventBus, worker, veritabanı, tema, L10N, ikon, görevler modülü, kurallar, yol haritası. Kaynak: senior analiz raporu (`Project_docs/SENIOR_ANALIZ_RAPORU_2026-06-12.md`) + P0-P2 refactor oturumu.

## [2026-06-12] UPDATE | P2 tamamlandı
`BaseRepository[T]` ile 12 repo sadeleştirildi; StringManager'a `language_changed` sinyali eklendi; L10N ratchet testi (`tests/test_l10n_no_hardcoded.py`) yazıldı; `project_dialog` string migrasyonu yapıldı. Detay: [[veritabani-katmani]], [[l10n-string-yonetimi]].

## [2026-06-12] UPDATE | P0-P1 tamamlandı
EventBus WeakMethod'a geçirildi ([[event-bus]]); `tasks_page` pakete bölündü ([[gorevler-modulu]]); monolitik `base.qss` 8 modüle ayrıldı ([[tema-sistemi]]); tema sözleşmesi bağlantıları eklendi.

## [2026-06-12] DECISION | Graphify zorunluluğu kaldırıldı
CLAUDE.md §3 silindi (kullanıcı kararı). Mimari dokümantasyon artık bu wiki üzerinde tutuluyor.

## [2026-06-12] DECISION | Yazma işlemleri senkron kalacak
SQLite WAL'de yazmalar ms seviyesinde; Worker'a taşımanın sinyal sıralaması riski kazancı aşıyor. Detay: [[worker-altyapisi]].
