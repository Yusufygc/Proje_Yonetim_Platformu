# AI Asistan Geliştirme Yönergeleri (CLAUDE.md)

Bu dosya, **Proje Yönetim ve Takip Platformu** deposunda (repository) çalışacak tüm yapay zeka asistanları (Claude, ChatGPT, Gemini vb.) için bağlayıcı kuralları içerir. Bu projede kod yazmadan veya mimari bir değişiklik önermeden önce bu kuralları ve `RULES.md` dosyasını okumak **ZORUNLUDUR**.

## 1. Temel Anayasa: RULES.md
- Geliştirilecek her kod parçası `RULES.md` dosyasındaki standartlara uymak zorundadır.
- **Asla "God Object" yaratma:** Bir dosya 400 satırı, bir sınıf 15 metodu aşıyorsa, mevcut koda ekleme yapmak yerine refactoring (alt modüllere bölme) öner.
- SOLID prensiplerini ve Single Responsibility (Tek Sorumluluk) kuralını her fonksiyonda gözet.

## 2. Mimari ve Teknoloji Yığını
- **Arayüz (UI):** PySide6 kullanılacak. Eski tip gri, kutu gibi arayüzler yerine `14_PREMIUM_UI_UX_TASARIM_PLANI.md` uyarınca modern, gölgeli (QGraphicsDropShadowEffect), gradyanlı ve animasyonlu (200-300ms) bileşenler kodlanacak.
- **Veritabanı:** Doğrudan SQLite sorguları YASAKTIR. Veri katmanında `SQLAlchemy` ve `Alembic` kullanılacaktır. Tüm şema değişiklikleri migration scriptleri ile yapılacaktır.
- **Bellek Yönetimi:** PySide6 widget'ları oluşturulurken memory leak (bellek sızıntısı) olmaması için daima `parent` parametresi atanacaktır.

## 3. İletişim ve Commit Kuralları
- Commit mesajları yazarken asla AI referansı verme (Örn: "Yapay zeka tarafından düzeltildi", "Prompt uygulandı" YASAKTIR).
- Commit mesajları tamamen Türkçe, imla kurallarına uygun ve o dosyadaki değişikliği spesifik olarak açıklayan nitelikte olacaktır.
- Kod yazarken neyin yapıldığını değil, **neden** yapıldığını anlatan açıklayıcı Türkçe yorum satırları eklenecektir.