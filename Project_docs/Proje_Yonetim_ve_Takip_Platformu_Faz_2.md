# Proje Yönetim ve Takip Platformu - Faz 2 Planlaması

Bu doküman, MVP (İlk Sürüm) planlamasındaki "Faz 2: Proje Yönetimi" geliştirme adımlarını ve MVP sonrasına bırakılan "İkinci Faz (Post-MVP)" gereksinimlerini detaylandırır. 

Ürün İsmi: **Proje Yönetim ve Takip Platformu**

## 1. Onaylanan Temel Kararların Özeti

Tasarım netleştirme aşamasında (Faz 0) aşağıdaki kararlar kilitlenmiştir:
* **Uygulama Türü:** PySide6 masaüstü uygulaması.
* **Kullanıcı Modeli:** MVP'de tek kullanıcı, veri modelinde ilerisi için ekip esnekliği.
* **Fikir Yönetimi:** Fikirler ayrı bir varlık (entity) olarak yönetilecek.
* **Tasarım Kayıtları:** Ayrı bir modül yerine görev, karar ve ek (attachment) olarak eritilecek.
* **İlerleme Hesabı:** Görev tamamlanma oranından otomatik hesaplama ve manuel override imkanı.
* **Süreç:** Tüm projeler tek varsayılan süreçle başlayacak (Fikir, Analiz, Tasarım, Geliştirme, Test, Yayın, Tamamlandı).
* **Silme Politikası:** Birincil yöntem "Arşivleme", ikincil yöntem onaylı "Kalıcı Silme".
* **Dosya Ekleri:** İlk sürümde URL (Link) eklenecek, yerel dosya ekleri ikinci faza bırakılacak.
* **Dışa Aktarma (Export):** MVP sonunda Markdown export, ikinci fazda PDF/DOCX.
* **Dil:** UI tamamen Türkçe, kod içi enum değerleri İngilizce.

---

## 2. MVP - Faz 2: Proje Yönetimi Geliştirme Detayları

Bu aşama, uygulamanın temel CRUD işlemlerinin yapıldığı ve ana proje döngüsünün ayağa kaldırıldığı kısımdır.

### Geliştirilecek Modeller ve Katmanlar
* **Domain Modeli:** `Project` sınıfının oluşturulması (id, title, description, status, priority, progress_percent vb.).
* **Repository:** `ProjectRepository` üzerinden SQLite tabanlı CRUD işlemlerinin yazılması.
* **Service:** `ProjectService` oluşturularak iş kurallarının (boş başlık kontrolü, otomatik ilerleme hesaplama, arşivleme mantığı) eklenmesi.
* **Controller:** `ProjectController` ile arayüz sinyallerinin (Signal/Slot) servise bağlanması.

### Geliştirilecek Ekranlar (UI)
* **Projeler Sayfası (Liste):** Sol panelde projelerin listelenmesi, arama ve durum/öncelik filtreleme kutuları.
* **Proje Oluşturma/Düzenleme Dialogu:** Başlık, kısa açıklama, öncelik ve durum gibi bilgilerin girileceği form.
* **Proje Detay Ekranı:** Seçili projenin sağ/orta panelde özet bilgilerinin ve ilerleme barının (progress bar) gösterilmesi.

### Kabul Kriterleri (Faz 2 İçin)
- [ ] Kullanıcı yeni bir proje oluşturabilmelidir (Başlıksız kayıt engellenmelidir).
- [ ] Oluşturulan proje sol listede anında güncellenerek görünmelidir.
- [ ] Kullanıcı mevcut bir projeyi düzenleyebilmelidir.
- [ ] Kullanıcı bir projeyi arşivleyebilmeli ve arşivlenen proje aktif listeden düşmelidir.
- [ ] Silme işlemi öncesi kullanıcıdan kesin onay istenmelidir.

---

## 3. İkinci Faz (MVP Sonrası) Gereksinimleri

Tasarım aşamasında ilk sürüme dahil edilmeyip, başarılı bir MVP sonrası geliştirilecek özellikler:

* **Çoklu Kullanıcı ve Ekip Desteği:** Veritabanındaki `users`, `assignees` ve `comments` tablolarının aktif edilerek takım çalışmasına uygun hale getirilmesi.
* **Gelişmiş Dosya Yönetimi:** Bilgisayardaki yerel dosyaların ve görsellerin uygulamaya yüklenmesi (Attachments).
* **Gelişmiş Export (Dışa Aktarım):** Proje çıktılarının, süreç geçmişinin ve kararların profesyonel formatlarda (PDF ve DOCX) raporlanması.
* **Gelişmiş Görünümler:** Görevler için Kanban tahtası ve süreç takibi için Takvim/Gantt çizelgesi görünümleri.
* **Otomatik Proje Sağlığı:** İlerlemeye, tıkanan görevlere ve teslim tarihlerine bakarak proje sağlığının (`GOOD`, `AT_RISK`, `BLOCKED`) otomatik hesaplanması.
* **Web/Cloud Entegrasyonu:** Masaüstü uygulamasının bulut ile senkronize çalışması veya bir web paneline bağlanması.
