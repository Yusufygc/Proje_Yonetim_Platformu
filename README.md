# Proje Yönetim ve Takip Platformu

![Sürüm](https://img.shields.io/badge/s%C3%BCr%C3%BCm-0.1.5-38BDF8)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.6+-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.13+-6BA3BE)](https://alembic.sqlalchemy.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)](https://www.microsoft.com/windows)

Masaüstü tabanlı proje, görev ve fikir yönetim uygulaması. PySide6 ile oluşturulmuş modern arayüzü, SQLAlchemy ORM destekli SQLite veritabanı ve katmanlı mimarisiyle; bireysel geliştiriciler ve küçük ekipler için tasarlanmış, kurulum gerektirmeyen bir üretkenlik aracıdır.

---

## Özellikler

- 📊 **Ana Panel** — İstatistik kartları, tıkanan projeler, son aktiviteler ve yüksek öncelikli açık görevler tek ekranda
- 📁 **Proje Yönetimi** — Durum takibi (Planlandı, Aktif, Beklemede, Tamamlandı…), sağlık durumu, öncelik, karar kayıtları, notlar ve kaynak bağlantıları
- 🗂️ **WBS Görev Ağacı** — Hiyerarşik iş kırılım yapısı; durum, öncelik ve türe göre filtreleme; checklist ve alt görev desteği
- 💡 **Fikir Yönetimi** — Ham fikirden projeye dönüşüm akışını izleme; fikir puanlama ve kategorilendirme
- 🎨 **Tema Desteği** — Koyu ve açık tema; 6 küratörlü renk paleti (Slate, Indigo, Emerald, Ocean, Rose, Violet), temalara özel desenli kenar çubuğu arka planları
- 🌐 **Yerelleştirme** — Türkçe ve İngilizce arayüz; tüm metinler çeviri anahtarları üzerinden yönetilir
- 🔔 **Toast Bildirimleri** — İşlem sonuçları için animasyonlu, otomatik kapanan bildirim sistemi
- 💾 **Otomatik Yedekleme** — Başlangıçta arka planda veritabanı yedeği; `~/.proje_takip/.backups/` altında saklanır
- 🎤 **Sesli Komut (Çevrimdışı)** — Vosk Türkçe modeliyle mikrofondan görev/fikir başlığı, açıklama ve notları sese dönüştürerek girme; internet/API anahtarı gerektirmez
- 📝 **Notlar ve Çizim Tuvali** — Markdown destekli otomatik kaydedilen notlar, serbest çizim, geometrik şekiller, resim ekleme ve kaydırılabilir tuval araç çubuğu
- 📋 **Görev Kopyalama & Akıllı Ağaç** — Panoya kopyalama ve anında çoğaltma (duplicate), tamamlanan alt görevlerin otomatik daraltılması ve kaydırma konumu koruması
- 📈 **Gelişmiş Metrikler ve Analitik** — KPI kartları, zaman serileri, proje bazlı filtreleme ve performans istatistikleri

---

## Ekran Görüntüleri

<!-- Ekran görüntüleri buraya eklenecek -->

---

## Mimari

Uygulama, katı bir katmanlı mimariye sahiptir; katmanlar arası doğrudan atlamalar ve döngüsel bağımlılıklar yasaktır.

```
┌─────────────────────────────────────────────────┐
│            Sunum Katmanı  (PySide6 + QML)       │
│   QML Görünümler · ViewModel'ler · Köprüler     │
├─────────────────────────────────────────────────┤
│            Controller Katmanı                   │
│   ProjectController · TaskController · …        │
├─────────────────────────────────────────────────┤
│            Servis Katmanı                       │
│   ProjectService · TaskService · IdeaService…   │
├─────────────────────────────────────────────────┤
│            Repository Katmanı                   │
│   SQLAlchemy ORM  ·  Alembic Migrations         │
├─────────────────────────────────────────────────┤
│   SQLite  ·  ~/.proje_takip/proje_takip.db      │
└─────────────────────────────────────────────────┘
```

Bileşenler arası iletişim `EventBus` üzerinden sağlanır; bağımlılıklar `DIContainer` tarafından enjekte edilir.

---

## Teknoloji Yığını

| Bileşen | Teknoloji | Sürüm |
|---------|-----------|-------|
| Arayüz çerçevesi | PySide6 (Qt for Python) | 6.6+ |
| Veritabanı ORM | SQLAlchemy | 2.0+ |
| Şema migrasyonu | Alembic | 1.13+ |
| Veritabanı | SQLite | — |
| Python | CPython | 3.10+ |
| EXE paketleme | PyInstaller | 6.0+ |
| Sesli komut (STT) | Vosk (çevrimdışı) | 0.3+ |
| Ses yakalama | sounddevice | 0.4+ |
| Linting | ruff | 0.6+ |
| Tip denetimi | mypy | 1.8+ |
| Test | pytest + pytest-qt | 8.0+ |

---

## Başlarken

### A) Kurulum Dosyası ile — Son kullanıcı (önerilen)

GitHub Releases'ten indirilen `ProjeTakipPlatformu-Setup-<sürüm>.exe` dosyasını çalıştırıp kurulumu tamamlayın (`%LOCALAPPDATA%\Programs\ProjeTakipPlatformu` altına UAC gerektirmeden kurulur).

Uygulama verileri `%LOCALAPPDATA%\ProjeTakip\` altında otomatik oluşturulur:

```
%LOCALAPPDATA%\ProjeTakip\
├── proje_takip.db       # SQLite veritabanı
├── updates.json         # Güncelleme tercihleri (açılış denetimi, atlanan sürüm)
├── .backups/            # Otomatik yedekler
└── logs/app.log         # Uygulama günlüğü
```

---

### B) Kaynak Koddan — Geliştirici

#### 1. Depoyu klonla

```bash
git clone https://github.com/Yusufygc/Proje_Yonetim_Platformu.git
cd proje_takip_platformu
```

#### 2. Sanal ortam oluştur ve etkinleştir

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Komut İstemi):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> Etkinleştirildiğinde terminal satırı başında `(.venv)` görünür.

#### 3. Bağımlılıkları yükle

```bash
pip install -e .
```

Bu komut `pyproject.toml` içindeki tüm bağımlılıkları yükler.

#### 4. Sesli komut modelini indir (opsiyonel)

Sesli komut özelliği [Vosk](https://alphacephei.com/vosk/models) Türkçe modelini kullanır.
Model boyutu (~35 MB) nedeniyle depoya dahil değildir; özelliği kullanmak için:

1. [`vosk-model-small-tr-0.3.zip`](https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip) indir.
2. `resources/models/vosk-model-small-tr-0.3/` altına çıkar (zip içeriği doğrudan bu klasöre).

Model yoksa uygulama normal çalışır; mikrofon butonuna tıklandığında bilgilendirici bir
uyarı (toast) gösterilir, diğer özellikler etkilenmez.

#### 5. Uygulamayı başlat

```bash
python main.py
```

Veritabanı ilk başlatmada otomatik oluşturulur; ayrıca `alembic upgrade head` çalıştırmaya gerek yoktur.

---

## EXE Derleme ve Sürüm Yayınlama

Kurulum dosyasını ve kararlı `.exe`'yi tek komutla derlemek için:

```powershell
python build_installer.py
```

Bu komut sırasıyla:
1. PyInstaller (`--onedir --debug=noarchive`, sabit `packaging/launcher.py` ve sabit `packaging/launcher_version_info.txt` ile) `dist\ProjeTakipPlatformu\ProjeTakipPlatformu.exe` dosyasını derler.
2. Derlenen `.exe`'nin SHA-256 özetini onaylı `packaging/launcher.sha256` kapısıyla doğrular.
3. Yerelde çalıştırma denemesi yapar (`build_verify.launch_check`).
4. Inno Setup (`packaging/ProjeTakipPlatformu.iss`) ile `dist\installer\ProjeTakipPlatformu-Setup-<sürüm>.exe` ve `.sha256` dosyasını üretip sessiz kurulum/kaldırma doğrulamasından geçirir.

> **Not (Windows SmartScreen / Akıllı Uygulama Denetimi):** Kurulum dosyası imzasızdır. SmartScreen uyarısında **Ek bilgi → Yine de çalıştır** seçilebilir; Akıllı Uygulama Denetimi (SAC) engelinde dosya birkaç dakika sonra yeniden çalıştırılmalı veya güncel sürüm indirilmelidir.

### Sürüm yayınlama ve otomatik güncelleme

Kurulu uygulama açılışta GitHub Releases'te yeni sürüm arar ve güncelleme teklif eder. Sürüm çıkarmak için:

```powershell
python tools/release.py 0.2.0
git push origin main
git push origin v0.2.0
```

Etiket push edilince `.github/workflows/release.yml` kalite kapılarını koşar, kurulum dosyasını ve `.sha256` özetini yayınlar. Kurallar: `docs/Project_docs/RULES.md` §8; adımlar ve geri alma: `docs/wiki/surum-yayinlama.md`; kararlı exe tasarımı: `docs/wiki/exe-dagitim-rehberi.md`; güncelleme mekanizması: `docs/wiki/guncelleme-sistemi.md`.

---

## Klasör Yapısı

```
proje_takip_platformu/
├── app/
│   ├── config.py             # Uygulama sabitleri ve yol tanımları
│   ├── di_container.py       # Dependency Injection konteyneri
│   └── di_registries.py      # Repository / Service / Controller kayıt noktaları
├── controllers/              # UI ile servis katmanı arasındaki köprü
├── core/
│   ├── events/               # EventBus — bileşenler arası gevşek bağlantı
│   ├── managers/             # ThemeManager, StringManager, FontManager, BackupManager…
│   └── workers/              # QThreadPool worker'ları (Worker, TranscriptionWorker)
├── domain/
│   ├── enums/                # TaskStatus, Priority, TaskType, IdeaStatus…
│   └── models/               # SQLAlchemy model tanımları (14 model)
├── infrastructure/
│   ├── migrations/           # Alembic migrasyon scriptleri
│   └── repositories/         # Veritabanı erişim katmanı
├── presentation/
│   ├── qml/                  # QML arayüzü: main.qml, shell/, views/, dialogs/, components/, theme/
│   ├── viewmodels/           # QML'e açılan ViewModel, liste modeli ve köprü sınıfları
│   ├── utils/                # i18n (tr()) yardımcıları
│   ├── modules.py            # Kenar çubuğu modül kayıtları (ModuleRegistry)
│   └── dimensions.py         # Font ailesi sabitleri
├── resources/
│   ├── fonts/                # JetBrains Mono, Plus Jakarta Sans
│   ├── locales/              # strings.tr.json, strings.en.json
│   ├── models/               # Vosk STT modeli (depoya dahil değil — bkz. "Başlarken")
│   └── themes/               # Renk paleti JSON dosyaları
├── services/                 # İş mantığı katmanı (10 servis + speech/ — sesli komut)
├── tests/                    # pytest test paketi
├── icons/                    # Uygulama ikonu
├── packaging/                # Sabit launcher, sürüm kaynağı, onay hash'i ve Inno Setup betiği
├── tools/                    # Sürüm yayınlama aracı (release.py)
├── scripts/                  # Yardımcı scriptler (font indirme, kalite)
├── build_exe.py              # Kararlı exe PyInstaller derleyicisi ve özet kapısı
├── build_installer.py        # Tek komutla exe + kurulum + doğrulama aracı
├── build_verify.py           # EXE ve sessiz kurulum/kaldırma doğrulayıcısı
├── version.py                # Tek uygulama sürüm kaynağı
├── main.py                   # Uygulama giriş noktası (QML arayüzünü başlatır)
├── pyproject.toml            # Proje meta verisi ve bağımlılıklar
└── alembic.ini               # Alembic yapılandırması
```

---

## Geliştirme

### Kod kalitesi

```bash
# Linting
ruff check .

# Tip denetimi
mypy .

# Testler
pytest

# Tüm kontroller
python scripts/quality.py
```

### Yeni migrasyon oluşturma

```bash
alembic revision --autogenerate -m "açıklama"
alembic upgrade head
```

### Dil dosyaları

Çeviri anahtarları `resources/locales/strings.tr.json` ve `strings.en.json` dosyalarındadır.
Yeni arayüz metni eklenirken her iki dosyaya da ilgili anahtar eklenmelidir.

---

## Geliştirme Notları

- Doğrudan SQLite sorgusu yazılmaz; tüm veri erişimi repository katmanı üzerinden yapılır.
- Tema renkleri `ThemeManager.color(key)` ve `ThemeBridge` üzerinden çözülür; QML dosyalarına sabit renk yazılmaz.
- Tüm kullanıcıya görünen metinler `tr(key, varsayılan)` ile sarmalanır.
- Python tarafında oluşturulan her `QObject`'e `parent=` verilir (bellek sızıntısını önlemek için).
- Bileşenler arası iletişim `EventBus.publish()` / `EventBus.subscribe()` ile sağlanır.
- Bir dosya 400 satırı veya bir sınıf 15 public metodu aşıyorsa alt modüllere bölünmesi gerekir.
- UI thread'i bloke eden işlemler (DB sorgusu, dosya okuma) `QThread` veya `QTimer` ile asenkrona alınır.
