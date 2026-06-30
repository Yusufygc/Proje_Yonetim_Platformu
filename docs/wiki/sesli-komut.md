# Sesli Komut (Speech-to-Text)

QLineEdit/QTextEdit alanlarına mikrofonla dikte. Tamamen çevrimdışı — [Vosk](https://alphacephei.com/vosk/models) Türkçe modeli, internet/API anahtarı gerektirmez.

## Mimari (katman sırası)

```
VoiceInputButton (UI)
  → TranscriptionWorker (QThreadPool, [[worker-altyapisi]] deseni)
    → SpeechToTextService (Vosk model yaşam döngüsü)
      → vosk + sounddevice
```

- `presentation/widgets/voice_input_button.py` — `VoiceInputButton(IconActionButton)` toggle
  buton + `attach_voice_button(target, parent)` yardımcı fonksiyonu. `target`
  `QLineEdit | QTextEdit` olabilir (`VoiceTarget` union tipi); her ikisi de aynı butonla
  sarmalanır, container `QHBoxLayout` döndürür.
- `core/workers/transcription_worker.py` — `TranscriptionWorker(QRunnable)` +
  `TranscriptionSignals(QObject)` (`started`, `partial`, `final`, `error`, `finished`).
  `Worker` (genel amaçlı, tek atış) yerine ayrı sınıf: bu worker `stop()` çağrılana kadar
  sürekli döngüde kalır. GC güvenliği aynı desen — sınıf seviyesi `_active_workers` seti.
- `services/speech/speech_to_text_service.py` — `SpeechToTextService`: Vosk modelini
  **lazy** yükler (`ensure_loaded()`), `create_recognizer()` ile `KaldiRecognizer` üretir.
  Model yükleme ağır olduğundan her zaman Worker içinden çağrılır, boot'ta değil.
- DI: `app/di_registries.py` → `ServiceRegistry.speech_to_text` (`@cached_property`);
  `app/di_container.py` → `DIContainer.speech_service` property ([[di-container]] desenine uyumlu).

## Akış

1. Kullanıcı 🎤 butona tıklar → `VoiceInputButton._start_recording()` →
   `DIContainer.instance().speech_service` çekilir → `TranscriptionWorker` oluşturulup
   `start()` ile `QThreadPool`'a verilir.
2. Worker `run()` içinde `service.ensure_loaded()` (ilk çağrıda model diskten yüklenir) →
   `sounddevice.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1)`
   açılır; callback ses çerçevelerini `queue.Queue`'ya yazar.
3. Kuyruk döngüsü `recognizer.AcceptWaveform(data)` ile beslenir: tam cümlede `final`,
   ara sonuçta `partial` sinyali atılır (partial şu an UI'da kullanılmıyor — bkz. Kapsam Dışı).
4. `VoiceInputButton._on_final_text` hedefin tipine göre dallanır:
   `QLineEdit.insert()` (cursor konumuna) veya `QTextEdit` cursor-insert; her ikisinde de
   önceki metin boşlukla bitmiyorsa otomatik boşluk eklenir.
5. Tekrar tıklama → `worker.stop()` → `_stop_flag` set edilir → döngü çıkar →
   `FinalResult()` ile kalan parça da işlenir → `finished` sinyali.

## Model

- Yol: `app/config.py` → `VOSK_TR_MODEL_DIR = RESOURCES_DIR / "models" / "vosk-model-small-tr-0.3"`.
- Model dosyası (~35 MB) **repoya dahil değil** (`.gitignore`: `resources/models/`).
  Kurulum: README "Başlarken → Sesli komut modelini indir" adımı.
- Model klasör yapısı standart Vosk dizin yapısından farklı (am/conf/graph alt klasörleri
  yok, dosyalar düz: `final.mdl`, `HCLr.fst`, `Gr.fst`, `ivector/`); bu, küçük TR modelinin
  kendi paketleme biçimi — `vosk.Model()` sorunsuz yükler, doğrulandı.

## Hata yolları

- `core/exceptions/speech_exceptions.py`: `SpeechRecognitionError` (taban),
  `SpeechModelNotFoundError` (model klasörü yok/`vosk` kurulu değil),
  `MicrophoneUnavailableError` (cihaz açılamadı — `sounddevice.PortAudioError`).
- Her ikisi de Worker içinde yakalanır → `error` sinyali → `VoiceInputButton._on_error` →
  `EventBus.publish("toast.show", type_="warning")`; stack trace kullanıcıya gösterilmez,
  UI thread bloklanmaz.

## Bağımlılıklar

`pyproject.toml`: `vosk>=0.3.45`, `sounddevice>=0.4.6`.

## Kapsam

Mikrofon butonu eklenen alanlar:
- **QLineEdit:** görev başlığı (`task_dialog.py`), fikir başlığı (`idea_dialog.py`),
  hızlı görev ekle (`pages/tasks/page.py`).
- **QTextEdit:** tüm çok satırlı açıklama/not/gerekçe/çözüm alanları (idea, decision, note,
  resource, task, project dialogları + `memo_page.py` editörü).

## Kapsam Dışı (sonraki iterasyon)

- Otomatik model indirme (şu an elle zip indir + çıkar).
- Canlı `partial` sonucun alana önizleme olarak akıtılması — yalnızca `final` segment eklenir.
- Cloud/Whisper motoru seçeneği (ayarlardan motor değiştirme).

İlgili: [[worker-altyapisi]], [[di-container]], [[ikon-yonetimi]], [[log]]
