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
- [[analitik-sayfasi]] — Analitik ve Metrikler: KPI, zaman serisi, açılan/biten akışı, aktivite ısı haritası, durum halkası; veri kaynakları ve kararlar.
- [[gorevler-modulu]] — QML Görev Ağacı (WBS): filtreler, kopyalama/çoğaltma, akıllı daraltma, scroll koruma, sürükle-bırak taşıma, satır içi checklist ve üst görev durum kuralı.
- [[notlar-modulu]] — Otomatik kaydedilen Markdown notlar, serbest çizim tuvali, geometrik şekiller ve resim ekleme.
- [[sesli-komut]] — Vosk tabanlı çevrimdışı sesli dikte; `VoiceInputButton.qml` + `VoiceBridge` + `TranscriptionWorker` + `SpeechToTextService`.
- [[guncelleme-sistemi]] — Açılışta GitHub Releases denetimi, güncelleme penceresi, SHA-256 doğrulamalı indirme, SAC kurtarma ve sessiz kurulum.
- [[liste-siralama]] — Liste sıralama altyapısı (`sort_order`/`display_order`, `reorder` zinciri); bu listeler için QML'de sürükle-bırak arayüzü yok (görev ağacı için bkz. [[gorevler-modulu]]).

## Kurallar ve Süreç
- [[tanitim-videosu]] — `video/` altındaki otomatik tanıtım videosu hattı: kare yakalama, seslendirme, Remotion kurgusu, denetim ve lisanslar.
- [[exe-dagitim-rehberi]] — Kararlı exe mimarisi, `packaging/launcher.sha256` kapısı, `build_exe.py`, `build_installer.py` ve `build_verify.py` doğrulamaları.
- [[surum-yayinlama]] — Etiketle sürüm yayınlama: `tools/release.py`, release iş akışı, kontrol listesi, hata/geri alma tablosu ve asistan kısıtı.
- [[kurallar-ve-sozlesmeler]] — RULES.md limitleri, bellek yönetimi, tema/L10N sözleşmeleri ve commit kuralları.
- [[yol-haritasi]] — Tamamlanan P0-P2 işleri ve bekleyen P3 + L10N migrasyon kuyruğu.
