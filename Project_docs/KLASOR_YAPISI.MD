proje_takip_platformu/
│
├── main.py                     # Uygulama giriş noktası (bootstrap ve global exception hook)
├── config.py                   # Uygulama sabitleri, yol tanımları ve çevre değişkenleri
├── di_container.py             # Katmanlar arası Dependency Injection (Wiring) merkezi
├── alembic.ini                 # Alembic veritabanı göç konfigürasyonu
│
├── core/                       # Çekirdek yardımcı sistemler ve yöneticiler
│   ├── __init__.py
│   ├── exceptions/             # Özelleştirilmiş iş kuralı hata sınıfları
│   │   ├── base_exception.py
│   │   ├── project_exceptions.py
│   │   └── task_exceptions.py
│   └── managers/               # Merkezi kaynak ve sistem yöneticileri (Singleton/Factory)
│       ├── icon_manager.py     # İnternetten SVG indirme, önbellekleme ve renklendirme
│       ├── theme_manager.py    # Dark/Light palet yönetimi ve QSS (Style) dinamik üretimi
│       ├── font_manager.py     # QFontDatabase ile lokal font gömme işlemleri
│       ├── string_manager.py   # strings.tr.json üzerinden i18n metin dağıtımı
│       ├── preference_manager.py # QSettings ile pencere boyutu, son seçili proje kaydı
│       ├── log_manager.py      # RotatingFileHandler ile 5MB sınırında log rotasyonu
│       └── backup_manager.py   # Uygulama açılışında .backups altına DB yedekleme
│
├── domain/                     # Saf iş modelleri ve kuralları (Framework/Kütüphane Bağımsız)
│   ├── __init__.py
│   ├── models/                 # SQLAlchemy veri modelleri ve iş nesneleri
│   │   ├── project.py          # Proje varlığı
│   │   ├── task.py             # WBS destekli (parent_task_id içeren) hiyerarşik görev varlığı
│   │   ├── idea.py             # Projeye dönüştürülebilir fikir varlığı
│   │   ├── decision.py         # Teknik karar kayıtları (ADR)
│   │   ├── note.py             # Proje serbest metin notları
│   │   ├── resource.py         # Linkler ve referans kaynakları
│   │   └── activity_log.py     # Geriye dönük ters kronolojik aktivite log modeli
│   └── enums/                  # Tip güvenliği sağlayan İngilizce enum tanımları
│       ├── project_status.py   # PLANNED, ACTIVE, BLOCKED, ARCHIVED vb.
│       ├── task_status.py      # TODO, IN_PROGRESS, WAITING, DONE, BLOCKED vb.
│       ├── task_type.py        # GROUP, TASK, BUG, RESEARCH, DESIGN vb.
│       └── priority.py         # LOW, MEDIUM, HIGH, CRITICAL
│
├── infrastructure/             # Veri tabanı erişimi ve dış kaynak persistency katmanı
│   ├── __init__.py
│   ├── database/
│   │   ├── base_model.py       # SQLAlchemy Base (DeclarativeBase) sınıfı
│   │   └── db_manager.py       # Scoped_session üreten agnostik DB bağlantı yöneticisi
│   ├── migrations/             # Alembic tarafından üretilen otomatik göç versiyonları
│   └── repositories/           # ham SQL içermeyen, SQLAlchemy tabanlı CRUD sınıfları
│       ├── project_repository.py
│       ├── task_repository.py
│       ├── idea_repository.py
│       └── activity_repository.py
│
├── services/                   # İş kuralları, validasyonlar ve matematiksel hesaplamalar
│   ├── __init__.py
│   ├── project_service.py      # Proje CRUD kuralları, boş başlık validasyonu
│   ├── task_service.py         # WBS alt görev rollup (ilerleme yüzdesi yukarı taşıma) hesaplama
│   ├── idea_service.py         # Fikri projeye dönüştürme ve log tetikleme kuralları
│   └── dashboard_service.py    # İstatistik kartları, tıkalı iş verileri toplama mantığı
│
├── controllers/                # PySide6 Sinyal/Slot mekanizmasını yöneten ViewModel katmanı
│   ├── __init__.py
│   ├── base_controller.py      # Ortak refresh sinyallerini barındıran üst sınıf
│   ├── project_controller.py   # Proje ekranı arayüz tetikleyicileri
│   ├── task_controller.py      # Ağaç yapısı arayüz sinyal/slot yönetimi
│   └── dashboard_controller.py # İstatistik verilerini UI'a besleyen sinyaller
│
├── presentation/               # PySide6 Arayüz Bileşenleri (Yalnızca görsel mantık)
│   ├── __init__.py
│   ├── shell/                  # Ana uygulama pencereleri ve iskelet düzeni
│   │   ├── main_window.py      # Ana form penceresi
│   │   └── sidebar.py          # QPropertyAnimation ile daralan premium sol menü
│   ├── pages/                  # Sidebar'dan geçiş yapılan ana sayfalar
│   │   ├── dashboard_page.py   # İstatistik kartları ve hızlı fikir kutusu barındıran ekran
│   │   ├── projects_page.py    # Sol liste + sağ detay görünümlü çalışma merkezi
│   │   └── ideas_page.py       # Kart tasarımlı fikir havuzu ekranı
│   ├── widgets/                # Yeniden kullanılabilir premium görsel bileşenler
│   │   ├── task_tree_widget.py # QTreeView tabanlı hiyerarşik görev ağacı widget'ı
│   │   ├── gradient_button.py  # qlineargradient içeren yumuşak geçişli buton
│   │   └── status_badge.py     # Yüksek kontrastlı, yuvarlatılmış durum rozeti
│   └── dialogs/                # Açılır modal pencereler
│       ├── project_dialog.py   # Yeni proje ekleme / düzenleme modalı
│       └── task_dialog.py      # Görev detay ve checklist düzenleme modalı
│
├── resources/                  # Uygulama içi statik dosyalar ve yerel kaynaklar
│   ├── icons/                  # İndirilen ve çalışma zamanı renklendirilen SVG ikonlar
│   ├── fonts/                  # Gömülü (Embedded) modern font dosyaları (örn: Inter-Regular.ttf)
│   ├── themes/                 # Renk palet sözlükleri
│   │   ├── dark.json           # Premium yüksek kontrastlı koyu tema paleti
│   │   └── light.json          # Göz yormayan soft açık tema paleti
│   └── locales/                # i18n dil haritaları
│       └── strings.tr.json     # Uygulamanın tüm Türkçe string ifadeleri
│
└── tests/                      # Pytest otomatik test suite katmanı
    ├── __init__.py
    ├── conftest.py             # RAM üzerinde çalışan test veritabanı fixture tanımları
    ├── unit/                   # Servis katmanı bağımsız unit testleri
    │   └── test_task_rollup.py # WBS ilerleme algoritması unit testi
    └── integration/            # Repository ve DB entegrasyon testleri
        └── test_project_repo.py