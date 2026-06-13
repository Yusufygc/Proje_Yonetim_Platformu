# Bilgi Mimarisi ve UX Akışları

## Ana Navigasyon

Önerilen sol menü:

- Dashboard.
- Projeler.
- Fikir Havuzu.
- Görevler.
- Süreçler.
- Kaynaklar.
- Arşiv.
- Ayarlar.

MVP için minimum menü:

- Dashboard.
- Projeler.
- Fikirler.
- Görevler.
- Ayarlar.

## Ana Ekran Düzeni

Mevcut admin projeler sekmesinden esinlenen temel düzen:

- Sol kolon: Proje listesi ve filtreler.
- Orta alan: Seçili proje özeti ve aktif iş alanı.
- Üst bar: Arama, hızlı ekleme, görünüm değiştirici.
- Sağ panel veya sekmeler: Detay, süreç, görevler, fikirler, kararlar, kaynaklar, notlar.

Alternatif olarak proje detay ekranı sekmeli olabilir:

- Özet.
- Süreç.
- Görevler.
- Fikirler.
- Kararlar.
- Notlar.
- Kaynaklar.
- Çıktılar.

## Projeler Ekranı

Liste kartında gösterilecek bilgiler:

- Proje adı.
- Kısa açıklama.
- Durum rozeti.
- Öncelik.
- İlerleme yüzdesi.
- Aktif aşama.
- Açık görev sayısı.
- Son güncelleme.
- Etiketler.

Detay üst bölümünde gösterilecek bilgiler:

- Proje adı.
- Durum.
- Aktif aşama.
- İlerleme.
- Hedef tarih.
- Kısa açıklama.
- Hızlı aksiyonlar: görev ekle, fikir ekle, not ekle, karar ekle, kaynak ekle.

## Proje Detay Sekmeleri

### Özet

İçerik:

- Proje amacı.
- Problem tanımı.
- Hedef çıktı.
- Durum ve öncelik.
- İlerleme yüzdesi.
- Son aktiviteler.
- Açık riskler.
- Yaklaşan görevler.

### Süreç

İçerik:

- Aşama listesi.
- Her aşama için durum.
- Aşamaya bağlı görevler.
- Kabul kriterleri.
- Aşama notları.

Görünüm:

- Yatay stepper.
- Dikey timeline.
- Aşama kartları.

MVP için dikey timeline daha kolay ve okunabilir.

### Görevler

İçerik:

- Filtreler: durum, öncelik, tür, aşama.
- Liste veya Kanban görünümü.
- Görev kartları.
- Kart içinde checklist özeti.

MVP için liste görünümü yeterli. Kanban ikinci fazda eklenebilir.

### Fikirler

İçerik:

- Projeye bağlı fikirler.
- Projeye dönüşmeyi bekleyen fikirler.
- Fikri göreve veya karara bağlama.

### Kararlar

İçerik:

- Karar başlığı.
- Durum.
- Kısa gerekçe.
- Etki alanı.
- Tarih.

### Notlar

İçerik:

- Serbest metin notları.
- Not türü.
- Tarih.
- Etiketler.

### Kaynaklar

İçerik:

- Linkler.
- Dokümanlar.
- Repo bağlantıları.
- Tasarım dosyaları.
- API referansları.

## Kullanıcı Akışları

### Akış 1: Hızlı Fikir Kaydetme

1. Kullanıcı Dashboard veya Fikirler ekranında hızlı fikir kutusuna yazar.
2. Başlık zorunlu, diğer alanlar opsiyoneldir.
3. Fikir `Ham fikir` durumunda kaydedilir.
4. Son aktivitelerde görünür.
5. Kullanıcı daha sonra fikri detaylandırabilir.

Başarı kriteri:

- Kullanıcı sadece başlık girerek fikir kaydedebilmelidir.

### Akış 2: Fikri Projeye Dönüştürme

1. Kullanıcı fikir detayını açar.
2. "Projeye dönüştür" aksiyonunu seçer.
3. Sistem proje oluşturma formunu fikir bilgileriyle doldurur.
4. Kullanıcı proje türü, durum, öncelik ve hedef tarih ekler.
5. Proje oluşturulur.
6. Fikir durumu `Projeye dönüştü` olur.
7. Proje ile fikir arasında bağlantı kurulur.

Başarı kriteri:

- Fikir geçmişi kaybolmamalıdır.

### Akış 3: Yeni Proje Oluşturma

1. Kullanıcı "Yeni Proje" butonuna basar.
2. Minimum alan: başlık.
3. Önerilen alanlar: kısa açıklama, durum, öncelik, hedef çıktı.
4. Sistem varsayılan süreç aşamalarını oluşturur.
5. Proje listede görünür.

Başarı kriteri:

- Boş başlıkla proje kaydedilemez.
- Proje oluşturulunca ilk aşama otomatik aktif olabilir.

### Akış 4: Süreç Aşaması İlerletme

1. Kullanıcı proje detayında süreç sekmesine gider.
2. Aktif aşamanın kabul kriterlerini ve görevlerini görür.
3. Gerekli görevleri tamamlar.
4. "Aşamayı tamamla" aksiyonunu seçer.
5. Sistem sonraki aşamayı aktif yapar.
6. Aktivite geçmişine kayıt düşer.

Başarı kriteri:

- Tamamlanmamış zorunlu görev varsa sistem kullanıcıyı uyarmalıdır.

### Akış 5: Görev ve Checklist Yönetimi

1. Kullanıcı proje içinde görev ekler.
2. Görevin aşamasını, önceliğini ve durumunu seçer.
3. Görev kartında checklist maddeleri ekler.
4. Checklist tamamlandıkça görev ilerleme oranı hesaplanır.
5. Tüm checklist tamamlanınca kullanıcıya görevi tamamlama önerisi gösterilir.

Başarı kriteri:

- Checklist değişimi tüm proje detayını yeniden yüklemek zorunda kalmadan hızlı kaydedilmelidir.

## Etkileşim Prensipleri

- Hızlı kayıt önceliklidir: Başlıkla kayıt yapılabilmeli.
- Detay sonradan doldurulabilmeli.
- Liste ekranları yoğun ama okunabilir olmalı.
- Kartlar gereksiz büyük olmamalı.
- Durumlar renk ve metinle birlikte gösterilmeli.
- Silme aksiyonları onay istemeli.
- Arşivleme, silmeye göre daha görünür bir seçenek olmalı.
- Her kritik değişiklik aktivite geçmişine yazılmalı.

