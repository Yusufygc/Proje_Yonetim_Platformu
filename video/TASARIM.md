# Tanıtım videosu tasarımı

## Amaç
Uygulamanın kullanımını göstererek tanıtan, hareketli grafik (motion) tarzında bir video.

- Yatay 1920x1080, 30 fps, MP4 (H.264, yuv420p, AAC), 60-90 sn. Senaryo hedefi 82 sn.
- Türkçe seslendirme ve altyazı (gömülü ve ayrı `.srt`).
- Hedefler: senaryo metni ve süresi tek dosyadan (`scenario.yaml`) değişir; tek komutla yeniden üretilir.

## Varsayımlar (yanlışsa düzeltilecek)
- Hedef kitle: bireysel geliştiriciler ve küçük ekipler (README'deki tanım).
- Ton: sade, samimi, profesyonel.
- Kapanış çağrısı: GitHub'dan indirme.

## Kapsam dışı
- 9:16 dikey sürüm.
- Sesli komut sahnesi: gerçek mikrofon gerektirir.
- Özel 3D ve karakter animasyonu.
- Uygulamaya yeni özellik eklemek.

## Videoyu başarısız sayacak durumlar
Gerçek kullanıcı verisinin görünmesi, kullanıcı ayarlarının değişmesi, bulanık arayüz, lisansı belirsiz müzik.

## Yaklaşımlar
| Yol | Artı | Eksi |
|---|---|---|
| A. PySide + ffmpeg | En az araç | Kamera hareketi ve yazı animasyonu zayıf |
| **B. PySide yakalar, Remotion kurgular (seçildi)** | Motion tarzı; zamanlama kurguda değişir | İkinci teknoloji (Node/React) |
| C. Kurgu da QML'de | Tek teknoloji | Efektlerin çoğu elle yazılır |

B'yi kullanıcı seçti.

## Akış
1. `capture/` (Python): örnek veriyi kurar, uygulamayı sürer; temiz kare dizileri ve olay kaydı
   (imleç konumu, tıklama, tuş; kare numarasıyla) üretir.
2. `audio/` (Python): sahne başına seslendirme, süre ölçümü, `.srt`, müzik ve efektler.
3. `remotion/`: kareler + olay kaydı + sesler → kamera, imleç, yazılar, kartlar, geçişler.
4. `build.py`: üç adımı sırayla çalıştırır, ffmpeg ile ses seviyesini dengeler, denetimi koşar.

## Yakalama kuralları
- **Veri yalıtımı:** uygulama içe aktarılmadan önce `PROJE_TAKIP_HOME` geçici klasöre,
  `PROJE_TAKIP_NO_UPDATE_CHECK=1` olarak ayarlanır.
- **Ayar yalıtımı:** tercihler `QSettings` ile kayıt defterine yazılır ve `PROJE_TAKIP_HOME` bunları
  kapsamaz. `QSettings` biçimi geçici INI dosyasına yönlendirilir.
- **Eski veri klasörü:** `migrate_legacy_data_dir()`, `~/.proje_takip` varsa ve hedefte veritabanı yoksa
  o klasörü hedefe taşır. Örnek veritabanı uygulama başlamadan önce kurulur. Bu makinede klasör yok.
- **Örnek veri:** sabit içerik. Tarihler üretim gününe göre geriye doğru verilir; analitik için 12 haftalık
  geçmiş kurulur, aksi halde grafik düz görünür.
- **Uygulama kodu:** hedef değiştirmemek. Betik, `QApplication.exec` çağrısını kendi yönetmeniyle sararak
  `run_qml_app()` kurulumunu aynen kullanır. Prototipte çalışmazsa kurulum ayrı bir fonksiyona bölünür.
- **İmleç:** uygulamaya çizilmez, kurguda olay kaydından eklenir.

## Doğrulanmamış teknik riskler (ilk prototipin konusu)
| Risk | Deneme | Yedek |
|---|---|---|
| Animasyon gerçek saatle akar, kare atlar | `QAnimationDriver` ile her karede 33,3 ms ilerletmek (`QTimer` kapsam dışı) | `QSG_FIXED_ANIMATION_STEP`; zaman damgasıyla yeniden örnekleme |
| 3840x2160 pencere ekrandan büyük, Windows kırpabilir | Ölçek 3, DPI etkisini ölçmek | Ölçek 1,5 veya `QQuickRenderControl` |
| `offscreen` modunda font ve gölge farkı | Normal modla yan yana karşılaştırmak | Normal pencere modu |
| QML'de yalnızca 4 `objectName` var | Öğeyi görünen metninden bulmak | Gerekli öğelere `objectName` eklemek |
| Sürükle-bırak sentetik olayla tetiklenmeyebilir | Fare basma, taşıma, bırakma olayları | `moveTaskRelative` çağrısı ve kurguda sürükleme canlandırması |

### Prototip sonuçları (yukarıdaki tablonun yerine geçer)
- `QAnimationDriver` PySide6 6.11'de dışa açık değil. `QSG_FIXED_ANIMATION_STEP=yes` işe yaradı: üç render
  döngüsünde aynı animasyon değerleri, her `grabWindow()` bir ekran yenilemesi (60 Hz'de 16,7 ms) ilerletiyor.
  Ekran yenileme hızı 60 Hz'in katı değilse hız sapar.
- `QTimer` gerçek saatle akıyor: bildirim videoda erken kayboluyordu. Çekimde bildirim süresi uzatılıyor
  (`capture/run.py::_keep_toasts`).
- `QT_SCALE_FACTOR=3` ile 3840x2160 kare alınıyor. Pencere çerçevesiz ve sabit; gerçek fare yok sayılıyor.
  Boyut tutmazsa çekim hata verip duruyor. Yalnızca %100 Windows ölçeğinde denendi.
- Küçük mantıksal ekran kenar çubuğunu daraltıyor; çekim başında açılıyor.
- Öğeleri görünen metinden bulmak çalıştı; uygulama koduna ve QML'e dokunulmadı.
- `offscreen` modu denenmedi: normal pencere modu yeterli oldu.
- Sürükle-bırak sentetik fare olaylarıyla çalışıyor.
- Pencere etkin değilken `Ctrl+K` tetiklenmiyor; arama bu durumda doğrudan açılır ve uyarı yazılır.
- Bir tam üretimde görev adı yarım kaydedildi ("Giriş ekra"). Muhtemel neden odak kaybı; yeniden
  üretilemedi. Tuşlar artık doğrudan metin alanına gidiyor ve yazılan metin harfiyen doğrulanıyor.
- Cümle zamanlaması: sahne betiği `say` işareti bırakır, cümle o eylemden önce okunmaz.

## Görsel dil
- Arayüz, gölgeli ve köşeleri yuvarlak bir pencere olarak koyu gradyan zeminde durur.
- Vurgu rengi uygulamanın slate teması; yazı tipi depodaki Plus Jakarta Sans.
- Kamera: sahne başına en fazla iki yakınlaştırma, yumuşak geçişli (spring).
- Her sahnede 2-4 kelimelik bir başlık. Altyazı alt güvenli alanda; arayüz metnini kapatmaz.
- Geçişler 8-12 kare. İlk 3 saniyede soru ve hareket (kanca).

## Ses (ücretsiz ve güvenli)
- **Seslendirme:** Supertonic 3 (`supertonic==1.3.1`, paket MIT). Sentez bilgisayarda yapılır, anahtar
  istemez. Model `video/assets/models/supertonic3` altındadır (385 MB, git dışı); SDK sürümü modeli sabit
  bir kayda (`724fb5ab`) bağlar.
  - Model lisansı OpenRAIL-M: üretilen ses üzerinde lisans veren hak iddia etmez; sorumluluk üretende.
    Kullanım kısıtları lisans ekinde (Attachment A).
  - Ek A(e), makine üretimi içeriğin açıkça belirtilmesini ister. Ses ayrıca sayılmıyor; yine de kapanış
    kartında not gösterilir ve video açıklamasına da eklenmelidir.
  - Örnekler: `python video/voice.py` (çıktı `video/out/ses_ornekleri/`).
  - Elenenler: Piper `fettah` ve `fahrettin` (2025-12-30'da katkıda bulunanların isteğiyle depodan
    kaldırıldı), Piper `dfki` (CC BY-NC-SA 4.0), Windows "Tolga" (yayın hakkına dair resmî açıklama
    bulunamadı). Yedek: VoxCPM2 (Apache-2.0, ana model dosyası 4,58 GB, GPU ister).
- **Müzik ve efekt:** betikle sıfırdan üretilir; üçüncü taraf lisansı yoktur. Kalite sade bir fon düzeyinde
  olur. İstersen kendi CC0 parçanı `assets/` altına koyabilirsin.
- Ses seviyesi `ffmpeg loudnorm` ile -14 LUFS; konuşurken müzik kısılır.

## Remotion lisansı
Bireyler ve en fazla 3 kişilik kuruluşlar için ücretsiz. Ortak çalışmada kişi sayıları toplanır.
5.0 sürümünde lisans metni bir miktar değişecek; bu yüzden 4.x sürümü sabitlenir (bugün 4.0.547).
Kaynak: https://github.com/remotion-dev/remotion/blob/main/LICENSE.md

## Kurulum ve indirmeler
- Python: `pyproject.toml` içindeki `demo` grubu (`supertonic`, `pyyaml`); `.venv` içine
  `pip install -e ".[demo]"`.
- Node: `video/remotion/package.json` ve kilit dosyası; sürümler sabit.
- İndirilenler: npm paketleri, Chrome Headless Shell (131 MB), Python paketleri ve Supertonic 3 modeli.

## Denetim
- Her sahnenin başı, ortası ve sonundan kare çıkarılıp gözle incelenir.
- Otomatik: süre, çözünürlük, fps, siyah kare (`blackdetect`), donma (`freezedetect`), ses seviyesi.
- Akıcılık ve ses tınısı otomatik ölçülemez; son izleme kullanıcıdadır.

## Onay noktaları
1. Senaryo (`scenario.yaml`).
2. Stil karesi ve kısa taslak (yakalama prototipi dahil).
3. Final video.
