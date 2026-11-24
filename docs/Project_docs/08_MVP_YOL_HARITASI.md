# MVP Yol Haritası

## Faz 0: Tasarım Netleştirme

Amaç:

- Bu dokümanları okuyup kapsamı netleştirmek.

Çıktılar:

- Onaylı veri modeli.
- Onaylı ekran listesi.
- Onaylı MVP kapsamı.
- Açık kararların kapatılması.

## Faz 1: Proje Temeli

Amaç:

- Yeni uygulamanın iskeletini oluşturmak.

İşler:

- Klasör yapısı.
- Config.
- DB manager.
- Migration sistemi.
- DI container.
- Tema ve temel layout.
- Ana pencere ve sidebar.

Kabul kriterleri:

- Uygulama açılır.
- SQLite DB oluşur.
- Migration'lar çalışır.
- Sidebar ile boş sayfalar arasında geçiş yapılır.

## Faz 2: Proje Yönetimi

Amaç:

- Proje CRUD ve proje detay ekranı.

İşler:

- `Project` modeli.
- `ProjectRepository`.
- `ProjectService`.
- `ProjectController`.
- Projeler sayfası.
- Proje oluşturma/düzenleme dialogu.
- Proje silme/arşivleme.
- Etiket yönetimi.

Kabul kriterleri:

- Kullanıcı proje oluşturur.
- Proje listede görünür.
- Proje düzenlenir.
- Boş başlık reddedilir.
- Proje arşivlenir veya silinir.

## Faz 3: Süreç Aşamaları

Amaç:

- Proje ilerlemesini aşamalarla izlemek.

İşler:

- Varsayılan süreç aşamaları.
- Proje oluşturulunca aşamaların kopyalanması.
- Aşama durumları.
- Stage timeline widget.
- Aşama tamamlama aksiyonu.

Kabul kriterleri:

- Yeni projede varsayılan aşamalar oluşur.
- Aktif aşama görünür.
- Aşama tamamlanabilir.
- Sonraki aşama aktif olabilir.

## Faz 4: Görev ve Checklist

Amaç:

- Proje içi yapılacakları yönetmek.

İşler:

- `Task` modeli.
- `ChecklistItem` modeli.
- Görev CRUD.
- Checklist editor.
- Görev durum/öncelik filtreleri.
- Proje detayında görev listesi.

Kabul kriterleri:

- Projeye görev eklenir.
- Görev aşamaya bağlanır.
- Checklist maddesi eklenir/silinir/tamamlanır.
- Görev tamamlanınca tarih yazılır.

## Faz 5: Fikir Havuzu

Amaç:

- Fikirleri kaydetmek ve projeye dönüştürmek.

İşler:

- `Idea` modeli.
- Fikir CRUD.
- Fikirler sayfası.
- Hızlı fikir ekleme.
- Fikri projeye dönüştürme.

Kabul kriterleri:

- Kullanıcı hızlı fikir kaydeder.
- Fikir listelenir.
- Fikir projeye dönüştürülür.
- Fikir ile proje bağlantısı korunur.

## Faz 6: Kararlar, Notlar, Kaynaklar

Amaç:

- Proje hafızasını güçlendirmek.

İşler:

- Decision record CRUD.
- Notes CRUD.
- Resources CRUD.
- Proje detay sekmelerine ekleme.

Kabul kriterleri:

- Projeye karar kaydı eklenir.
- Projeye not eklenir.
- Projeye kaynak linki eklenir.
- Hepsi proje detayında görünür.

## Faz 7: Dashboard ve Arama

Amaç:

- Genel görünürlük ve hızlı erişim.

İşler:

- Dashboard service.
- İstatistik kartları.
- Aktif/tıkanan proje listesi.
- Son aktiviteler.
- Global arama.
- Filtreler.

Kabul kriterleri:

- Dashboard gerçek verilerle dolar.
- Tıkalı projeler görünür.
- Arama proje, fikir ve görevlerde çalışır.

## Faz 8: Stabilizasyon

Amaç:

- İlk kullanılabilir sürüm.

İşler:

- Testlerin tamamlanması.
- Boş durum ekranları.
- Hata mesajları.
- Veri yedekleme.
- Basit export.
- UI cilası.

Kabul kriterleri:

- Kritik servis testleri geçer.
- Migration testleri geçer.
- Uygulama temiz DB ile açılır.
- Kullanıcı bir projeyi baştan sona takip edebilir.

## MVP Dışı İleri Fazlar

Sonraki özellikler:

- Kanban görünümü.
- Takvim görünümü.
- Gantt/timeline.
- GitHub entegrasyonu.
- Markdown editörü.
- Dosya ekleri.
- Export: Markdown, PDF, DOCX.
- AI destekli proje özeti.
- Web sürümü.
- Çok kullanıcı ve senkronizasyon.

