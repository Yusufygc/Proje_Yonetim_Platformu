# 18. Proje İnşa Süreci ve Geliştirme Pipeline'ı

Bu doküman, tasarım ve planlama evresi (Faz 0) tamamlanan **Proje Yönetim ve Takip Platformu**'nun fiili kodlama sürecinin (Faz 1 ve sonrası) hangi adımlarla, hangi sırayla ve nasıl inşa edileceğini gösteren **adım adım geliştirme yol haritasıdır**.

Geliştiriciler ve otonom sistemler kodlamaya bu sırayı takip ederek başlamalıdır.

---

## ADIM 1: Geliştirme Ortamının ve Altyapının Hazırlanması
**Odak:** Projenin dış dünyayla olan bağlantılarını ve klasörlerini kurmak.

1. **Klasör Ağacının Oluşturulması:** `RULES.md` belgesinde belirtilen tüm dizinlerin (`core/`, `domain/`, `infrastructure/`, `services/`, `controllers/`, `presentation/`, `resources/`) yaratılması.
2. **Bağımlılıkların Yüklenmesi:** `pyproject.toml` üzerinden `poetry install` veya `uv pip install` komutu ile kilitli paketlerin (PySide6, SQLAlchemy, Alembic, vb.) sanal ortama kurulması.
3. **Alembic Başlangıcı:** Terminalden `alembic init infrastructure/migrations` komutu çalıştırılarak veritabanı göç (migration) iskeletinin oluşturulması. `alembic.ini` dosyasının SQLite kullanacak şekilde ayarlanması.
4. **Git İlklemesi:** `.gitignore`, `.claudeignore` ve `.graphifyignore` dosyaları eklenerek `git init` yapılması ve `Initial commit`'in atılması.

---

## ADIM 2: Çekirdek (Core) ve Ortak Yöneticilerin Kodlanması
**Odak:** Uygulamanın her yerinde kullanılacak olan merkezi araçların (Singleton/Factory) hazırlanması.

1. **Yapılandırma:** `config.py` içine veritabanı yolları ve sabitlerin (ENV ayarları) tanımlanması.
2. **Loglama:** `core/managers/log_manager.py` oluşturulup sistem hatalarını yakalayacak `sys.excepthook` mekanizmasının `main.py`'ye bağlanması.
3. **Temel Kaynak Yöneticileri:** - `ThemeManager` (Renk paletleri ve QSS üreticisi)
   - `IconManager` (İnternetten SVG çeken ve boyayan sistem)
   - `FontManager` (Lokal fontları `QFontDatabase` ile yükleyen yapı)
   - `PreferenceManager` (`QSettings` ile pencere boyutlarını kaydeden sistem)
4. **Olay Otobüsü:** `core/events/event_bus.py` oluşturularak Pub/Sub (Yayınla/Abone Ol) altyapısının kodlanması.

---

## ADIM 3: Veritabanı ve Domain Modellerinin İnşası (Data Layer)
**Odak:** Veritabanının platform bağımsız şekilde ayağa kaldırılması ve şemaların çizilmesi.

1. **Bağlantı Motoru:** `infrastructure/database/db_manager.py` kodlanarak `scoped_session` altyapısının kurulması.
2. **Base Model:** Tüm modellerin türetileceği `DeclarativeBase` ve ortak alanların (`created_at`, `updated_at`) yazılması.
3. **Modellerin Kodlanması (Sırayla):**
   - `Project` ve `ProjectTag` (En temel tablo)
   - `WorkflowStage` (Süreç şablonları)
   - `Task` (WBS - Kendi kendine referans veren `parent_task_id` yapısıyla)
   - Diğerleri: `Idea`, `DecisionRecord`, `Note`, `ActivityLog`.
4. **İlk Migration:** Modeller yazıldıktan sonra `alembic revision --autogenerate -m "init_schema"` ile ilk göç dosyasının oluşturulması ve `alembic upgrade head` ile `.db` dosyasının yaratılması.

---

## ADIM 4: Veri Erişimi ve İş Kuralları (Repository & Service)
**Odak:** Uygulamanın beyni olan iş mantığının ve SQL soyutlamalarının yazılması.

