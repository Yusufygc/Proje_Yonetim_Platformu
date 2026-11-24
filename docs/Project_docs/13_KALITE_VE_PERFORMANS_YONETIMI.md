# 13. Kalite, Performans ve Hata Yönetim Sistemleri

Bu doküman, "Proje Yönetim ve Takip Platformu"nun çökmeden çalışmasını, verimli bellek kullanmasını, hataları profesyonelce yakalamasını ve güvenilir bir şekilde test edilmesini sağlayacak altyapı standartlarını belirler.

---

## 1. Profesyonel Hata Yönetim Mekanizması (Error Handling)

Masaüstü uygulamalarında uygulamanın sessizce kapanması (crash) veya kullanıcıya anlamsız terminal hataları göstermesi kabul edilemez.

**Gereksinimler ve Çözüm:**
* **Global Exception Hook:** PySide6 uygulamasının en üst seviyesinde (`sys.excepthook` kullanılarak) yakalanamayan tüm hatalar (Unhandled Exceptions) yakalanacak. Uygulama çökmek yerine kullanıcıya "Beklenmeyen bir hata oluştu" diyalogu gösterecek ve hatanın detayını log dosyasına yazacaktır.
* **Custom Domain Exceptions (Özel Hata Sınıfları):** Python'ın standart hataları yerine iş kurallarına özel hatalar fırlatılacaktır.
  * Örn: `ProjectNotFoundError`, `TaskHierarchyError` (Bir görevi kendi altına taşımaya çalışırken), `DatabaseConnectionError`.
* **Kullanıcı Dostu UI Tepkileri:** Hata durumlarında uygulamanın donmasını engellemek için, uzun süren işlemler "try-except" bloklarına alınacak ve UI tarafında kullanıcının anlayacağı dilde, çözüm öneren bildirimler (Toast veya QMessageBox) gösterilecektir.

---

## 2. Merkezi Loglama Sistemi (Logging)

Sistemin ne zaman, nerede ve neden hata verdiğini geriye dönük izleyebilmek (Traceability) için profesyonel bir loglama modülü kurulacaktır.

**Gereksinimler ve Çözüm:**
* **Rolling File Appender:** Loglar tek bir dosyada şişmeyecektir. `logging.handlers.RotatingFileHandler` kullanılarak log dosyaları belirli bir boyuta (örn. 5MB) ulaştığında arşivlenip yeni dosyaya geçilecektir (Max 3 yedek).
* **Farklı Log Seviyeleri (Levels):**
  * `DEBUG`: Sadece geliştirme ortamında çalışacak detaylı algoritma adımları ve SQL sorguları.
  * `INFO`: Uygulamanın normal işleyişi (Uygulama açıldı, yeni proje oluşturuldu vb.).
  * `WARNING`: Kritik olmayan ama dikkat edilmesi gereken durumlar (Örn: İkon internetten indirilemedi, lokal cache kullanıldı).
  * `ERROR` / `CRITICAL`: Sistem hataları, veritabanı bağlantı kopmaları, UI çökmeleri.
* **Format:** Loglar `[Tarih-Saat] [Seviye] [Modül] - Mesaj` formatında standartlaştırılacaktır.

---

## 3. Test Mekanizması (Testing Strategy)

Katmanlı mimarinin getirdiği avantaj kullanılarak, ürünün her parçası bağımsız olarak test edilecektir.

**Gereksinimler ve Çözüm:**
* **Test Framework:** `pytest` kullanılacaktır. Hızlı ve okunabilir olması sebebiyle Python ekosisteminin standart test aracıdır.
* **Birim Testleri (Unit Tests):** Service katmanı (`ProjectService`, `TaskService`) ve algoritmalar veritabanından izole edilerek (Mock/MagicMock kullanılarak) test edilecektir.
  * *Örnek Test:* "Alt görevleri olan bir başlık tamamlandığında ilerleme %100 dönmelidir."
* **Entegrasyon Testleri (Integration Tests):** `Repository` katmanının SQLite ile doğru konuşup konuşmadığı, Memory (RAM) üzerinde çalışan geçici bir SQLite DB (`:memory:`) kurularak test edilecektir.
* **UI Testleri (Opsiyonel/Kritik Yollar):** `pytest-qt` kütüphanesi kullanılarak uygulamanın ana pencerelerinin render edilip edilmediği ve buton tıklama sinyallerinin doğru çalışıp çalışmadığı otomatik test edilecektir.

---

## 4. Bellek Maliyeti ve Optimizasyon (Memory Management)

PySide6, arka planda C++ nesneleri (QObject) kullanır. Bu nesnelerin bellekte asılı kalması (Memory Leak) uygulamanın zamanla RAM'i sömürmesine neden olur.

**Gereksinimler ve Çözüm:**
* **Parent-Child İlişkisi:** PySide6'da UI elementleri oluşturulurken muhakkak bir `parent` (ebeveyn) atanacaktır. Örneğin, bir detay penceresi açıldığında, ana pencere kapatılırsa detay penceresi de otomatik olarak bellekten silinmelidir (Garbage Collection).
* **Lazy Loading (Tembel Yükleme):** Arşivde 1000 tane proje varsa, uygulama açılır açılmaz hepsi belleğe yüklenmeyecektir. Projeler sayfa sayfa (Pagination) veya kullanıcı kaydırdıkça yüklenecektir.
* **Görsel Önbellekleme (Image Caching):** `QPixmap` ve SVG'ler bellekte tekrar tekrar oluşturulmayacak, `IconManager` vasıtasıyla tek bir referans üzerinden kullanılacaktır.

---

## 5. Algoritma Analizi ve Performans

Özellikle Hiyerarşik Görev Yönetimi (WBS) eklendiği için ağaç (Tree) algoritmalarının maliyetine dikkat edilmelidir.

**Gereksinimler ve Çözüm:**
* **N+1 Sorgu Probleminden Kaçınma:** 50 tane görev yüklerken 50 ayrı SQL sorgusu atmak yerine, `JOIN` kullanılarak veya tek bir `IN` sorgusu ile veriler toplu çekilecektir.
* **İlerlemeyi Hesaplama (O(N) Maliyeti):** Ağaç yapısındaki görevlerin genel tamamlanma yüzdesini hesaplarken rekürsif (kendi kendini çağıran) fonksiyonlar kullanılacaktır. Performans kaybını önlemek için ilerleme verisi, veritabanına yazılırken hesaplanıp kaydedilecek, ekran her çizildiğinde baştan hesaplanmayacaktır (Memoization/Caching).
* **Veritabanı İndeksleri (Indexes):** SQLite'ta en çok arama yapılan alanlara (örn: `project_id`, `parent_task_id`, `status`) sorgu performansını `O(N)`'den `O(log N)`'e düşürmek için DB seviyesinde index eklenecektir.
