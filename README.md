# Proje Yönetim ve Takip Platformu

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
- 🗂️ **WBS Görev Ağacı** — Sürükle-bırak destekli hiyerarşik iş kırılım yapısı; durum, öncelik ve türe göre filtreleme; checklist ve alt görev desteği
- 💡 **Fikir Yönetimi** — Ham fikirden projeye dönüşüm akışını izleme; fikir puanlama ve kategorilendirme
- 🎨 **Tema Desteği** — Koyu ve açık tema; Federal Blue/Altın ile Sapphire/Quicksand renk paletleri; özel tema oluşturma ve dışa aktarma
- 🌐 **Yerelleştirme** — Türkçe ve İngilizce arayüz; tüm metinler çeviri anahtarları üzerinden yönetilir
- 🔔 **Toast Bildirimleri** — İşlem sonuçları için animasyonlu, otomatik kapanan bildirim sistemi
- 💾 **Otomatik Yedekleme** — Başlangıçta arka planda veritabanı yedeği; `~/.proje_takip/.backups/` altında saklanır

---

## Ekran Görüntüleri

<!-- Ekran görüntüleri buraya eklenecek -->

---

## Mimari

Uygulama, katı bir katmanlı mimariye sahiptir; katmanlar arası doğrudan atlamalar ve döngüsel bağımlılıklar yasaktır.

```
┌─────────────────────────────────────────────────┐
│            Sunum Katmanı  (PySide6)             │
│   Pages · Dialogs · Widgets · Shell             │
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
| Kimlik bilgisi depolama | keyring | 25.0+ |
| Linting | ruff | 0.6+ |
| Tip denetimi | mypy | 1.8+ |
| Test | pytest + pytest-qt | 8.0+ |

---

## Başlarken

### A) EXE ile — Son kullanıcı (önerilen)

`dist\ProjeTakipPlatformu.exe` dosyasını çift tıkla. Ek kurulum gerekmez.

Uygulama verileri `%USERPROFILE%\.proje_takip\` altında otomatik oluşturulur:

```
~/.proje_takip/
├── proje_takip.db       # SQLite veritabanı
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

#### 4. Uygulamayı başlat

```bash
python main.py
```

Veritabanı ilk başlatmada otomatik oluşturulur; ayrıca `alembic upgrade head` çalıştırmaya gerek yoktur.

---

## EXE Derleme

Kaynak koddan tek dosya EXE üretmek için:

```powershell
.venv\Scripts\pyinstaller.exe packaging\proje_takip_platformu.spec --noconfirm --clean
```

Çıktı: `dist\ProjeTakipPlatformu.exe` (~57 MB, bağımsız tek dosya)

Build parametreleri `packaging\proje_takip_platformu.spec` içinde tanımlıdır.

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
│   └── managers/             # ThemeManager, StringManager, FontManager, BackupManager…
├── domain/
│   ├── enums/                # TaskStatus, Priority, TaskType, IdeaStatus…
│   └── models/               # SQLAlchemy model tanımları (14 model)
├── infrastructure/
│   ├── migrations/           # Alembic migrasyon scriptleri
│   └── repositories/         # Veritabanı erişim katmanı
├── presentation/
│   ├── dialogs/              # Görev, proje, fikir oluşturma/düzenleme iletişim kutuları
│   ├── pages/                # Ana Panel, Projeler, Görevler (WBS), Fikirler, Ayarlar…
│   ├── shell/                # Ana pencere ve kenar çubuğu
│   ├── utils/                # i18n (tr()), stil yardımcıları, filtreler
│   └── widgets/              # Toast, proje kartı, detay paneli, skeleton loader…
├── resources/
│   ├── fonts/                # JetBrains Mono, Plus Jakarta Sans
│   ├── locales/              # strings.tr.json, strings.en.json
│   ├── styles/               # QSS tema dosyaları (18 dosya)
│   └── themes/               # Renk paleti JSON dosyaları
├── services/                 # İş mantığı katmanı (10 servis)
├── tests/                    # pytest test paketi
├── icons/                    # Uygulama ikonu
├── packaging/                # PyInstaller spec ve EXE meta verisi
├── scripts/                  # Yardımcı scriptler (font indirme vb.)
├── main.py                   # Uygulama giriş noktası
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
python quality.py
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
- Tema renkleri `ThemeManager.color(key)` ile çözülür; QSS dosyalarına sabit renk yazılmaz.
- Tüm kullanıcıya görünen metinler `tr(key, varsayılan)` ile sarmalanır.
- Widget'lar `parent=` parametresi ile oluşturulur (bellek sızıntısını önlemek için).
- Bileşenler arası iletişim `EventBus.publish()` / `EventBus.subscribe()` ile sağlanır.
- Bir dosya 400 satırı veya bir sınıf 15 public metodu aşıyorsa alt modüllere bölünmesi gerekir.
- UI thread'i bloke eden işlemler (DB sorgusu, dosya okuma) `QThread` veya `QTimer` ile asenkrona alınır.
