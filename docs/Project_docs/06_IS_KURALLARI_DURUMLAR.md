# İş Kuralları ve Durumlar

## Proje Durumları

Önerilen değerler:

- `PLANNED`: Planlandı.
- `ACTIVE`: Aktif.
- `ON_HOLD`: Beklemede.
- `BLOCKED`: Tıkandı.
- `COMPLETED`: Tamamlandı.
- `CANCELLED`: İptal edildi.
- `ARCHIVED`: Arşivlendi.

Mevcut uygulamadaki durumlar korunabilir ama yeni üründe `BLOCKED` ayrı olmalı. Çünkü proje takip uygulamasında "bekliyor" ile "tıkanmış" farklı anlamlara gelir.

## Proje Sağlığı

Önerilen değerler:

- `GOOD`: Yolunda.
- `AT_RISK`: Riskli.
- `BLOCKED`: Tıkandı.
- `UNKNOWN`: Belirsiz.

Kural:

- Proje durumu `BLOCKED` ise sağlık da `BLOCKED` olmalı.
- Hedef tarihi geçmiş ve açık kritik görev varsa sağlık `AT_RISK` olabilir.
- MVP'de sağlık manuel seçilebilir; otomatik hesap ikinci fazda eklenebilir.

## Öncelik

Önerilen değerler:

- `LOW`: Düşük.
- `MEDIUM`: Orta.
- `HIGH`: Yüksek.
- `CRITICAL`: Kritik.

Kural:

- Dashboard kritik ve yüksek öncelikli açık görevleri öne çıkarır.

## Fikir Durumları

Önerilen değerler:

- `RAW`: Ham fikir.
- `REVIEWING`: İnceleniyor.
- `VALIDATING`: Doğrulanacak.
- `CONVERTED`: Projeye dönüştü.
- `DEFERRED`: Ertelendi.
- `REJECTED`: Reddedildi.

Kural:

- `CONVERTED` durumundaki fikirde `converted_project_id` dolu olmalı.
- `REJECTED` fikir silinmemeli; gerekçe notu tutulmalı.

## Süreç Aşaması Durumları

Önerilen değerler:

- `NOT_STARTED`: Başlamadı.
- `ACTIVE`: Aktif.
- `DONE`: Tamamlandı.
- `SKIPPED`: Atlandı.

Kural:

- Bir projede aynı anda varsayılan olarak tek aktif aşama olmalı.
- Kullanıcı isterse birden fazla aşamayı aktif yapmaya izin verilebilir; bu açık karar.
- Aşama tamamlandığında `completed_at` set edilmeli.
- Bir aşama tamamlanınca sıradaki aşama otomatik aktif olabilir.

## Görev Durumları

Önerilen değerler:

- `TODO`: Yapılacak.
- `IN_PROGRESS`: Devam ediyor.
- `WAITING`: Bekliyor.
- `BLOCKED`: Tıkandı.
- `DONE`: Tamamlandı.
- `CANCELLED`: İptal edildi.

Kural:

- Görev tamamlanınca `completed_at` set edilmeli.
- Tüm checklist maddeleri tamamlanmışsa sistem görevi tamamlamayı önerebilir.
- Görev `BLOCKED` olursa blokaj nedeni istenebilir.

## Görev Türleri

Önerilen değerler:

- `TASK`: Görev.
- `BUG`: Hata.
- `IMPROVEMENT`: İyileştirme.
- `RESEARCH`: Araştırma.
- `DOCUMENTATION`: Dokümantasyon.
- `DESIGN`: Tasarım.
- `TEST`: Test.

Mevcut uygulamadaki `FIKIR` ve `TASARIM` task tipi yaklaşımı MVP'de kullanılabilir. Ancak daha temiz model için fikir ayrı varlık, tasarım ise görev türü veya karar/not türü olarak modellenmeli.

## Karar Durumları

Önerilen değerler:

- `DRAFT`: Taslak.
- `ACCEPTED`: Kabul edildi.
- `SUPERSEDED`: Değiştirildi.
- `CANCELLED`: İptal edildi.

Kural:

- `SUPERSEDED` karar yeni bir karar kaydına bağlanabilmeli.
- Karar silmek yerine iptal etmek tercih edilmeli.

## Silme ve Arşivleme

Kural:

- Proje silme onay istemeli.
- Ürün genelinde "arşivle" aksiyonu silmeden daha görünür olmalı.
- Silinen proje ilişkili görevleri, aşamaları, notları ve kaynakları cascade silebilir.
- Arşivlenen proje dashboard aktif listelerinden çıkar.

## Validasyon Kuralları

Zorunlu alanlar:

- Proje: `title`.
- Fikir: `title`.
- Görev: `title`, `project_id`.
- Checklist: `text`, `task_id`.
- Karar: `title`, `decision`.
- Kaynak: `title` veya `url`.

Önerilen metin kuralları:

- Başlık trim edilmeli.
- Boş başlık reddedilmeli.
- Aynı proje içinde aynı başlıklı aktif görev uyarı verebilir ama kesin engel olmak zorunda değil.

## İlerleme Hesaplama

Üç seçenek var:

1. Manuel ilerleme yüzdesi.
2. Görev tamamlanma oranından otomatik ilerleme.
3. Süreç aşamalarından ağırlıklı ilerleme.

MVP önerisi:

- İlk sürümde otomatik görev oranı + manuel override alanı.
- Proje detayında "hesaplanan ilerleme" ve "manuel ilerleme" ayrımı gösterilebilir.

