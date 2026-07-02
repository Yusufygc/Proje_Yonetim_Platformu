# LLM Wiki — İçerik Haritası

Proje Yönetim ve Takip Platformu bilgi tabanı. Her oturum başında bu dosya okunur;
detay için ilgili sayfaya inilir. Kronolojik kayıt: [[log]].

## Mimari
- [[mimari-genel-bakis]] — Katmanlı mimari (presentation → controllers → services → repositories), modül haritası ve veri akışı.
- [[di-container]] — Bağımlılık enjeksiyonu, bootstrap sırası ve singleton manager'lar.
- [[event-bus]] — WeakMethod tabanlı pub/sub mekanizması ve kullanım kuralları.
- [[worker-altyapisi]] — QThreadPool tabanlı asenkron okuma deseni ve "yazmalar senkron" kararı.

## Veri Katmanı
- [[veritabani-katmani]] — DatabaseManager, scoped_session, WAL modu ve `BaseRepository[T]` / `ProjectScopedRepository[T]` desenleri.

## Sunum Katmanı
- [[tema-sistemi]] — JSON palet + token'lı modüler QSS yapısı; 6 küratörlü tema paketi (Slate/Indigo/Emerald/Ocean/Rose/Violet) × 2 mod. Font boyutu sabit (`FontFamily.DEFAULT_SIZE`) — QSS'teki 56+ sabit `font-size` kuralı zaten `QApplication.setFont()` boyutunu eziyordu, kullanıcı sadece aile seçer.
- [[l10n-string-yonetimi]] — StringManager, `tr()` yardımcısı, `language_changed` → MainWindow UI yeniden kurulum, ratchet testi.
- [[ikon-yonetimi]] — IconManager SVG renklendirme/cache mekanizması ve planlanan iyileştirmeler.
- [[gorevler-modulu]] — WBS görev sayfası paketi (`pages/tasks/`): filter bar + ağaç + sayfa kompozisyonu.
- [[sesli-komut]] — Vosk tabanlı çevrimdışı sesli dikte; `VoiceInputButton` + `TranscriptionWorker` + `SpeechToTextService`.
- [[liste-siralama]] — Notlar/Fikirler/Projeler listelerinde sürükle-bırak sıralama; `DragReorderController` + `sort_order`/`display_order` kolonları.

## Kurallar ve Süreç
- [[kurallar-ve-sozlesmeler]] — RULES.md limitleri, bellek yönetimi, tema/L10N sözleşmeleri ve commit kuralları.
- [[yol-haritasi]] — Tamamlanan P0-P2 işleri ve bekleyen P3 + L10N migrasyon kuyruğu.
