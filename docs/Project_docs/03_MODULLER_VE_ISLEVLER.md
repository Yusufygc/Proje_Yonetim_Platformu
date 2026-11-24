# Modüller ve İşlevler

## 1. Dashboard

Amaç: Kullanıcının genel proje sağlığını hızlıca görmesi.

Önerilen bileşenler:

- Toplam proje sayısı.
- Aktif proje sayısı.
- Bekleyen/tıkanan proje sayısı.
- Tamamlanan proje sayısı.
- Bu hafta güncellenen projeler.
- En yüksek öncelikli açık görevler.
- Son eklenen fikirler.
- Yaklaşan kilometre taşları.
- Süreci yavaşlayan projeler.

MVP dashboard sade olmalı:

- 4-6 istatistik kartı.
- Aktif projeler listesi.
- Son aktiviteler listesi.
- Hızlı fikir ekleme kutusu.

## 2. Projeler

Amaç: Projeleri oluşturmak, düzenlemek, takip etmek ve detaylandırmak.

Temel alanlar:

- Başlık.
- Kısa açıklama.
- Detaylı açıklama.
- Problem tanımı.
- Hedef çıktı.
- Proje türü.
- Durum.
- Öncelik.
- Başlangıç tarihi.
- Hedef bitiş tarihi.
- Gerçek bitiş tarihi.
- Etiketler.
- Teknolojiler.
- GitHub URL.
- Demo URL.
- Doküman URL.
- Portfolyoya eklensin mi?
- Arşivlendi mi?

Liste görünümü (Uygulandı, 2026-07-01): kullanıcı sol panelde projeleri sürükleyerek
kendi sırasını (`display_order`) belirleyebilir; kartlar soluk dolgu zeminli, ayrık
görünümdedir. Detay: `07_TEKNIK_MIMARI.md`, `docs/wiki/liste-siralama.md`.

Önerilen proje türleri:

- Yazılım.
- Eğitim.
- Araştırma.
- Tasarım.
- İç araç.
- Müşteri işi.
- Deneysel.
- Diğer.

## 3. Fikir Havuzu

Amaç: Henüz projeye dönüşmemiş fikirleri kaybetmeden saklamak.

Fikir alanları:

- Başlık.
- Problem veya ihtiyaç.
- Önerilen çözüm.
- Hedef kullanıcı.
- Beklenen fayda.
- Zorluk seviyesi.
- Tahmini efor.
- Öncelik.
- Durum.
- Etiketler.
- Kaynak bağlantıları.
- Notlar.

Fikir durumları:

- Ham fikir.
- İnceleniyor.
- Doğrulanacak.
- Projeye dönüştü.
- Ertelendi.
- Reddedildi.

Önemli aksiyon:

- "Projeye dönüştür" butonu.
- Bu aksiyon yeni proje oluşturur ve fikri kaynak fikir olarak bağlar.

Liste görünümü (Uygulandı, 2026-07-01): fikirler sürükle-bırak ile yeniden
sıralanabilir (`sort_order`). Detay: `docs/wiki/liste-siralama.md`.

## 4. Süreç İzleme

Amaç: Projeyi tek bir durum alanından daha ayrıntılı izlemek.

Önerilen varsayılan süreç:

1. Fikir.
2. Analiz.
3. Tasarım.
4. Geliştirme.
5. Test.
6. Yayın.
7. Bakım.
8. Tamamlandı.

Her proje kendi süreç aşamalarını özelleştirebilir:

- Aşama adı.
- Sıralama.
- Durum.
- Başlangıç tarihi.
- Bitiş tarihi.
- Açıklama.
- Aşamaya bağlı görevler.
- Aşama kabul kriterleri.

## 5. Görevler

Amaç: Yapılabilir işleri takip etmek.

Görev alanları:

- Başlık.
- Açıklama.
- Durum.
- Öncelik.
- Tür.
- Proje.
- Süreç aşaması.
- Hedef tarih.
- Tahmini süre.
- Harcanan süre.
- Checklist.
- Bağlı fikir veya karar.
- Etiketler.

Görev türleri:

- Görev.
- Hata.
- İyileştirme.
- Araştırma.
- Dokümantasyon.
- Tasarım.
- Test.

