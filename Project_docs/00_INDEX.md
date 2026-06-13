# NewProject Tasarım Dokümanları

Bu klasör, mevcut portfolyo uygulamasındaki admin/projeler sekmesinden ilham alan fakat bağımsız bir "proje takip ve süreç izleme" ürünü için ilk tasarım paketidir.

Amaç, kod yazmadan önce ürünün kapsamını, veri modelini, ekranlarını, iş kurallarını ve geliştirme yol haritasını netleştirmektir. Dokümanları okurken eksik, gereksiz veya yanlış gördüğün noktaları işaretleyebilirsin; sonraki adımda bunları revize edip uygulama tasarımını kesinleştirebiliriz.

## Dosya Sırası

1. [01_MEVCUT_ADMIN_PROJELER_SEKMESI_ANALIZI.md](01_MEVCUT_ADMIN_PROJELER_SEKMESI_ANALIZI.md)
   - Mevcut admin sayfasındaki proje mantığından çıkarılan gözlemler.

2. [02_URUN_VIZYONU_VE_KAPSAM.md](02_URUN_VIZYONU_VE_KAPSAM.md)
   - Yeni ürünün hedefi, kullanıcı tipi, kapsamı ve kapsam dışı kararları.

3. [03_MODULLER_VE_ISLEVLER.md](03_MODULLER_VE_ISLEVLER.md)
   - Proje takip, süreç izleme, fikir kaydı, görev yönetimi ve destek modülleri.

4. [04_BILGI_MIMARISI_UX_AKISLARI.md](04_BILGI_MIMARISI_UX_AKISLARI.md)
   - Ana navigasyon, ekran tasarımları, kullanıcı akışları ve etkileşim modeli.

5. [05_VERI_MODELI.md](05_VERI_MODELI.md)
   - Varlıklar, ilişkiler, alanlar ve örnek şema tasarımı.

6. [06_IS_KURALLARI_DURUMLAR.md](06_IS_KURALLARI_DURUMLAR.md)
   - Proje, süreç, görev, fikir ve karar durumları için kurallar.

7. [07_TEKNIK_MIMARI.md](07_TEKNIK_MIMARI.md)
   - Önerilen katmanlı mimari, servisler, depolama ve teknoloji kararları.

8. [08_MVP_YOL_HARITASI.md](08_MVP_YOL_HARITASI.md)
   - İlk sürümden ileri sürümlere doğru geliştirme planı.

9. [09_TEST_KABUL_KRITERLERI.md](09_TEST_KABUL_KRITERLERI.md)
   - Test stratejisi ve kabul kriterleri.

10. [10_ACIK_KARARLAR.md](10_ACIK_KARARLAR.md)
    - Senden netleşmesi gereken ürün ve teknik kararlar.

11. [11_HIYERARSIK_GOREV_YONETIMI.md](11_HIYERARSIK_GOREV_YONETIMI.md)
    - WBS, alt görevler ve görev ağacı yaklaşımı.

12. [12_UI_UX_YONETIM_SISTEMLERI.md](12_UI_UX_YONETIM_SISTEMLERI.md)
    - Yönetim ekranları için UI/UX standartları.

13. [13_KALITE_VE_PERFORMANS_YONETIMI.md](13_KALITE_VE_PERFORMANS_YONETIMI.md)
    - Kalite, performans ve sürdürülebilirlik kararları.

14. [14_PREMIUM_UI_UX_TASARIM_PLANI.md](14_PREMIUM_UI_UX_TASARIM_PLANI.md)
    - Premium görsel sistem ve etkileşim planı.

15. [15_ALTYAPI_VE_DAGITIM_PLANI.md](15_ALTYAPI_VE_DAGITIM_PLANI.md)
    - Altyapı, paketleme ve dağıtım yaklaşımı.

16. [16_SENIOR_MIMARI_STANDARTLAR.md](16_SENIOR_MIMARI_STANDARTLAR.md)
    - Kod kalitesi, mimari sınırlar ve senior standartlar.

17. [17_UX_ERISILEBILIRLIK_VE_ETKILESIM_PLANI.md](17_UX_ERISILEBILIRLIK_VE_ETKILESIM_PLANI.md)
    - Erişilebilirlik ve etkileşim prensipleri.

18. [18_PROJE_INSA_SURECI_PIPELINE.md](18_PROJE_INSA_SURECI_PIPELINE.md)
    - Uygulama inşa süreci ve pipeline planı.

## Ek Dosyalar

- [KLASOR_YAPISI.MD](KLASOR_YAPISI.MD)
  - Hedef klasör yapısı.
- [RULES.md](RULES.md)
  - Kodlama ve proje kuralları.
- [Proje_Yonetim_ve_Takip_Platformu_Faz_2.md](Proje_Yonetim_ve_Takip_Platformu_Faz_2.md)
  - Faz 2 kapsamı.

## Tasarımın Ana Fikri

Yeni proje, basit bir "proje listesi + task kartı" sayfasından büyüyerek şu merkeze oturur:

- Projeleri sadece portfolyo öğesi olarak değil, canlı çalışma alanı olarak yönetmek.
- Görev, fikir, tasarım, karar, not, kaynak ve süreç adımlarını aynı proje bağlamında tutmak.
- Proje ilerlemesini durum, aşama, yapılacaklar, kararlar ve zaman çizelgesi üzerinden izlemek.
- Kişisel kullanımda hızlı ve sade, ekip kullanımına genişletilebilir bir temel kurmak.

## İlk Okuma İçin Öneri

Önce şu üç dosyayı oku:

- `01_MEVCUT_ADMIN_PROJELER_SEKMESI_ANALIZI.md`
- `02_URUN_VIZYONU_VE_KAPSAM.md`
- `04_BILGI_MIMARISI_UX_AKISLARI.md`

Sonra veri ve mimari tarafını değerlendirmek için:

- `05_VERI_MODELI.md`
- `07_TEKNIK_MIMARI.md`
