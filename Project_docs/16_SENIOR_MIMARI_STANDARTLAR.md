# 16. Senior Mimari ve Mühendislik Standartları

Bu doküman, **Proje Yönetim ve Takip Platformu** projesinin kurumsal düzeyde kararlılığa, yüksek performansa, asenkron çalışma kabiliyetine ve sıfır teknik borç (zero technical debt) hedefine ulaşması için uyulması zorunlu olan ileri düzey mimari kuralları tanımlar.

---

## 1. Asenkron UI ve İş Parçacığı Yönetimi (Worker Pattern)

PySide6 (Qt) mimarisinde arayüz elemanlarının çizimi ve kullanıcı etkileşimleri tek bir ana iş parçacığı (**Main/GUI Thread**) üzerinden yürütülür. Kullanıcı deneyiminin (Premium UI/UX) kesintiye uğramaması ve uygulamanın "Yanıt Vermiyor" (Not Responding) konumuna düşmemesi için katı iş parçacığı izolasyonu uygulanacaktır.

### Kurallar ve Standartlar:
* **UI Thread Kilitleme Yasağı:** 50ms'den uzun süren hiçbir işlem (veritabanı okuma/yazma, disk I/O, internetten ikon indirme, hiyerarşik ilerleme hesaplama) doğrudan Controller veya Presentation katmanında (Main Thread üzerinde) çalıştırılamaz.
* **Worker Altyapısı:** Ağır işlemler için `QThreadPool` ve `QRunnable` (veya `QThread`) tabanlı asenkron yapılar kullanılacaktır.
* **Sinyal Tabanlı Haberleşme:** Arka planda çalışan iş parçacıkları (Workers), UI bileşenlerine doğrudan erişemez veya onları değiştiremez. Veri aktarımı ve arayüz güncellemeleri yalnızca Qt Sinyalleri (`pyqtSignal`) üzerinden gerçekleştirilecektir.

---

## 2. Olay Güdümlü İletişim Mimarisi (Event Bus Pattern)

Modüller ve denetleyiciler (Controllers) arasındaki bağımlılıkları en aza indirmek (Loose Coupling) ve "Tak-Çıkar" mimarisini güvenceye almak için merkezi bir olay mekanizması işletilecektir.

### Kurallar ve Standartlar:
* **Doğrudan Çağrı Yasağı:** Bir modülde gerçekleşen olay, başka bir modülü doğrudan tetiklememelidir. (Örn: `TaskController` bir görevi tamamladığında, `DashboardController`'ın metodunu doğrudan çağıramaz).
* **Yayınla/Abone Ol (Pub/Sub):** Tüm katmanlar arası küresel etkileşimler `core/events/event_bus.py` üzerinden yürütülecektir.
    * Olayı gerçekleştiren modül sinyali yayınlar (**Publish**).
    * Olayla ilgilenen diğer bağımsız modüller bu olayı dinler (**Subscribe**) ve kendi iç durumlarını günceller.
* **Örnek Akış:** `TaskService` bir görevi bitirdiğinde Event Bus üzerinden `TaskCompletedEvent` yayınlar. `DashboardService` bu olayı yakalayarak istatistikleri günceller; `ActivityLogService` ise aktivite geçmişine yazar.

---

## 3. Katı Tip Güvenliği ve Veri Transfer Nesneleri (Strict Typing & DTOs)

Python'ın dinamik yapısından kaynaklanabilecek çalışma zamanı (Runtime) hatalarını engellemek ve kod tabanını statik analiz araçlarına uyumlu hale getirmek için katı tip kuralları geçerlidir.

### Kurallar ve Standartlar:
* **Strict Type Hinting:** Yazılan tüm fonksiyon, metod ve değişken tanımlamalarında tip belirtimleri eksiksiz yapılacaktır (Örn: `def fetch_project(self, project_id: int) -> Optional[Project]:`). Tip belirtimi içermeyen kodlar CI/CD veya pre-commit aşamasında reddedilecektir.
* **DTO (Data Transfer Object) Katmanı:** UI katmanından gelen form verileri veya dış kaynak girdileri doğrudan servis katmanına veya SQLAlchemy modellerine çıplak olarak aktarılamaz.
* **Validasyon:** Girdiler önce Pydantic veya Dataclasses tabanlı DTO nesnelerine dönüştürülerek doğrulanacak (Validation), ardından iş mantığına dahil edilecektir.

---

## 4. Modern Bağımlılık ve Ortam Yönetimi

Projenin farklı geliştirme, test ve dağıtım ortamlarında %100 aynı kararlılıkta çalışmasını sağlamak için kütüphane bağımlılıkları sıkı bir şekilde kilitlenecektir.

### Kurallar ve Standartlar:
* **Paket Yönetimi:** Klasik `requirements.txt` yerine **Poetry** veya **uv** tabanlı deterministik paket yöneticileri kullanılacaktır.
* **Kilit Dosyası (Lock File):** Proje bağımlılıkları `pyproject.toml` üzerinden tanımlanacak ve alt bağımlılıkların sürümlerini sabitleyen `poetry.lock` (veya `uv.lock`) dosyası kesinlikle sürüm kontrol sistemine (Git) dahil edilecektir. Kurulumlar her zaman `poetry install --sync` ile yapılacaktır.

---

## 5. Statik Analiz, Linting ve Pre-commit Otomasyonu

Clean Code standartlarının kişisel yorumlardan bağımsız olarak korunması amacıyla otomatik denetim mekanizmaları kurulacaktır.

### Kurallar ve Standartlar:
* **Ruff & Mypy Entegrasyonu:** Kod formatlama, stil hatalarının tespiti (linting) ve tip doğrulamaları için **Ruff** ve **Mypy** araçları kullanılacaktır. PEP 8 standartları otomatik olarak dayatılacaktır.
* **Pre-commit Kancaları (Hooks):** Git commit işlemi tetiklendiğinde yerel bilgisayarda pre-commit scriptleri otomatik olarak çalışacaktır. Kod formatı hatalı olan veya statik analiz testlerinden (Mypy tip kontrolü dahil) geçemeyen hiçbir değişiklik commit edilemez.