1. **Repository'ler:** `ProjectRepository` ve `TaskRepository` başta olmak üzere, veri tabanına CRUD yapan SQLAlchemy metodlarının yazılması.
2. **DTO Katmanı (Data Transfer Objects):** UI'dan servise gidecek verileri doğrulayan Pydantic veya Dataclass nesnelerinin oluşturulması.
3. **Service'ler:** İş mantığının (`ProjectService`, `TaskService`) yazılması.
   - *Kritik İşlev:* Görev ağacında (WBS) ilerleme yüzdesini yukarı doğru hesaplayan (Roll-up) algoritmanın kodlanması.
4. **Birim Testleri (Unit Tests):** Yazılan servislerin ve algoritmaların, `pytest` ve `:memory:` veritabanı kullanılarak test edilmesi.

---

## ADIM 5: Ana Arayüz İskeleti ve Controller Bağlantıları (UI Shell)
**Odak:** Kullanıcının göreceği ana pencerenin, menülerin ve modern UI hissinin ayağa kaldırılması.

1. **Dependency Injection (DI):** `di_container.py` kodlanarak servislerin, yöneticilerin ve repository'lerin birbirine bağlanması (Wiring).
2. **Ana Pencere:** `presentation/shell/main_window.py` oluşturulması. Özel pencere kenarlıkları (Custom Titlebar), gölgelendirmeler ve köşe yumuşatmalarının uygulanması.
3. **Sidebar (Menü):** QPropertyAnimation ile daralan/genişleyen modern yan navigasyon menüsünün tasarlanması.
4. **Controller'lar:** `BaseController` ve temel sayfa controller'larının sinyal/slot (pyqtSignal) iletişim altyapılarının kurulması.

---

## ADIM 6: Sayfalar, Etkileşimler ve Asenkron İşlemler
**Odak:** Alt sayfaların (Dashboard, Projeler, Görevler) oluşturulup veriyle doldurulması.

1. **Asenkron Worker:** `core/workers/async_worker.py` oluşturularak, veritabanından çekilecek uzun listelerin GUI'yi dondurmasının engellenmesi.
2. **Projeler Sayfası:** Sol liste ve sağ detay ekranının, `ProjectController` ile bağlanarak çalışır hale getirilmesi.
3. **Görevler WBS Ekranı:** `QTreeView` kullanılarak hiyerarşik görev ağacının çizilmesi, satır içi (inline) ekleme fonksiyonunun entegrasyonu.
4. **Etkileşimler:** Sürükle-bırak (Drag & Drop), Focus Ring ve global klavye kısayollarının sisteme eklenmesi.

---

## ADIM 7: Cila, Hata Kurtarma ve UX Dokunuşları
**Odak:** Uygulamayı "çalışan bir kottan" "premium bir ürüne" dönüştürmek.

1. **Empty States:** Hiç proje yokken çıkacak illüstrasyonların ve Onboarding (Örnek proje yükleme) ekranlarının eklenmesi.
2. **Geri Bildirim:** Skeleton loading (veri yüklenirken gri iskelet animasyonları) ve işlemler sonrası çıkan Toast/Snackbar (Undo/Geri al) mesajlarının kodlanması.
3. **Arayüz Optimizasyonu:** Custom Scrollbar (özel kaydırma çubukları) ve metin kırpma (Tooltip) özelliklerinin aktif edilmesi.

---

## ADIM 8: Stabilizasyon, Build ve Dağıtım
**Odak:** Ürünü paketleyip son kullanıcıya hazır hale getirmek.

1. **Entegrasyon Testleri:** UI testlerinin `pytest-qt` ile koşturulması ve tüm akışın denenmesi.
2. **Code Review & Linting:** `ruff` ve `mypy` ile tüm projenin formatlanması ve tip hatalarının giderilmesi.
3. **Paketleme:** `pyinstaller` veya `nuitka` kullanılarak uygulamanın tek bir klasör veya `.exe` haline getirilmesi. (Terminal penceresinin gizlenmesi `--noconsole`).
4. **Kurulum Sihirbazı:** Inno Setup veya NSIS ile bir yükleyici oluşturularak Faz 1 (MVP) sürümünün tamamlanması.
