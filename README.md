# Proje Yönetim ve Takip Platformu

Masaüstü tabanlı proje, görev ve fikir yönetim uygulaması. PySide6 ile oluşturulmuş, modern ve tema destekli arayüze sahiptir.

## Özellikler

- **Proje Yönetimi** — Proje oluşturma, durum takibi (Planlandı, Aktif, Beklemede, Tamamlandı vb.), sağlık durumu ve öncelik atama; karar kayıtları, notlar ve kaynak bağlantıları
- **WBS Görev Ağacı** — Sürükle-bırak destekli hiyerarşik iş kırılım yapısı, durum/öncelik/tür filtreleme
- **Fikir Yönetimi** — Ham fikirden projeye dönüşüm akışını izleme
- **Ana Panel** — İstatistik kartları, tıkanan projeler, son aktiviteler, yüksek öncelikli açık görevler ve son fikirler
- **Tema Desteği** — Koyu ve açık tema, Federal Blue / Altın (koyu) ve Sapphire / Quicksand (açık) renk paletleri
- **Yerelleştirme** — Türkçe ve İngilizce dil desteği; tüm arayüz metinleri çeviri anahtarları üzerinden yönetilir
- **Toast Bildirimleri** — İşlem sonuçları için animasyonlu, otomatik kapanan bildirim sistemi

## Teknoloji Yığını

| Bileşen | Teknoloji |
|---------|-----------|
| Arayüz | PySide6 6.6+ |
| Veritabanı ORM | SQLAlchemy 2.0+ |
| Migrasyon | Alembic 1.13+ |
| Veritabanı | SQLite |
| Python | 3.10+ |

## Gereksinimler

- Python 3.10 veya üstü
- pip 23+
- Git (isteğe bağlı)

Windows'ta Python kurulu değilse [python.org](https://www.python.org/downloads/) adresinden indirilebilir. Kurulum sırasında **"Add Python to PATH"** seçeneğinin işaretli olduğundan emin olunmalıdır.

---

## Kurulum

### 1. Depoyu klonla

```bash
git clone <repo-url>
cd proje_takip_platformu
```

### 2. Sanal ortam oluştur ve etkinleştir

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Komut İstemi / cmd.exe):**
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

### 3. Bağımlılıkları yükle

```bash
pip install pyside6 sqlalchemy alembic keyring
```

Geliştirme araçlarıyla birlikte kurmak için:

```bash
pip install pyside6 sqlalchemy alembic keyring mypy ruff pytest pytest-qt
```

`pyproject.toml` varsa (uv veya pip ile):

```bash
pip install -e .
```

### 4. Veritabanını hazırla

```bash
alembic upgrade head
```

Bu komut `infrastructure/migrations/` altındaki tüm migrasyon scriptlerini sırasıyla çalıştırır ve `proje_takip.db` dosyasını oluşturur.

> Veritabanı şeması değiştiğinde (`git pull` sonrası vb.) bu komutu tekrar çalıştırmak yeterlidir.

### 5. Uygulamayı başlat

```bash
python main.py
```

---

## Sanal Ortam Hakkında Sık Sorulanlar

**Sanal ortamı nasıl devre dışı bırakırım?**
```bash
deactivate
```

**Sanal ortam bozulursa ne yapmalıyım?**
```bash
# Mevcut ortamı sil ve yeniden oluştur
rm -rf .venv          # Linux/macOS
Remove-Item -Recurse -Force .venv   # PowerShell

python -m venv .venv
# Ardından 3. adımı tekrarla
```

**`python` komutu bulunamazsa:**
```bash
# Sistemde python3 olarak kayıtlıysa
python3 -m venv .venv
```

**PowerShell'de script çalıştırma engeli:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Geliştirme

### Kod kalitesi

```bash
# Linting (ruff)
ruff check .

# Tip denetimi (mypy)
mypy .

# Testler
pytest

# Tüm kontroller (quality.py scripti ile)
python quality.py
```

### Yeni migrasyon oluşturma

```bash
alembic revision --autogenerate -m "açıklama"
alembic upgrade head
```

### Dil dosyaları

Çeviri anahtarları `resources/locales/strings.tr.json` ve `strings.en.json` dosyalarındadır. Yeni bir arayüz metni eklenirken her iki dosyaya da ilgili anahtar eklenmelidir.

---

## Klasör Yapısı

```
proje_takip_platformu/
├── controllers/          # UI ile servis katmanı arasındaki köprü
├── core/
│   ├── events/           # EventBus — bileşenler arası gevşek bağlantı
│   └── managers/         # ThemeManager, StringManager, FontManager
├── domain/
│   ├── enums/            # TaskStatus, Priority, TaskType, IdeaStatus...
│   └── models/           # SQLAlchemy model tanımları
├── infrastructure/
│   ├── migrations/       # Alembic migrasyon scriptleri
│   └── repositories/     # Veritabanı erişim katmanı
├── presentation/
│   ├── dialogs/          # Görev, proje, fikir oluşturma/düzenleme iletişim kutuları
│   ├── pages/            # Ana Panel, Projeler, Görevler (WBS), Fikirler, Ayarlar
│   ├── shell/            # Ana pencere ve kenar çubuğu
│   ├── utils/            # i18n (tr()), ui_utils, stil yardımcıları
│   └── widgets/          # Toast, proje kartı, detay paneli vb.
├── resources/
│   ├── fonts/            # JetBrains Mono, Plus Jakarta Sans
│   ├── locales/          # strings.tr.json, strings.en.json
│   └── styles/           # QSS tema dosyaları
├── scripts/              # Yardımcı scriptler (font indirme vb.)
├── services/             # İş mantığı katmanı
├── main.py               # Uygulama giriş noktası
├── pyproject.toml        # Proje meta verisi ve bağımlılıklar
└── alembic.ini           # Alembic yapılandırması
```

---

## Geliştirme Notları

- Doğrudan SQLite sorgusu yazılmaz; tüm veri erişimi repository katmanı üzerinden yapılır.
- Tema renkleri `ThemeManager.color(key)` ile çözülür; QSS'e sabit renk yazılmaz.
- Tüm kullanıcıya görünen metinler `tr(key, varsayılan)` ile sarmalanır.
- Widget'lar `parent=` parametresi ile oluşturulur (bellek sızıntısını önlemek için).
- Bileşenler arası iletişim `EventBus.publish()` / `EventBus.subscribe()` ile sağlanır.
- Bir dosya 400 satırı veya bir sınıf 15 metodu aşıyorsa alt modüllere bölünmesi gerekir.
