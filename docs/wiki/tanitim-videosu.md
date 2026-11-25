# Tanıtım Videosu Üretimi

`video/` klasörü, uygulamanın kullanımını gösteren 1920x1080 tanıtım videosunu üretir. Uygulama kodunu
değiştirmez ve kurulum dosyasına girmez.

## Kurulum (bir kez)

```powershell
.venv\Scripts\python.exe -m pip install -e ".[demo]"
```

```powershell
npm install --prefix video\remotion
```

Ayrıca `ffmpeg` ve Node.js gerekir. Ses modeli (Supertonic 3, yaklaşık 385 MB) depoda yoktur:

```powershell
.venv\Scripts\python.exe -c "from pathlib import Path; from supertonic import TTS; TTS(model='supertonic-3', model_dir=Path('video/assets/models/supertonic3').resolve(), auto_download=True)"
```

İlk kurguda Remotion, Chrome Headless Shell indirir.

## Üretim

```powershell
.venv\Scripts\python.exe video\build.py
```

Çıktılar: `video/out/demo.mp4` ve `video/out/demo.srt`. Baştan üretim yaklaşık 12 dakika sürer.
Çekim sırasında uygulama penceresi ekranı kaplar ve gerçek fare girdisini yok sayar.

| İstek | Komut veya ayar |
|---|---|
| Yalnızca metin, ses veya kurgu değişti | `video\build.py --skip-capture` |
| Tek sahneyi yeniden çek | `video\capture\run.py --scene arama` |
| Altyazıyı gömme | `scenario.yaml` içinde `altyazi_gomulu: false` |
| Başka ses | `scenario.yaml` içinde `seslendirme.ses` (`F1`-`F5`, `M1`-`M5`) |
| Kendi müziğin | dosyayı `video/assets/` altına koy, `muzik.kaynak` alanına adını yaz |

Metin, süre ve başlıklar [scenario.yaml](../../video/scenario.yaml) dosyasındadır. Ekrandaki adımlar
`video/capture/scenes.py` içindedir; her adımın sonucu doğrulanır, boşa giden tıklamada çekim durur.

## Nasıl çalışır

1. **Yakalama:** her sahne ayrı süreçte, geçici veri klasörü ve geçici ayar dosyasıyla açılır. Kareler
   `grabWindow()` ile 3840x2160 alınır; `QSG_FIXED_ANIMATION_STEP` animasyonu her karede sabit ilerletir.
2. **Ses:** metin cümle cümle seslendirilir; altyazı zamanları ölçülen süreden gelir. Müzik ve efektler
   betikle üretilir.
3. **Kurgu:** Remotion kamera, imleç, başlık ve kartları ekler; `ffmpeg` sesi dengeleyip birleştirir.
4. **Denetim:** biçim, süre, siyah ve donuk bölüm, ses seviyesi. Akıcılık ve ses tınısı elle izlenir.

## Bilinmesi gerekenler

- Yalnızca %100 Windows ölçeğinde ve 60 Hz ekranda denendi. Kare boyutu tutmazsa çekim hata verir.
- Çekim sırasında başka pencereye geçilirse `Ctrl+K` tetiklenmeyebilir; üretim uyarı yazıp devam eder.
- `QTimer` gerçek saatle çalışır; bildirimler çekimde sahne sonuna kadar ekranda tutulur.
- Örnek verideki tarihler üretim gününe göredir.
- Testler ayrıdır: `.venv\Scripts\python.exe -m pytest video\tests -q`.

## Lisanslar

| Bileşen | Koşul |
|---|---|
| Remotion | Bireyler ve en fazla 3 kişilik kuruluşlar için ücretsiz |
| Supertonic 3 modeli | OpenRAIL-M; kullanım kısıtları lisans ekinde. Videoda "seslendirme yapay zekâ ile üretilmiştir" notu bulunur, video açıklamasına da eklenmelidir |
| Plus Jakarta Sans | Depodaki yazı tipi |
| Müzik ve efektler | Betikle üretilir |

Kararların gerekçesi: [TASARIM.md](../../video/TASARIM.md).
