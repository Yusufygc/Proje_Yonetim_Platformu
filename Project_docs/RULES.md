# Geliştirme Standartları ve Kuralları (RULES.md)

Bu doküman, **Proje Yönetim ve Takip Platformu** projesinde geliştirilecek tüm kodların mimari kalitesini, sürdürülebilirliğini, güvenliğini ve ekip/kod bütünlüğünü korumak adına uyulması zorunlu olan kuralları tanımlar. Projede çalışacak tüm geliştiriciler (ve yapay zeka asistanları/ajanları) bu kurallara kayıtsız şartsız uymakla yükümlüdür.

çalışma ortamı : C:\Users\ysfygc\anaconda3\envs\projeTakip kurulumlar ve testler bu ortamda yapılacak 
---

## 1. Kodlama ve Temiz Kod (Clean Code) Prensipleri

* **Anlamlı ve Kendini Açıklayan İsimlendirmeler:** Değişken, fonksiyon ve sınıf isimleri kısaltma içermemeli, ne iş yaptıklarını açıkça belli etmelidir. (Örn: `p` yerine `project_id`, `get_data()` yerine `fetch_active_projects()`).
* **Küçük ve Odaklanmış Fonksiyonlar:** Bir fonksiyon veya metod yalnızca tek bir işi yapmalıdır (Single Responsibility). Fonksiyon satır sayısı ideal olarak 20-25 satırı geçmemelidir.
* **Koşul ve Döngü Optimizasyonları:** İçi içe geçmiş karmaşık `if-else` bloklarından (Arrow Anti-Pattern) kaçınılmalıdır. Guard Clauses (erken dönüş/return) yaklaşımı benimsenmelidir.
* **Yazı Renkleri ve UI Kontrast Standartları:** PySide6 arayüz tasarımlarında kesinlikle okunamayacak seviyede soluk, opaklığı çok düşük veya arka plana yakın gri tonlarında metin renkleri kullanılmamalıdır. Dark ve Light temalarda metin-arka plan kontrast oranı en üst seviyede tutulmalıdır.

---

## 2. Mimari, OOP, SOLID ve Tasarım Kalıpları (Design Patterns)

* **SOLID Prensiplerine Tam Uyum:**
    * **S (Single Responsibility):** Görsel bileşenler (Presentation/Widget) kesinlikle SQL sorgusu yazmamalı veya doğrudan iş kuralı işletmemelidir. Business logic servis katmanında olmalıdır.
    * **O (Open/Closed):** Mevcut sınıfların kaynak kodunu değiştirmeden, kalıtım (inheritance) veya arayüzler (interfaces) aracılığıyla yeni özellikler eklenebilmelidir.
    * **L (Liskov Substitution):** Alt sınıflar, türetildikleri üst sınıfların davranışlarını bozmamalıdır.
    * **I (Interface Segregation):** Sınıflar, kullanmadıkları metodları içeren devasa arayüzleri implement etmeye zorlanmamalıdır.
    * **D (Dependency Inversion):** Katmanlar birbirine sıkı sıkıya (tightly coupled) bağlı olmamalıdır. Bağımlılıklar `di_container.py` (Dependency Injection) üzerinden yönetilmelidir.
* **Tasarım Kalıpları (Design Patterns):** * Veritabanı işlemleri için **Repository Pattern**,
    * İş kuralları yönetimi için **Service Pattern**,
    * Arayüz ve arka plan haberleşmesi için Qt sinyallerini kullanan **Controller/ViewModel Pattern**,
    * Merkezi yönetimler için (Tema, İkon, Font) **Singleton veya Factory Pattern** kullanılmalıdır.
* **Modülerlik ve "Tak-Çıkar" Mimarisi:** Yeni bir modül veya özellik eklenirken mevcut sınıflarda yapısal değişiklik gerektirmemeli; arayüzler ve PySide6 sinyal/slot mekanizmaları (Loose Coupling) sayesinde sisteme bir eklenti gibi entegre edilebilmelidir.

---

## 3. "God Object" Önleme ve Dosya Düzeni Kuralı

* **Şişen Dosya Yasağı:** Tek bir sınıfın veya dosyanın tüm uygulamanın yükünü üstlenmesine (God Object) kesinlikle izin verilmez. `ProjectController` veya `MainWindow` gibi sınıflar büyüdüğünde alt bileşenlere ve alt controller'lara (Örn: `TaskController`, `IdeaController`, `DecisionController`) bölünmelidir.
* **Dosya Başına Sınır:** Bir Python dosyasının toplam satır sayısı 400 satırı, bir sınıfın metod sayısı ise 15'i geçmemelidir. Bu sınırlara yaklaşıldığında refactoring zorunludur.

---

## 4. Dokümantasyon ve Yorum Satırları

