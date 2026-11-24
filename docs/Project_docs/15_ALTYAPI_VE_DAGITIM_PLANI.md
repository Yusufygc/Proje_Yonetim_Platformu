# 15. Altyapı, Veritabanı ve Dağıtım Planı

Bu doküman, **Proje Yönetim ve Takip Platformu**'nun platform bağımsızlığını (database-agnostic), veri güvenliğini, kullanıcı tercihlerinin sürekliliğini ve son kullanıcıya sorunsuz bir şekilde paketlenip dağıtılmasını sağlayacak mimari altyapı standartlarını belirler.

---

## 1. Veritabanı ve Şema Yönetimi (ORM & Migrations)

Uygulamanın veri katmanı, belirli bir veritabanı motoruna sıkı sıkıya bağlı (tightly coupled) kalmamalıdır. Bu esnekliği sağlamak ve platform bağımsızlığını güvenceye almak için ham SQL sorguları yerine Nesne-İlişkisel Eşleme (ORM) ve şema versiyonlama altyapısı kurulacaktır.

### 1.1. SQLAlchemy Entegrasyonu
* **Katman Bağımsızlığı:** Veritabanı motoru (SQLite, PostgreSQL, MySQL veya Cloud DB) ne olursa olsun, domain modelleri ve repository katmanı değişmeyecektir.
* **Modelleme:** Tüm veritabanı tabloları, SQLAlchemy `DeclarativeBase` kullanılarak Python sınıfları olarak tanımlanacaktır.
* **Bağlantı Yönetimi:** `infrastructure/database/db_manager.py` içerisinde bir `scoped_session` veya `sessionmaker` fabrikası kurulacak, thread-safe oturum yönetimi sağlanacaktır.

### 1.2. Alembic ile Veritabanı Göçleri (Migrations)
* **Şema Versiyon Kontrolü:** Kod tabanındaki model değişiklikleri (örn: `parent_task_id` alanının eklenmesi) veritabanına el ile değil, Alembic göç scriptleri vasıtasıyla yansıtılacaktır.
* **Geri Döndürülebilirlik:** Her göç adımı `upgrade()` ve `downgrade()` metodlarını içerecektir. Bu sayede veritabanı şeması güvenle ileri veya geri sürümlere taşınabilecektir.
* **Çalışma Zamanı Kuralı:** Uygulama ilk açıldığında, `Alembic API` yardımıyla mevcut veritabanının sürümünü kontrol edecek ve eksik göçleri otomatik olarak (kullanıcıya fark ettirmeden) arka planda koşturacaktır.

---

## 2. Uygulama Durumu ve Ayar Yönetimi (State Persistence)

Kullanıcının arayüzle olan etkileşimleri sonucunda oluşan durumların (state) ve kişisel ayarların, uygulama kapatılıp açıldığında korunması premium hissinin temel şartlarındandır.

### 2.1. PreferencesManager Tasarımı
* **Depolama Alanı:** İş mantığına ait olmayan UI durumları veritabanında tutulmayacaktır. Bunun yerine işletim sisteminin yerel konfigürasyon mekanizmaları kullanılacaktır.
* **Teknoloji:** PySide6'nın yerleşik `QSettings` sınıfı kullanılacaktır. `QSettings`, ayarları Windows'ta *Kayıt Defteri (Registry)*, macOS'ta *Core Application Preferences (.plist)*, Linux'ta ise *INI konfigürasyon dosyaları* üzerinde yerel olarak saklar.
* **Saklanacak Durum Parametreleri:**
    * Ana pencerenin son genişlik, yükseklik ve ekran pozisyonu verileri.
    * Sidebar panelinin açık mı yoksa daraltılmış (collapsed) mı olduğu bilgisi.
    * Aktif olarak seçilmiş olan tema konsepti (Dark, Light vb.).
    * Sol proje listesindeki son seçili kalan projenin ID'si (uygulama açıldığında doğrudan o projeyi getirmek için).

---

## 3. Dağıtım ve Paketleme Stratejisi (Deployment & Packaging)

Geliştirilen Python ve PySide6 uygulamasının, son kullanıcının bilgisayarında Python çalışma ortamı, kütüphaneler veya bağımlılıklar kurulu olmasına gerek kalmadan tek bir paket halinde çalışabilmesi gerekir.

