# Otonom Ajan Protokolleri (AGENTS.md)

Bu doküman, projede görev alacak otonom yazılım ajanları, CI/CD pipeline scriptleri ve otomatik kod üreticileri için kesin davranış sınırlarını belirler. Otonom ajanlar, bu repository üzerinde işlem yaparken aşağıdaki yaşam döngüsüne ve `RULES.md` kurallarına uymak zorundadır.

## 1. İşlem Öncesi Durum (State) Kontrolü
- Kod yazmaya başlamadan önce mevcut mimariyi anlamak için `graphify` çıktılarını ve `RULES.md` dosyasını analiz et.
- Ortam bağımlılıklarının (`requirements.txt` / sanal ortam) tam yüklendiğinden ve `pytest` testlerinin mevcut durumda başarılı olduğundan emin ol. Hatalı (failing) bir state üzerine yeni özellik inşa etme.

## 2. Geliştirme Sınırları ve Kuralları
- **Modülerlik:** Değişiklik yapacağın dosyanın satır sayısını kontrol et. Dosya `400` satıra yaklaştıysa otonom olarak refactoring sürecini başlat ve modülü parçala (Örn: `project_controller.py` dosyasını `task_controller.py` ve `idea_controller.py` olarak ayır).
- **Veritabanı Müdahalesi:** SQLite veritabanı dosyasına doğrudan müdahale etme. Tüm veri modeli güncellemelerini `Alembic` kullanarak `alembic revision -m "degisiklik_adi"` komutuyla oluştur ve uygula.
- **Enjeksiyon:** Sınıflar arası bağımlılıkları hardcode etme. Her zaman projede bulunan Dependency Injection (DI) konteyneri üzerinden servisleri çağır.

## 3. Test ve Doğrulama
- Yaptığın değişiklikler sonrasında sistemi kendi kendine test et. Service katmanında yaptığın mantıksal değişiklikler için `pytest` kullanarak unit testler yaz veya mevcut testleri güncelle.
- PySide6 UI testlerinde uygulamanın çökmediğini (crash) doğrulamak için Global Exception Hook'un tetiklenip tetiklenmediğini kontrol et.

## 4. Otonom Graphify ve Dokümantasyon Güncellemesi
- Bir sınıf silindiğinde, eklendiğinde veya bir SQLAlchemy modeli değiştiğinde, otonom olarak projenin `graphify` şemalarını güncelleyen betiği çalıştır.
- Yapılan değişiklikleri projenin mimari Markdown belgelerine (gerekiyorsa) yansıt.

## 5. Güvenli Otonom Commit
- İşlemi bitirdiğinde commit atmadan önce `git diff` ile sadece kendi görev kapsamındaki dosyaları değiştirdiğinden emin ol.
- Commit mesajlarında robotik ifadeler kullanma, doğrudan insan mühendis tarafından yazılmış gibi profesyonel ve yapısal Türkçe dili kullan.