Sıralama (Düzeltildi, 2026-07-01): yeni görev oluşturulurken `order_index`
otomatik hesaplanır (`TaskRepository.next_order_index`, kardeş grubunun
`max+1`'i); "Hızlı Ekle" ile eklenen görev artık listenin başına değil
sonuna düşer.

Görev görünümleri:

- Liste.
- Kanban.
- Proje detayında gruplanmış kartlar.
- Aşama bazlı görünüm.

## 6. Checklist

Amaç: Görev içindeki küçük yapılacakları yönetmek.

Mevcut projede checklist bilgisi task açıklamasında JSON olarak tutuluyor. Yeni projede ayrı model olmalı.

Alanlar:

- Görev ID.
- Metin.
- Tamamlandı mı?
- Sıralama.
- Oluşturulma tarihi.
- Tamamlanma tarihi.

Avantaj:

- Tamamlanma oranı hesaplanabilir.
- Arama yapılabilir.
- Aktivite geçmişi üretilebilir.
- Görev açıklaması gerçek açıklama olarak kalır.

## 7. Karar Kayıtları

Amaç: Projede verilen teknik veya ürün kararlarını gerekçeleriyle saklamak.

Alanlar:

- Başlık.
- Karar özeti.
- Bağlam.
- Seçilen çözüm.
- Alternatifler.
- Gerekçe.
- Etki.
- Durum.
- İlgili proje.
- İlgili süreç aşaması.
- İlgili görevler.

Durumlar:

- Taslak.
- Kabul edildi.
- Değiştirildi.
- İptal edildi.

Bu modül özellikle proje sonunda "neden böyle yaptım?" sorusunu cevaplar.

## 8. Notlar

Amaç: Serbest metinli proje hafızası.

Not türleri:

- Genel not.
- Toplantı notu.
- Araştırma notu.
- Hata ayıklama notu.
- Öğrenilen ders.
- Yayın notu.

Notlar Markdown desteklemeli. İlk sürümde basit plain text yeterli olabilir, ama veri modeli Markdown'a uygun tutulmalı.

Liste görünümü (Uygulandı, 2026-07-01): notlar sürükle-bırak ile yeniden
sıralanabilir (`sort_order`). Detay: `docs/wiki/liste-siralama.md`.

## 9. Kaynaklar

Amaç: Projeye bağlı link, doküman, video, repo, makale veya referansları saklamak.

Kaynak alanları:

- Başlık.
- URL.
- Tür.
- Açıklama.
- Etiketler.
- İlgili proje.
- İlgili fikir.
- İlgili görev.

Kaynak türleri:

- Doküman.
- Makale.
- Video.
- GitHub.
- Tasarım.
- API.
- Araç.
- Diğer.

## 10. Aktivite Geçmişi

Amaç: Projenin nasıl ilerlediğini zaman içinde görmek.

Kaydedilecek olaylar:

- Proje oluşturuldu.
- Proje durumu değişti.
- Görev eklendi.
- Görev tamamlandı.
- Fikir projeye dönüştü.
- Karar kabul edildi.
- Süreç aşaması tamamlandı.
- Not eklendi.
- Kaynak eklendi.

MVP'de bu modül otomatik arka plan kaydı olarak çalışabilir; UI'da sadece proje detayında "Son Aktiviteler" listesi gösterilir.

## 11. Sesli Komut (Dikte)

Amaç: Klavyeyle yazmak yerine mikrofona konuşarak metin alanlarını doldurmak; erişilebilirlik
ve hız kazandırır.

Kapsam: ayrı bir modül/sayfa değil, mevcut metin alanlarına eklenen **çapraz kesit (cross-cutting)
yetenek**. Mikrofon butonu eklenen alanlar:

- Proje, görev, fikir, karar, not, kaynak başlık alanları (tek satır).
- Açıklama, problem, çözüm, gerekçe, notlar gibi çok satırlı alanlar.
- Görevler sayfasındaki "Hızlı Ekle" kutusu.
- Notlarım (memo) sayfası editörü.

Çalışma şekli:

- Mikrofon ikonuna tıkla → dinleme başlar (buton görsel olarak "kayıt" durumuna geçer).
- Konuşulan metin, çevrimdışı bir tanıma motoruyla (Vosk, Türkçe model) yazıya çevrilir ve
  imleç konumuna eklenir.
- Tekrar tıklamak dinlemeyi durdurur.

Tasarım kararları:

- **Çevrimdışı çalışır** — internet bağlantısı veya üçüncü taraf API anahtarı gerekmez;
  ses verisi cihaz dışına çıkmaz (gizlilik).
- Model dosyası uygulamayla birlikte dağıtılmaz (boyut nedeniyle), kullanıcı/kurulum
  sürecinde ayrıca indirilir; model yoksa özellik sessizce devre dışı kalır (uygulama
  diğer işlevlerini etkilemeden çalışmaya devam eder), kullanıcıya bilgilendirici uyarı gösterilir.
- Mikrofon erişilemezse (cihaz yok/izin yok) aynı şekilde kullanıcıya anlaşılır bir uyarı
  gösterilir; uygulama kilitlenmez.

Teknik mimari detayı: `07_TEKNIK_MIMARI.md` ve `docs/wiki/sesli-komut.md`.

