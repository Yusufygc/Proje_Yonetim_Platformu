# EXE Dağıtımı ve Kararlı EXE Mimarisi

Bu belge, Windows 11 Akıllı Uygulama Denetimi (Smart App Control, SAC) engellerine takılmayan **kararlı exe** yapısını, Inno Setup 6 paketlemesini ve doğrulama kapısını açıklar. Gerekçe ve yayın/güncelleme ilişkisi: [[surum-yayinlama]], [[guncelleme-sistemi]].

## 1. Kararlı EXE ("Bayt Bayt Aynı" Çalıştırılabilir Dosya)

Windows 11'de SAC imzasız çalıştırılabilir dosyaları SHA-256 özetine göre değerlendirir. Uygulama kodu her sürümde exe'nin içine gömülürse her sürüm yeni ve onaylanmamış bir exe özeti üretir; güncelleme başarılı olsa bile yeni sürüm açılmayabilir.

Bu yüzden uygulama mantığı exe'nin dışına çıkarılır (`--onedir --debug=noarchive`):
- **Sabit giriş betiği (`packaging/launcher.py`):** Yalnızca `from main import main; main()` içerir ve **asla değiştirilmez**.
- **Sabit sürüm kaynağı (`packaging/launcher_version_info.txt`):** `1.0.0.0` olarak sabitlenir; ürün sürümü kurulum dosyasında, Windows kayıt defterinde ve uygulama ayarlarında (`version.py`) görünür.
- **Sabit zaman damgası (`LAUNCHER_EPOCH = 1700000000`):** `build_exe.py`, PyInstaller çalıştırmadan hemen önce `SOURCE_DATE_EPOCH` ortam değişkenini ayarlar.
- **Sabit bağımlılıklar ve satır sonları:** `requirements-lock.txt` geçişli bağımlılıkları sabitler; `.gitattributes` giriş betiği ve sürüm kaynağı için `eol=lf` zorlar.
- **Qt budaması (`prune`):** Kullanılmayan Qt6 DLL/QML modülleri derleme sonrası `_internal/PySide6` altından silinir (`QtSvg`, `QtQuick*`, `QtQml*`, `QtNetwork` korunur). Bu işlem exe dışında yapıldığından exe özetini etkilemez.

## 2. Onay Kapısı (`packaging/launcher.sha256`)

`build_exe.py` derleme bitince `ProjeTakipPlatformu.exe` özetini `packaging/launcher.sha256` ile karşılaştırır:
- Özet eşleşirse derleme ve yayın devam eder.
- Dosya yoksa veya özet değişmişse `sys.exit(1)` ile derleme/CI yayınını durdurur.
- Exe'nin bilerek değiştiği nadir durumlarda (Python/PyInstaller/simge değişikliği):
  1. Önce yerel makinede derleyip `build_verify.launch_check(Path("dist/ProjeTakipPlatformu/ProjeTakipPlatformu.exe"))` ile çalıştığını doğrula.
  2. Engellenirse yalnızca `build_exe.py` içindeki `LAUNCHER_EPOCH` değerini değiştirip yeniden dene.
  3. Açılan özeti `python build_installer.py --update-launcher-hash` ile kaydet ve `tests/test_release_packaging.py` sabitlerini güncelle.

## 3. Tek Komutla Kurulum ve Doğrulama (`build_installer.py` & `build_verify.py`)

```powershell
python build_installer.py
```

1. `build_exe.build_executable()` exe'yi derler, Qt budaması yapar ve özet kapısından geçirir.
2. `build_verify.launch_check()` exe'yi `PROJE_TAKIP_NO_UPDATE_CHECK=1` ve geçici `PROJE_TAKIP_HOME` ortamıyla başlatıp 5 saniye çökmeden çalıştığını doğrular (kullanıcı verisine dokunmaz).
3. Inno Setup 6 (`packaging/ProjeTakipPlatformu.iss`, `/DAppVersion=<__version__>`) ile `dist/installer/ProjeTakipPlatformu-Setup-<sürüm>.exe` ve `.sha256` dosyasını üretir.
4. `build_verify.installer_check()` kurulum dosyasını geçici dizine sessizce (`/VERYSILENT`) kurar, kurulu exe'yi açar ve `unins000.exe` kaldırıcısını da test eder; deneme öncesi gerçek kurulumun Uninstall kayıt defteri ve Başlat menüsü kısayollarını yedekleyip `try/finally` ile geri yazar.

`CI` ortam değişkeni ayarlıysa (`release.yml` içinde) veya `--no-verify` verilirse SAC denemesi atlanır, ancak özet kapısı asla atlanmaz.

İlgili: [[surum-yayinlama]], [[guncelleme-sistemi]]
