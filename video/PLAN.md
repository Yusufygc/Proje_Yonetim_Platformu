# Tanıtım videosu uygulama planı

**Tasarım:** [TASARIM.md](TASARIM.md). **Yapılandırma:** [scenario.yaml](scenario.yaml).
**Yürütme:** aynı oturumda, sırayla. Commit yalnızca kullanıcı isteyince atılır.

## Genel kurallar
- Komutlar proje kökünden, `.venv` ile çalışır. Yollar `pathlib` ile, dosyalar UTF-8.
- Uygulama kodu (`app/`, `core/`, `presentation/`, ...) değiştirilmez.
- Gerçek veri klasörüne ve kayıt defterindeki tercihlere yazılmaz.
- Dosya en fazla 400 satır, fonksiyon yaklaşık 25 satır, tip ipuçları zorunlu.

## Dosyalar
| Dosya | Sorumluluk |
|---|---|
| `capture/isolation.py` | Geçici veri klasörü, `QSettings` yönlendirmesi, ortam değişkenleri |
| `capture/recorder.py` | `grabWindow` kareleri ve olay kaydı (`events.json`) |
| `capture/driver.py` | Öğeyi metninden bulma, sentetik fare ve klavye |
| `capture/seed.py` | Sabit örnek veri |
| `capture/scenes.py` | Sahne eylemleri |
| `capture/run.py` | Giriş noktası: `--scene <id>` veya tümü |
| `voice.py` | Supertonic seslendirme ve ses örnekleri |
| `narration.py`, `timeline.py` | Cümle bazlı seslendirme, zaman çizelgesi, `.srt` |
| `synth.py`, `soundtrack.py` | Müzik, efekt, karışım, ses seviyesi |
| `checks.py` | Otomatik video denetimi |
| `remotion/` | Kurgu |
| `build.py` | Tek komutla üretim ve denetim |
| `tests/` | Saf mantığın testleri |

## Görev 1: Yakalama prototipi
Soru: 3840x2160 kare alınıyor mu, sanal saat animasyonu sabit adımla ilerletiyor mu?
- `isolation.prepare(root: Path) -> None`, uygulama içe aktarılmadan önce çağrılır.
- `QApplication.exec` sarılır; yönetmen `run_qml_app()` kurulumundan sonra devreye girer.
- Kabul: her kare 3840x2160; 200 ms'lik animasyon 30 fps'te yaklaşık 6 ara kare verir;
  iki çalıştırmada kare sayısı aynıdır; kayıt defteri anahtarı değişmez.
- Kare alma süresi (ms/kare) ölçülüp raporlanır.

## Görev 2: Örnek veri ve sürücü
- `seed.seed_database(today: date) -> None`: README görüntülerindeki içerik ve 12 haftalık geçmiş.
- `driver.find_item(window, text: str) -> QQuickItem`: görünür öğeyi `text` özelliğinden bulur,
  bulamazsa `LookupError`.
- `driver.click(item) -> None`: imleç olayını kaydeder, sonra tıklar.
- Test: `test_seed_database_when_run_should_create_expected_counts`.

## Görev 3: Sahneler
- `scenes.SCENES: dict[str, Callable]`; anahtarlar `scenario.yaml` içindeki `tur: uygulama` kimlikleri.
- Test: `test_scenes_when_scenario_loaded_should_cover_every_app_scene`.

## Görev 4: Ses
- Sahne başına WAV (`voice.Narrator.speak(text: str, target: Path) -> float`), süre ölçümü.
- Zaman çizelgesi: `sahne süresi = max(sure, ses + 0.8 sn)`; `timeline.json` ve `demo.srt` üretilir.
- Test: `test_build_timeline_when_voice_longer_should_extend_scene`,
  `test_write_srt_when_turkish_text_should_keep_utf8`.

## Görev 5: Kurgu
- Remotion 4.x, sürümler sabit. Girdi: `timeline.json`, kare videoları, `events.json`.
- Bileşenler: pencere çerçevesi, kamera, imleç ve tıklama halkası, başlık, altyazı, giriş ve kapanış kartı.

## Onay noktası 2
Kanca ve `fikir_proje` sahnelerinden stil karesi ve kısa taslak. Onaydan önce tüm sahneler üretilmez.

## Görev 6: Tam üretim, denetim, teslim
- `build.py`, `blackdetect`, `freezedetect`, `loudnorm`, süre ve çözünürlük kontrolü.
- Her sahnenin başı, ortası ve sonundan kare incelenir.
- `docs/wiki/` ve README'ye kısa not.

## Zorlanacak durumlar
- Aranan metin ekranda iki kez var veya görünmüyor: sessiz yanlış tıklama yerine hata.
- Sahne tek başına yeniden üretiliyor: önceki sahneye bağlı olmaz, kendi başlangıç durumunu kurar.
- Windows ölçeklendirmesi %100'den farklı: kare boyutu yine 3840x2160 olur, olmazsa üretim durur.
- Türkçe karakter yazma (`ş`, `ğ`, `İ`): yazılan metin ekrandakiyle aynıdır.
- Ses modeli eksik: indirme komutunu söyleyen hata verilir.
