# Teknik Mimari

## Mimari Yaklaşım

Mevcut uygulamadaki katmanlı yapı yeni proje için de uygundur:

- Domain.
- Infrastructure.
- Services.
- Controllers / ViewModels.
- Presentation.

Bu ayrım, PySide6 masaüstü uygulaması için temiz ve test edilebilir bir başlangıç sağlar.

## Önerilen Klasör Yapısı

```text
new_project_app/
  main.py
  config.py
  di_container.py
  domain/
    models/
    enums/
    exceptions/
  infrastructure/
    database/
      db_manager.py
      migrations/
    repositories/
    storage/
  services/
    dto/
    interfaces/
  controllers/
  presentation/
    shell/
    pages/
    widgets/
    dialogs/
  styles/
  resources/
  tests/
```

## Domain Katmanı

Sorumluluk:

- Varlık modelleri.
- Enum değerleri.
- Domain exception sınıfları.
- Basit domain davranışları.

Örnek modeller:

- `Project`
- `Idea`
- `ProjectStage`
- `Task`
- `ChecklistItem`
- `DecisionRecord`
- `Note`
- `Resource`
- `ActivityLog`

## Repository Katmanı

Sorumluluk:

- SQLite sorguları.
- Row -> domain model dönüşümü.
- CRUD işlemleri.
- Transaction gerektiren işlemler.

Önerilen repository'ler:

- `ProjectRepository`
- `IdeaRepository`
- `StageRepository`
- `TaskRepository`
- `ChecklistRepository`
- `DecisionRepository`
- `NoteRepository`
- `ResourceRepository`
- `ActivityLogRepository`

## Service Katmanı

Sorumluluk:

- Validasyon.
- İş kuralları.
- Birden fazla repository içeren aksiyonlar.
- Aktivite log üretimi.

Önerilen servisler:

- `ProjectService`
- `IdeaService`
- `WorkflowService`
- `TaskService`
- `DecisionService`
- `KnowledgeService`
- `DashboardService`

Örnek servis davranışları:

- Proje oluşturulunca varsayılan aşamaları yarat.
- Fikir projeye dönüştürülünce hem proje hem ilişki hem aktivite log yaz.
- Görev tamamlanınca checklist ve proje ilerlemesini güncelle.
- Aşama tamamlanınca sıradaki aşamayı aktif yap.

## Controller veya ViewModel Katmanı

Mevcut uygulama PySide6 Signal kullanan controller yapısına sahip. Yeni projede de bu yaklaşım kullanılabilir.

Sorumluluk:

- UI'dan gelen aksiyonları servise yönlendirmek.
- Başarı/ hata sinyalleri yaymak.
- Görünümlerin refresh akışını yönetmek.

Önerilen controller'lar:

- `ProjectController`
- `IdeaController`
- `TaskController`
- `DashboardController`
- `SettingsController`

Not:

- Proje detay ekranı çok büyürse tek `ProjectController` şişebilir. Bu nedenle görev, fikir ve karar aksiyonları ayrı controller'lara bölünmeli.

## Presentation Katmanı

PySide6 ile başlanırsa önerilen ekranlar:

- `MainWindow`
- `Sidebar`
- `DashboardPage`
- `ProjectsPage`
- `ProjectDetailPage`
- `IdeasPage`
- `TasksPage`
- `SettingsPage`

Önerilen widget'lar:

- `ProjectListItem`
- `ProjectSummaryHeader`
- `StageTimeline`
- `TaskCard`
- `ChecklistEditor`
- `IdeaCard`
- `DecisionCard`
- `ResourceList`
- `ActivityFeed`

## Sesli Komut (Speech-to-Text) Altyapısı — Uygulandı (2026-06-30)

Diğer bölümlerin aksine bu bir öneri değil, gerçekleştirilmiş bir mimari karardır.

Sorumluluk zinciri (UI → arka plan iş → servis), mevcut Worker desenine sadık kalır:

```
presentation/widgets/voice_input_button.py   (UI: toggle buton, QLineEdit/QTextEdit hedef)
  → core/workers/transcription_worker.py     (QRunnable + QThreadPool; sürekli ses döngüsü)
    → services/speech/speech_to_text_service.py  (Vosk model yaşam döngüsü, lazy yükleme)
      → vosk (tanıma motoru) + sounddevice (mikrofon yakalama)
```

Teknoloji kararı: **Vosk** (çevrimdışı, küçük Türkçe model) + **sounddevice**. Gerekçe:
internet/API anahtarı gerektirmeyen, ücretsiz, gizliliği koruyan (ses cihaz dışına çıkmaz)
bir çözüm; cloud STT alternatiflerine (Whisper API, Google Speech) göre kurulum sonrası
tamamen yerel çalışır.

Model `resources/models/vosk-model-small-tr-0.3/` altında tutulur, repoya dahil edilmez
(boyut), `app/config.py::VOSK_TR_MODEL_DIR` ile referans edilir. DI'a `ServiceRegistry`
üzerinden `@cached_property` ile lazy kaydedilir — uygulama açılışında model yüklenmez,
yalnızca ilk mikrofon kullanımında.

Hata yönetimi mevcut istisna deseniyle uyumlu: `core/exceptions/speech_exceptions.py`
(`SpeechModelNotFoundError`, `MicrophoneUnavailableError`) → UI'da toast, stack trace
kullanıcıya gösterilmez. Detay: `docs/wiki/sesli-komut.md`.

## Depolama

MVP için:

- SQLite.
- Migration sistemi.
- Yerel dosya depolama.
- JSON metadata sadece esnek alanlar için.

Kaçınılması gereken:

- Checklist gibi sorgulanabilir alanları JSON içinde saklamak.
- Aşama ve görev durumlarını serbest metin tutmak.

## Migration Stratejisi

Her şema değişikliği ayrı SQL dosyası olmalı:

```text
001_initial.sql
002_add_decision_records.sql
003_add_activity_logs.sql
```

Kural:

- Migration'lar idempotent olmalı.
- `schema_migrations` tablosu kullanılmalı.
- Test DB migration'ları otomatik koşmalı.

## Test Stratejisi

Öncelik:

- Service unit testleri.
- Repository integration testleri.
- Migration testleri.
- Kritik UI davranışları için sınırlı widget testleri.

Örnek testler:

- Boş başlıkla proje oluşturulamaz.
- Proje oluşturulunca varsayılan aşamalar oluşur.
- Fikir projeye dönüşünce bağlantı korunur.
- Checklist tamamlanınca görev ilerlemesi hesaplanır.
- Aşama tamamlanınca aktivite log yazılır.

## Teknoloji Seçimi

Mevcut uygulama PySide6 olduğu için en düşük riskli seçenek:

- Python.
- PySide6.
- SQLite.
- Pytest.

Alternatif:

- Web tabanlı ürün için FastAPI + React/Vue/Svelte.

Öneri:

- Eğer amaç mevcut masaüstü uygulama deneyimine yakın, hızlı prototip ise PySide6 ile devam et.
- Eğer amaç ileride ekip kullanımı ve web erişimi ise baştan web mimarisi düşün.

## MVP İçin Pratik Mimari Kararı

İlk sürüm:

- PySide6 masaüstü.
- SQLite yerel DB.
- Katmanlı mimari.
- Ayrı servisler.
- Basit tema sistemi.

İkinci faz:

- Export.
- Yedekleme.
- Web/API ayrımı.
- Senkronizasyon.

