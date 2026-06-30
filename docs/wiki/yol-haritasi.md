# Yol Haritası

Kaynak analiz: `Project_docs/SENIOR_ANALIZ_RAPORU_2026-06-12.md` (durum tablosu §9).

## Tamamlandı (2026-06-12)
- **P0**: [[event-bus]] WeakMethod + RuntimeError prune; WBS render fix (döngü içi import, `setUpdatesEnabled`).
- **P1**: [[gorevler-modulu]] paket bölünmesi; `project_dialog` + `form_utils` refactor; tema sözleşmesi bağlantıları ([[tema-sistemi]]); QSS modülerleştirme (base/ 8 modül).
- **P2**: `BaseRepository[T]` ([[veritabani-katmani]]); StringManager `language_changed` + ratchet testi + `project_dialog` migrasyonu ([[l10n-string-yonetimi]]); yazmalar senkron kararı ([[worker-altyapisi]]).

## P3 — Tamamlandı (2026-06-12)
1. ✅ **DIContainer bölünmesi**: `di_registries.py` (Repository/Service/Controller registry) + facade `__getattr__` delegasyonu ([[di-container]]).
2. ✅ **IconManager**: `QSvgRenderer`, `Icons` sabitleri, DRY, `try_instance()` ([[ikon-yonetimi]]).
3. ✅ **Script taşıma**: `commit_all.py`, `download_assets.py` → `scripts/`.

## P4 — Tamamlandı (2026-06-26 / 2026-06-27)

### UX İyileştirmeleri
- ✅ **Kart görünümü**: `_DecisionRow` ve `_NoteRow` `QWidget → QFrame + cssClass="panel"` dönüşümü; Kaynaklar sekmesiyle tutarlı görünüm.
- ✅ **Font sistemi fix**: `00_reset.qss`'ten `font-size: 13px` ve `font-family` hardcode kaldırıldı; `QApplication.setFont()` artık QSS tarafından override edilmiyor. Font önizleme + "Uygula" butonu akışı eklendi.
- ✅ **Anlık dil değişimi**: `MainWindow._on_language_changed` → `_setup_ui()` yeniden çağrısı; tüm sayfalar yeni dille anında yeniden oluşturuluyor. Restart mesaj kutusu kaldırıldı.
- ✅ **Backup butonu kaldırıldı**: Veri Yönetimi bölümünden DB yedekleme UI'ı çıkarıldı — backend operasyonu kullanıcıya yaptırılmamalı.
- ✅ **Sidebar hamburger düzeltmesi**: `_toggle_btn` `btn-secondary` yerine `#sidebar_toggle_btn` objectName ile özel şeffaf QSS kuralı aldı; light modda çizgiler artık görünüyor.
- ✅ **InfoPage yeniden tasarımı**: `QTextBrowser + HTML` → native PySide6 widget'ları; `IconManager` ile tema uyumlu SVG ikonlar; hero bölümü, iş akışı, özellik kartları, ipuçları, kısayollar bölümleri.

## P5 — Tamamlandı (2026-06-30)
- ✅ **Sesli komut (speech-to-text)**: Vosk çevrimdışı Türkçe model + `sounddevice`;
  `SpeechToTextService` → `TranscriptionWorker` ([[worker-altyapisi]] deseni) →
  `VoiceInputButton`/`attach_voice_button`. Görev/fikir başlığı, hızlı ekle ve tüm uzun
  metin alanlarında mikrofon. InfoPage'e özellik kartı + ipucu eklendi ([[sesli-komut]]).

## Sürekli kuyruk
- L10N migrasyonu: 21 dosya allowlist'te ([[l10n-string-yonetimi]]).
- ✅ Tamamlandı (2026-06-13): UI'daki Service Locator çağrıları (Theme/Icon/String/Pref/EventBus) constructor injection'a çevrildi; factory'ler `di.<manager>` ile besler ([[di-container]]).

İlgili: [[kurallar-ve-sozlesmeler]], [[log]]