* **Açıklayıcı Yorumlar (Yorum Satırları):** Kodun *ne* yaptığını değil, kodun *neden* o şekilde yazıldığını (iş kuralının arkasındaki mantığı) açıklayan yorum satırları eklenmelidir.
* **Docstring Standardı:** Her sınıf, metod ve fonksiyonun başında Google veya Sphinx formatında Docstring bulunmalıdır. Parametrelerin tipleri ve dönüş (return) değerleri açıkça belirtilmelidir.
* **Örnek:**
    ```python
    def convert_idea_to_project(self, idea_id: int) -> int:
        """
        Onaylanmış bir fikri resmi bir projeye dönüştürür.
        
        Fikrin durumunu 'CONVERTED' yapar ve referans ID'leri bağlar.
        İşlem başarısız olursa IdeaHierarchyError fırlatır.
        """
    ```

---

## 5. Güvenlik ve Bellek Yönetimi Kuralları

* **Veritabanı Güvenliği:** SQLite sorgularında string birleştirme (`+` veya f-string) kesinlikle yasaktır. Tüm sorgular SQL enjeksiyonuna karşı parametrik (`?` syntax'ı) olmalıdır.
* **Bellek Maliyeti ve Nesne Yönetimi:** PySide6 arayüz elemanları oluşturulurken `parent` parametresi boş bırakılmamalıdır. Pencere kapandığında bellekten temizlenmesi (Garbage Collection) için C++ nesne hiyerarşisi eksiksiz kurulmalıdır.
* **Lazy Loading:** Listeleme ve ağaç yapılarında (WBS) binlerce veri aynı anda RAM'e basılmamalı, kaydırdıkça yükleme (pagination/lazy load) kurgulanmalıdır.

---

## 6. Sürüm Kontrolü ve Commit Standartları

* **Türkçe Karakter ve Dil Kuralları:** Commit mesajları tamamen Türkçe dil kurallarına uygun, imla ve Türkçe karakterlere (`ç, g, ı, ö, ş, ü`) dikkat edilerek yazılmalıdır.
* **Dosyaya Özel ve Kapsamlı Açıklama:** Jenerik mesajlar (Örn: "güncelleme yapıldı", "fix", "kodlar eklendi") kesinlikle yasaktır. Commit mesajı, o commit dahilinde değiştirilen her kritik dosyaya ve yapılan yapısal değişikliğe özel, kapsamlı açıklamalar içermelidir.
* **Yapay Zeka (AI) Referans Yasağı:** Commit mesajlarında veya kod açıklamalarında asla "Yapay zeka tarafından düzenlendi", "AI asistanı kodu", "Prompt sonucu eklendi" gibi AI referansları, araç isimleri veya prompt ipuçları yer almayacaktır. Tüm commitler doğrudan insan yazmış gibi kurumsal bir dille atılacaktır.
* **Örnek Format:**
    ```text
    feat(project_service): Proje oluşturma iş kurallarına boş başlık doğrulaması eklendi

    - project_service.py dosyasına boş başlık girdilerini engelleyen doğrulama mantığı entegre edildi.
    - Boş başlık durumunda fırlatılacak ProjectValidationError sınıfı exceptions.py dosyasına tanımlandı.
    - Proje başarıyla kaydedildiğinde çalışacak otomatik süreç aşaması şablon kopyalama mekanizması eklendi.
    ```

---

## 7. Süreç Takip ve Dosya Entegrasyon Kuralları (Graphify & Claude/Agents)

* **Graphify Güncellemesi:** Projenin modül bağımlılıklarını, mimari şemasını veya süreç akışını etkileyen herhangi bir yapısal değişiklik, veritabanı şema güncellemesi (migration) ya da yeni katman eklemesi sonrasında projeye ait bağımlılık grafikleri ve `graphify` mimari haritası anında güncellenecektir. Mimari şema ile mevcut kod tabanı asla çelişmemelidir.
* **CLAUDE.md ve AGENTS.md Protokolü:** Proje dizininde yer alan `CLAUDE.md` veya `AGENTS.md` dosyalarındaki geliştirme ortamı komutlarına, test çalıştırma protokollerine ve otomatik ajan kurallarına mutlak suretle uyulacaktır. Ajanlar veya asistanlar kod üretmeden önce bu dosyalardaki güncel state'i, bağımlılıkları ve kısıtlamaları okumak ve harfiyen işletmekle yükümlüdür.
* **Dokümantasyon Güncelleme Zorunluluğu:** Yeni bir özellik eklendiğinde veya mevcut davranış değiştirildiğinde aşağıdaki belgeler aynı commit kapsamında güncellenmelidir; güncellenmemişse commit kabul edilmez:
    * `README.md` — Özellikler, kullanım talimatları veya ekran görüntüleri bölümü.
    * `docs/wiki/` — Değişikliği ilgilendiren wiki sayfası (yoksa yeni sayfa oluşturulur).
    * `Project_docs/` — Etkilenen modül veya mimari dokümanı.
    * Uygulama içi **Bilgilendirme / Hakkında** sayfası (varsa) — Sürüm notu veya özellik listesi.
