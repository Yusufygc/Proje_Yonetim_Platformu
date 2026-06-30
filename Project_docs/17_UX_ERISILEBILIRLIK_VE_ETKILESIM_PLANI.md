# 17. UX, Erişilebilirlik ve Etkileşim Planı

Bu doküman, uygulamanın görsel tasarımının (UI) ötesine geçerek, kullanıcının sistemle kurduğu etkileşimin kalitesini (UX), erişilebilirliğini ve profesyonel hissiyatını güvence altına alacak standartları belirler.

---

## 1. Boş Durumlar (Empty States) ve İlk Katılım (Onboarding)

Kullanıcı arayüzünde hiçbir verinin olmadığı durumlar, uygulamanın kalitesini gösteren en önemli anlardır. Bomboş beyaz/gri ekranlar kesinlikle yasaktır.

* **Görsel ve Metinsel Yönlendirme:** Proje listesi, görev listesi veya karar kayıtları boş olduğunda, o bölümün ortasında yüksek kaliteli, temaya uygun bir SVG illüstrasyon gösterilecektir.
* **Call-to-Action (CTA):** İllüstrasyonun hemen altında açıklayıcı, cesaretlendirici bir metin (Örn: "Henüz bir göreviniz yok. Harika işler başarmak için ilk adımı atın.") ve belirgin bir birincil buton (Örn: "Yeni Görev Ekle") yer alacaktır.
* **Örnek Proje Desteği (Onboarding):** Uygulama ilk kez kurulduğunda, sistemin yeteneklerini (WBS, Karar kayıtları vb.) gösteren örnek bir "Hoş Geldiniz" projesi otomatik olarak yüklü gelmelidir.

---

## 2. Erişilebilirlik (a11y) ve Klavye Navigasyonu (Power User Desteği)

Profesyonel masaüstü uygulamaları fareye bağımlı kalamaz. Hızlı ve akıcı bir kullanım için klavye etkileşimleri zorunludur.

* **Focus Ring (Odaklanma Halkası):** Kullanıcı `Tab` tuşu ile arayüzde gezinirken, aktif elementin etrafında arayüzü bozmayan ama net olarak görünen bir dış çizgi (Örn: 2px solid, temanın vurgu renginde) belirmelidir.
* **Global Klavye Kısayolları (Shortcuts):**
    * `Ctrl + N` veya `Cmd + N`: Bulunulan bağlama göre Yeni Proje veya Yeni Görev ekler.
    * `Ctrl + K` veya `Cmd + K`: Uygulama içi genel arama çubuğunu açar (Spotlight benzeri).
    * `Esc`: Açık olan modalları, dialogları kapatır veya arama kutusunu temizler.
* **Ağaç Gezinimi:** Görev listesinde ok tuşları (`Aşağı/Yukarı`) ile gezinilebilmeli, `Sağ Ok` klasörü açmalı, `Sol Ok` klasörü kapatmalıdır.
* **Sesli Girdi (Uygulandı):** Klavye kullanmakta zorlanan veya hızlı veri girmek isteyen kullanıcılar için metin alanlarının yanında mikrofon butonu bulunur — bkz. madde 6.

---

## 3. Sistem Geri Bildirimi (Feedback) ve Hata Kurtarma

Sistem hiçbir zaman "donmuş" veya "tepkisiz" hissettirmemelidir.

* **Skeleton Screens (İskelet Yükleyiciler):** Veritabanından büyük bir veri seti çekilirken veya ağaç yapısı oluşturulurken çirkin bir kum saati/spinner göstermek yerine, içeriğin geleceği yerlerde hafifçe parlayıp sönen (pulse animation) gri iskelet kutucuklar gösterilecektir.
* **Toast / Snackbar Bildirimleri:** Bir işlem (silme, arşivleme, dönüştürme) tamamlandığında, ekranın alt/üst köşesinde arayüzü engellemeyen, 3 saniye sonra kaybolan zarif bildirimler çıkacaktır.
* **Geri Al (Undo) Mekanizması:** "Arşivle" veya "Sil" gibi kritik işlemlerden sonra çıkan Toast mesajının sağında mutlaka bir "Geri Al" butonu bulunmalıdır. Kullanıcı yanlış bir tıklama yaptığında bunu anında telafi edebilmelidir.

