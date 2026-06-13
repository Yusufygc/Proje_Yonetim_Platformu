# Proje Yönetim ve Takip Platformu

Masaüstü tabanlı proje, görev ve fikir yönetim uygulaması. PySide6 ile oluşturulmuş, modern ve tema destekli arayüze sahiptir.

## Özellikler

- **Proje Yönetimi** — Proje oluşturma, durum takibi (Planlandı, Aktif, Beklemede, Tamamlandı vb.), sağlık durumu ve öncelik atama
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

## Kurulum

```bash
# Bağımlılıkları kur
pip install pyside6 sqlalchemy alembic

# Veritabanı migrasyonlarını uygula
alembic upgrade head

# Uygulamayı başlat
python main.py
```

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
└── services/             # İş mantığı katmanı
```

## Geliştirme Notları

- Doğrudan SQLite sorgusu yazılmaz; tüm veri erişimi repository katmanı üzerinden yapılır.
- Tema renkleri `ThemeManager.color(key)` ile çözülür; QSS'e sabit renk yazılmaz.
- Tüm kullanıcıya görünen metinler `tr(key, varsayılan)` ile sarmalanır.
- Widget'lar `parent=` parametresi ile oluşturulur (bellek sızıntısını önlemek için).
- Bileşenler arası iletişim `EventBus.publish()` / `EventBus.subscribe()` ile sağlanır.
