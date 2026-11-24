# Ürün Vizyonu ve Kapsam

## Çalışma Adı

Şimdilik ürün adı: **NewProject**

Alternatif isimler:

- ProjectFlow
- SüreçDefteri
- BuildTrack
- IdeaToProject
- ProjeAtölyesi

Nihai isim daha sonra seçilebilir. Bu dokümanda `NewProject` adı kullanılacaktır.

## Ürün Vizyonu

NewProject, bireysel geliştiriciler, ürün sahipleri, tasarımcılar veya küçük ekipler için proje fikirlerini yakalayan, projeye dönüştüren, süreçleri izleyen ve yapılan işleri kanıtlarıyla birlikte saklayan bir proje takip uygulamasıdır.

Ürünün temel iddiası:

> Fikir, görev, tasarım, karar ve kaynaklar ayrı ayrı kaybolmasın; hepsi proje bağlamında takip edilsin.

## Hedef Kullanıcılar

Birincil kullanıcı:

- Kendi projelerini geliştiren bireysel yazılımcı veya maker.
- Birden fazla proje fikrini ve aktif geliştirmeyi aynı anda takip etmek isteyen kullanıcı.
- Portfolyo, ürün, eğitim, araştırma veya müşteri işi gibi farklı proje türleriyle çalışan kişi.

İkincil kullanıcı:

- 2-5 kişilik küçük ekip.
- Mentor-öğrenci proje takibi.
- Freelance iş takibi.

MVP ilk aşamada tek kullanıcı odaklı tasarlanmalı. Ekip özellikleri veri modelinde genişlemeye açık bırakılmalı ama ilk sürümde karmaşık yetkilendirme eklenmemeli.

## Ana Kullanım Senaryoları

1. Kullanıcı aklına gelen bir fikri hızlıca kaydeder.
2. Fikri değerlendirir ve uygun görürse projeye dönüştürür.
3. Yeni proje oluşturur; amaç, kapsam, teknoloji, durum ve öncelik girer.
4. Proje sürecini aşamalarla takip eder.
5. Projeye görevler, checklist maddeleri, kaynaklar, kararlar, notlar ve görseller ekler.
6. Hangi projelerin takıldığını, hangilerinin ilerlediğini ve hangilerinin tamamlandığını görür.
7. Proje sonunda çıktı, öğrenilenler ve portfolyo özetini kaydeder.

## Ürün Kapsamı

MVP kapsamına girmesi önerilenler:

- Proje CRUD.
- Fikir havuzu.
- Fikri projeye dönüştürme.
- Proje durum ve öncelik yönetimi.
- Proje süreç aşamaları.
- Görev yönetimi.
- Checklist yönetimi.
- Proje notları.
- Karar kayıtları.
- Kaynak/link yönetimi.
- Basit dashboard.
- Arama ve filtreleme.
- Yerel SQLite depolama.

MVP sonrasına bırakılabilecekler:

- Çok kullanıcılı ekip yönetimi.
- Gerçek zamanlı senkronizasyon.
- Bulut hesabı.
- Gantt görünümü.
- Takvim entegrasyonu.
- GitHub/Jira/Trello entegrasyonları.
- Dosya versiyonlama.
- Bildirim sistemi.
- AI destekli özetleme ve görev önerileri.

## Kapsam Dışı Kararlar

İlk sürümde yapılmaması önerilenler:

- Ağır kurumsal proje yönetimi özellikleri.
- Karmaşık sprint/epic/story hiyerarşisi.
- Muhasebe, fatura veya müşteri sözleşmesi yönetimi.
- Gelişmiş role-based access control.
- Web sunucusu, backend API ve deployment zorunluluğu.

Sebep: Ürün önce kişisel verimlilik ve proje hafızası sorununu çözmeli. Çok erken kurumsal özellik eklemek tasarımı ağırlaştırır.

## Başarı Ölçütleri

MVP başarılı sayılırsa:

- Kullanıcı 30 saniyeden kısa sürede fikir kaydedebilir.
- Kullanıcı 1 dakikadan kısa sürede yeni proje oluşturabilir.
- Kullanıcı seçili projenin durumunu tek ekranda anlayabilir.
- Kullanıcı bir projenin neden beklediğini veya hangi görevde takıldığını görebilir.
- Kullanıcı tamamlanan projeden portfolyo/özet bilgisi çıkarabilir.
- Veri modeli, fikirden tamamlanmış projeye kadar geçmişi kaybetmeden izleyebilir.

