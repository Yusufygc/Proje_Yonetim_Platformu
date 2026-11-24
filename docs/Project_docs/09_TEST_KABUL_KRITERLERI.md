# Test ve Kabul Kriterleri

## Test Yaklaşımı

Öncelik sırası:

1. Domain ve service testleri.
2. Repository ve migration testleri.
3. Controller signal davranışları.
4. Kritik UI akışları.

MVP'de UI testleri sınırlı tutulabilir; iş kuralları service testleriyle güvenceye alınmalı.

## Proje Testleri

Kabul kriterleri:

- Başlıksız proje oluşturulamaz.
- Sadece başlıkla proje oluşturulabilir.
- Proje oluşturulunca varsayılan durum atanır.
- Proje oluşturulunca varsayılan süreç aşamaları oluşur.
- Proje güncellenebilir.
- Proje arşivlenebilir.
- Proje silinince ilişkili görevler cascade silinir.
- Etiketler kaydedilir ve tekrar yüklenir.

## Fikir Testleri

Kabul kriterleri:

- Başlıksız fikir oluşturulamaz.
- Fikir `RAW` durumunda oluşturulur.
- Fikir güncellenebilir.
- Fikir projeye dönüştürülebilir.
- Dönüşen fikirde proje bağlantısı kaybolmaz.
- Dönüşen fikir tekrar projeye dönüştürülemez veya kullanıcıya uyarı gösterilir.

## Süreç Testleri

Kabul kriterleri:

- Yeni projeye varsayılan aşamalar doğru sırayla eklenir.
- Bir aşama aktif yapılabilir.
- Aşama tamamlanınca `completed_at` yazılır.
- Zorunlu açık görev varsa aşama tamamlama uyarı verir.
- Aşama sırası değiştirilebilir.

## Görev Testleri

Kabul kriterleri:

- Başlıksız görev oluşturulamaz.
- Görev projeye bağlanır.
- Görev aşamaya bağlanabilir.
- Görev durumu değiştirilebilir.
- Görev tamamlanınca `completed_at` yazılır.
- Görev silinince checklist maddeleri silinir.
- Görev filtreleri doğru sonuç döndürür.

## Checklist Testleri

Kabul kriterleri:

- Checklist maddesi eklenir.
- Checklist maddesi tamamlanır.
- Checklist maddesi silinir.
- Checklist tamamlanma oranı doğru hesaplanır.
- Tüm checklist maddeleri tamamlanınca görev için tamamlandı önerisi üretilebilir.

## Karar Kaydı Testleri

Kabul kriterleri:

- Karar başlığı ve karar metni zorunludur.
- Karar taslak olarak oluşturulabilir.
- Karar kabul edilebilir.
- Kabul edilen karar değiştirildi durumuna alınabilir.
- Karar proje detayında listelenir.

## Aktivite Log Testleri

Kabul kriterleri:

- Proje oluşturulunca aktivite kaydı oluşur.
- Görev tamamlanınca aktivite kaydı oluşur.
- Fikir projeye dönüşünce aktivite kaydı oluşur.
- Aşama tamamlanınca aktivite kaydı oluşur.
- Aktivite kayıtları proje detayında ters kronolojik listelenir.

## Dashboard Testleri

Kabul kriterleri:

- Toplam proje sayısı doğru hesaplanır.
- Aktif proje sayısı doğru hesaplanır.
- Tıkalı proje sayısı doğru hesaplanır.
- Kritik açık görevler doğru listelenir.
- Son aktiviteler doğru sırayla gelir.

## Migration Testleri

Kabul kriterleri:

- Temiz DB üzerinde tüm migration'lar çalışır.
- Migration tekrar çalıştırıldığında veri bozulmaz.
- Foreign key kısıtları aktiftir.
- Cascade delete beklenen ilişkilerde çalışır.

## UI Kabul Kriterleri

Genel:

- Ana pencere açılır.
- Sidebar geçişleri çalışır.
- Proje listesi boşken anlamlı boş durum gösterilir.
- Dialoglarda iptal ve kaydet davranışları doğru çalışır.
- Hata mesajları kullanıcıya anlaşılır gösterilir.

Projeler ekranı:

- Sol listeden proje seçilince detay değişir.
- Proje ekleme sonrası liste yenilenir.
- Seçili proje güncelleme sonrası seçili kalır.
- Silme/arşivleme onay ister.

Görev ekranı:

- Görev kartı açılır/kapanır.
- Checklist değişiklikleri hızlı kaydedilir.
- Görev durumu görsel olarak anlaşılır.