### 3.1. Çalıştırılabilir Dosya (Executable) Üretimi
* **Araç Seçimi:** Projenin derleme ve paketleme süreci için **PyInstaller** veya donanım hızlandırmalı/C optimize derleme yapan **Nuitka** kullanılacaktır.
* **Paketleme Kuralları:**
    * Uygulama `--onedir` (klasör yapısı) veya `--onefile` (tek executable) modunda derlenecektir. MVP için performans avantajından dolayı `--onedir` tercih edilip, bir yükleyici (installer) içine gömülecektir.
    * `resources/` (ikonlar, yazı tipleri, dil dosyaları) klasörleri derleme scriptine (`.spec` dosyası) açıkça eklenerek paket içerisine dahil edilecektir.
    * Terminal penceresinin açılmaması için `--windowed` / `--noconsole` bayrağı aktif edilecektir.

### 3.2. Yükleyici (Installer) Sihirbazı
* **Platform Hedefleri:** İlk fazda Windows için **Inno Setup** veya **NSIS** kullanılarak bir `.exe` kurulum sihirbazı oluşturulacaktır. Bu sihirbaz kullanıcının masaüstüne ve başlat menüsüne kısayol atayacaktır.

---

## 4. Veri Güvenliği ve Hassas Bilgiler (Security)

Uygulama yerel odaklı çalışsa dahi, ileride eklenebilecek entegrasyonlar (GitHub senkronizasyonu vb.) ve kullanıcı verilerinin güvenliği için baştan güvenlik bariyerleri içermelidir.

### 4.1. İşletim Sistemi Güvenli Kasası (Keyring Entegrasyonu)
* **Hassas Veri Kuralı:** Kullanıcıya ait harici API anahtarları (örn: GitHub Token), şifreler veya bulut senkronizasyon yetkilendirme bilgileri asla veritabanında veya `QSettings` içinde düz metin (plain text) olarak saklanamaz.
* **Çözüm:** Python `keyring` kütüphanesi kullanılarak bu veriler işletim sisteminin şifreli güvenli kasasına yazılacaktır:
    * Windows: *Credential Manager (Kimlik Bilgisi Yöneticisi)*
    * macOS: *Keychain Access (Anahtar Zinciri Erişimi)*
    * Linux: *Secret Service API / KWallet*

### 4.2. Veritabanı Şifreleme Altyapısı (Geleceğe Yatırım)
* **SQLCipher Esnekliği:** İleride projelerin ticari gizlilik içermesi veya kullanıcının veritabanını tamamen şifrelemek istemesi durumunda, SQLAlchemy bağlantı string'i `sqlite+asynch://` yerine `sqlite+sqlcipher://` sürücüsüne kolayca geçirilebilecek mimari esneklikte kurulacaktır.

---

## 5. Otomatik Yedekleme Sistemi (Auto-Backup System)

Kişisel veri yönetim uygulamalarında en kritik risklerden biri veri kaybıdır. Bilgisayarın aniden kapanması, disk arızaları veya kullanıcının veritabanı dosyasını (`app.db`) kazara silmesi ihtimaline karşı proaktif bir koruma mekanizması işletilecektir.

### 5.1. Yaşam Döngüsü Yedekleme Mantığı
* **Zamanlama:** Uygulama her ilk açıldığında (App Lifecycle Startup), ana veritabanı dosyasının bütünlüğü kontrol edilecek ve otomatik olarak bir yedek alınacaktır.
* **Depolama Düzeni:** Uygulamanın kurulu olduğu dizinde gizli bir `.backups/` klasörü oluşturulacaktır. Yedek dosyaları `backup_Ymd_HMS.db` (Yıl-Ay-Gün_Saat-Dakika-Saniye) formatında zaman damgasıyla saklanacaktır.
* **Rotasyon Kuralı:** Kullanıcının diskini gereksiz yere şişirmemek adına klasörde maksimum 5 yedek dosyası tutulacaktır. 6. yedek alınırken en eski tarihli yedek dosyası sistemden otomatik olarak temizlenecektir.
