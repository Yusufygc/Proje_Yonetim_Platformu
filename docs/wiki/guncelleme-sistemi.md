# Uygulama İçi Güncelleme

Paketlenmiş uygulama açılışta GitHub Releases'te yeni sürüm arar; varsa "Yeni güncelleme var" penceresi çıkar. **Güncelle** denince kurulum dosyası indirilir, SHA-256 ile doğrulanır, uygulama kapanır ve kurulum dosyası sessiz kurulumla üstüne yazar; uygulama kendiliğinden yeniden açılır.

## Akış

1. **Yayın:** `vX.Y.Z` etiketi push edilince `.github/workflows/release.yml` kalite kapılarını koşar, `build_installer.py` ile `ProjeTakipPlatformu-Setup-X.Y.Z.exe` ve `.sha256` dosyalarını üretip GitHub Release olarak yükler ([[surum-yayinlama]]).
2. **Denetim:** `main_qml.py` pencere açılışından 3 sn sonra `update_viewmodel.checkForUpdates(True)` çağırır (`tests/` ve `build_verify` içinde `PROJE_TAKIP_NO_UPDATE_CHECK=1` ile devre dışıdır). Ağ yoksa, kullanıcı ayarı kapalıysa veya depoda henüz yayın yoksa (`releases/latest` → HTTP 404) sessiz geçer; Ayarlar'daki **Güncellemeleri Denetle** (`checkForUpdates(False)`) her sonucu gösterir.
3. **Karşılaştırma:** `services/update_service.py::release_to_update()` `releases/latest` etiketini `version.py` içindeki `__version__` ile sayısal olarak (`0.10.0 > 0.9.0`) kıyaslar. Taslak, ön sürüm (`prerelease`) ve `-beta`/`-rc` etiketleri yok sayılır.
4. **İndirme ve Doğrulama:** Arka planda (`Worker`) `%TEMP%\ProjeTakipUpdate` klasörüne `.exe.part` olarak indirilir. Boyut (400 MB sınırı ve Release boyutu eşleşmesi) ve **zorunlu SHA-256 özeti** (GitHub asset `digest` alanı veya `.sha256` yan dosyası; ikisi de yoksa güncelleme reddedilir) doğrulanır; uyuşmazlıkta dosya silinir.
5. **Kurulum ve Yeniden Başlatma:** `/SILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS /LOG=<klasör>\install.log` argümanlarıyla bağımsız süreç başlatılır (`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`). Ardından `quitRequested` sinyaliyle uygulama kapanır; `packaging/ProjeTakipPlatformu.iss` içindeki `Check: RelaunchAfterUpdate` (`/SILENT` için doğru, `/VERYSILENT` denemesi için yanlış) kurulum bitince uygulamayı yeniden açar.

### Windows Başlatmayı Engellerse (SAC Kurtarma)

`launch_installer()` önce `subprocess.Popen` (`CreateProcess`) ile başlatmayı dener. `WinError 4551` veya `1260` (Akıllı Uygulama Denetimi / grup ilkesi engeli) dönerse Gezgin'in çift tıklama yolu (`ShellExecuteW`) denenir; her ikisi de engellenirse `InstallerBlockedError` fırlatılır.

`UpdateViewModel` bu durumda `STATE_WAITING` durumuna geçer:
- 15 saniye aralıkla en fazla 40 kez (10 dakika) yeniden dener; diyalogda bekleme mesajı ve **Beklemeyi Bırak** düğmesi gösterilir.
- Engel kalkarsa kurulum otomatik başlar. Süre biter veya kullanıcı beklemeyi bırakırsa (`stopWaitingForBlock`) `STATE_BLOCKED` durumuna geçilir, dosya Windows Gezgini'nde seçili açılır (`explorer.exe /select,...`) ve **Sürüm Sayfası** düğmesi sunulur.

## Katmanlar ve Tercihler

- Akış: `UpdateDialog.qml` / `SettingsView.qml` → `UpdateViewModel` → `UpdateController` → `UpdateService` + `update_security.py`.
- Tercihler `%LOCALAPPDATA%\ProjeTakip\updates.json` (`check_on_startup`, `skipped_version`) dosyasında saklanır (`PROJE_TAKIP_HOME` ile izole edilebilir).

## Güvenlik

- İndirme ve yönlendirme (`_SafeRedirectHandler`) yalnızca `https://github.com/<owner>/<repo>/releases/download/...`, `api.github.com` ve `*.githubusercontent.com` adreslerine izin verir.
- Kurulum dosyası adı sıkı desene (`^ProjeTakipPlatformu-Setup-\d+\.\d+\.\d+\.exe$`) uymak zorundadır.
- İmzasız dağıtımda Windows SmartScreen/SAC uyarısı doğası gereği mümkündür; SHA-256 doğrulama kontrolleri kaldırılamaz.

İlgili: [[surum-yayinlama]], [[exe-dagitim-rehberi]]
