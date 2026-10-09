# Uygulama İçi Güncelleme

Paketlenmiş uygulama açılışta GitHub Releases'te yeni sürüm arar; varsa "Yeni güncelleme var" penceresi çıkar. **Güncelle** denince kurulum dosyası indirilir, doğrulanır, uygulama kapanır ve installer sessiz kurulumla üstüne yazar; uygulama kendiliğinden yeniden açılır.

## Akış

1. **Yayın:** `v0.2.0` gibi bir etiket push edilince `.github/workflows/release.yml` testleri koşar, PyInstaller ve Inno Setup ile `ProjeTakipPlatformuSetup.exe` üretir ve GitHub Release olarak yükler.
2. **Denetim:** `UpdateViewModel.checkOnStartup()` açılıştan 3 sn sonra çağrılır (`main_qml.py`). Yalnızca paketlenmiş uygulamada çalışır; kaynak koddan denemek için `PROJE_TAKIP_UPDATE_CHECK=1`. Ağ yoksa sessiz geçer.
3. **Karşılaştırma:** `UpdateService.check_for_update()` `releases/latest` yanıtındaki etiketi `app/config.py` `APP_VERSION` ile sayısal olarak (`0.10.0 > 0.9.0`) karşılaştırır. Ön sürüm ve taslaklar `latest` sonucunda yoktur.
4. **İndirme:** Arka planda (`Worker`), ilerleme çubuğuyla. Boyut ve (GitHub'ın verdiği) SHA-256 özeti doğrulanır; uyuşmazsa dosya silinir.
5. **Kurulum:** `/SILENT /SUPPRESSMSGBOXES /CLOSEAPPLICATIONS /LOG=<indirme klasörü>\install.log` ile bağımsız süreç başlatılır (sessiz kurulum hata göstermez; neden `%TEMP%\ProjeTakipUpdate\install.log` içinde), `quitRequested` ile uygulama kapanır. `installer/windows.iss` içindeki `Check: WizardSilent` satırı kurulumdan sonra uygulamayı yeniden açar.

## Katmanlar

`UpdateDialog.qml` → `UpdateViewModel` → `UpdateController` → `UpdateService` (`services/update_service.py`). Ayarlar sayfasında "Güncellemeleri Denetle" düğmesi elle denetler ve sonucu bildirir.

## Güvenlik

- İndirme adresi yalnızca `https://github.com/<repo>/releases/download/...` olabilir; başka adres reddedilir.
- Token gerekmez (depo public). İmzasız installer için Windows SmartScreen uyarısı çıkabilir; kod imzalama sertifikası ayrı bir konudur.

## Sürüm çıkarma

Adımlar, kontrol listesi ve geri alma: [[surum-yayinlama]]. Etiket ile `APP_VERSION` farklıysa release iş akışı yayın yapmadan durur.

## Sınırlar

- Yalnızca Windows. Otomatik güncelleme kapatma ayarı ve "bu sürümü atla" yoktur; "Sonra" yalnızca o açılış için pencereyi kapatır.
- Release iş akışı henüz bir kez bile koşmadı; ilk etiket çıkışı doğrulama niteliğindedir.