---

## 4. Akışkan Düzen (Fluid Layout) ve Veri Yoğunluğu

Kullanıcı pencereyi küçülttüğünde veya çok uzun metinler girdiğinde arayüz kırılmamalıdır.

* **Duyarlı Sidebar (Responsive Menü):** Pencere genişliği belirli bir pikselin altına düştüğünde, sol navigasyon menüsü metinleri gizleyerek sadece ikonların göründüğü "Daraltılmış" (Collapsed) moda otomatik geçmelidir.
* **Metin Kırpma (Truncation) ve Tooltip:** Kartların veya listelerin içine sığmayan uzun başlıklar asla butonların veya diğer elemanların üstüne taşmamalıdır. Metin sonuna `...` (ellipsis) konulmalı ve üzerine gelindiğinde tam metin bir **Tooltip** içinde gösterilmelidir.
* **Özel Kaydırma Çubukları (Custom Scrollbars):** İşletim sisteminin varsayılan (genellikle kalın ve kaba) kaydırma çubukları gizlenecek; arayüzle bütünleşik, ince, sadece üzerine gelindiğinde belirginleşen modern QScrollBar tasarımları (QSS) uygulanacaktır.

---

## 5. Sürükle ve Bırak (Drag & Drop) Mikroskobik Etkileşimi

Görevleri veya aşamaları sıralarken görsel geri bildirimler net olmalıdır.

* **Sürükleme Hissiyatı (Ghosting):** Bir görev tutulup sürüklendiğinde, farenin ucunda o görevin %70 opaklığında bir kopyası (Ghost) gelmeli, asıl liste üzerindeki yerinde ise hafif soluk veya kesik çizgili bir boşluk (Placeholder) kalmalıdır.
* **Bırakma Alanları (Drop Zones):** Sürüklenen öğe, hedefin üzerine geldiğinde hedefin arka plan rengi çok hafif değişmeli veya iki öğe arasına net bir yatay/dikey çizgi (Insertion Indicator) çizilerek öğenin tam olarak nereye düşeceği gösterilmelidir.

---

## 6. Sesli Girdi (Voice Input) — Uygulandı (2026-06-30)

Klavyeye alternatif, motor becerisi/hız kısıtı olan kullanıcılar veya elleri meşgulken hızlı
not almak isteyenler için erişilebilirlik kazandıran bir giriş yöntemidir.

* **Çevrimdışı çalışır:** Konuşma tanıma cihaz üzerinde (Vosk, Türkçe model) gerçekleşir;
  ses verisi ağa çıkmaz, internet bağlantısı gerekmez — gizlilik ve erişilebilirlik bir arada.
* **Tutarlı yerleşim:** Mikrofon ikonu her zaman ilgili metin alanının sağında, mevcut
  `IconActionButton` görsel diline uygun (28×28, hover'da renk değişimi) — yeni bir etkileşim
  paterni öğrenmeyi gerektirmez.
* **Net durum geri bildirimi:** Dinleme sırasında buton kırmızımsı arka plana döner ve
  tooltip "Dinleniyor… durdurmak için tıkla" olarak değişir; sistem asla sessizce ne
  yaptığını belirsiz bırakmaz (bkz. madde 3, Sistem Geri Bildirimi ilkesiyle tutarlı).
* **Zarif bozulma (graceful degradation):** Model dosyası kurulu değilse veya mikrofon
  erişilemezse, özellik sessizce uygulamayı kilitlemez — kullanıcıya Toast ile anlaşılır
  bir uyarı gösterilir, diğer tüm işlevler normal çalışmaya devam eder.
* **Kapsam:** Başlık alanları (görev, fikir, hızlı ekle) ve tüm uzun açıklama/not/gerekçe
  alanları. Teknik detay: `03_MODULLER_VE_ISLEVLER.md` §11, `07_TEKNIK_MIMARI.md`,
  `docs/wiki/sesli-komut.md`.
