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
- [[tema-sistemi]] — JSON palet + `ThemeBridge` ile QML'e açılan tokenlar; 6 küratörlü tema paketi (Slate/Indigo/Emerald/Ocean/Rose/Violet) × 2 mod. Font boyutu sabit (`FontFamily.DEFAULT_SIZE`), kullanıcı sadece aile seçer.
- [[l10n-string-yonetimi]] — StringManager, `tr()` / `I18nBridge.tr()`, dil değişimi ve ratchet testi.
- [[ikon-yonetimi]] — IconManager SVG renklendirme/cache mekanizması ve QML `IconImageProvider`.
- [[gorevler-modulu]] — QML Görev Ağacı (WBS): filtreler, kopyalama/çoğaltma, akıllı daraltma, scroll koruma ve üst görev durum kuralı.
- [[notlar-modulu]] — Markdown notlar, zengin serbest çizim tuvali, geometrik şekiller, algoritma akış şemaları ve resim ekleme.
- [[sesli-komut]] — Vosk tabanlı çevrimdışı sesli dikte; `VoiceInputButton.qml` + `VoiceBridge` + `TranscriptionWorker` + `SpeechToTextService`.
- [[liste-siralama]] — Liste sıralama altyapısı (`sort_order`/`display_order`, `reorder` zinciri); QML'de sürükle-bırak arayüzü şu an yok.

## Kurallar ve Süreç
- [[kurallar-ve-sozlesmeler]] — RULES.md limitleri, bellek yönetimi, tema/L10N sözleşmeleri ve commit kuralları.
- [[yol-haritasi]] — Tamamlanan P0-P2 işleri ve bekleyen P3 + L10N migrasyon kuyruğu.
