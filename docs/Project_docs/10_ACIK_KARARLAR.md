# Açık Kararlar

Bu dosya, `00_INDEX`-`07_TEKNIK_MIMARI` aralığındaki MVP uygulaması sırasında netleşmesi gereken kararları izler.

## Karar 1: Migration Stratejisi

**Varsayılan karar:** SQLite için idempotent Python migration runner kullanılacak.

- `schema_migrations` tablosu migration kayıtlarını tutar.
- Mevcut veri korunur; destructive reset yapılmaz.
- Yeni tablolar SQLAlchemy metadata ile oluşturulur.
- Eski enum değerleri migration içinde yeni değerlere taşınır.

## Karar 2: İlerleme Hesaplama

**Varsayılan karar:** MVP'de görev tamamlanma oranı otomatik ilerleme üretir.

- `manual_progress_percent` doluysa manuel değer önceliklidir.
- Manuel değer yoksa `DONE` görevlerin oranı `progress_percent` alanına yazılır.
- `GROUP` tipindeki görevler hesap dışı bırakılır.

## Karar 3: Desktop / Web Yönü

**Varsayılan karar:** MVP PySide6 masaüstü uygulaması olarak kalır.

- Yerel SQLite depolama korunur.
- Web/API, ekip kullanımı ve senkronizasyon Faz 2+ konusudur.

## Karar 4: Ek Dosya ve Çıktılar

**Varsayılan karar:** MVP'de dosya kopyalama yapılmaz; dosya yolu veya bağlantı saklanır.

- `attachments.file_path` yerel yol veya URL tutabilir.
- Versiyonlama ve fiziksel dosya yönetimi ikinci faza bırakılır.

## Karar 5: Aktivite Geçmişi

**Varsayılan karar:** Kritik değişiklikler `activity_logs` tablosuna yazılır.

- Proje oluşturma.
- Varsayılan aşama oluşturma.
- Fikirden projeye dönüşüm.
- Aşama tamamlama ve aktivasyon.
- Görev oluşturma, güncelleme, tamamlama.

## Karar 6: Fikirden Projeye Dönüşüm

**Varsayılan karar:** Kullanıcı proje formunu fikir bilgileriyle ön doldurulmuş şekilde görür.

- Kullanıcı başlık, öncelik, durum, tarih ve diğer proje alanlarını düzenleyebilir.
- Dönüşüm sonrası `converted_project_id` set edilir.
- `project_ideas` ilişkisi `SOURCE` olarak oluşturulur.
