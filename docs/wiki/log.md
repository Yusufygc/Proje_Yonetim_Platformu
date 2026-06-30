# Wiki Kayıt Defteri

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
