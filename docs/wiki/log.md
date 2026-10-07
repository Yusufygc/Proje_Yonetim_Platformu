# Wiki Kayıt Defteri

## [2026-10-08] REFACTOR | Emoji Yerine SVG İkon
- Çizim araç çubukları, Notlar'daki görsel düğmesi, Çıktılar'daki ataç, arama modalı, toast bildirimleri, analitik proje filtresindeki tik ve Ayarlar'daki dışa aktarma düğmesi emoji/metin sembolü yerine SVG ikon kullanıyor (21 yeni ikon dosyası). Yerelleştirme metinlerinden 📤/✅/❌ kaldırıldı.
- Bırakılanlar: tema düğmelerindeki 🌙/☀️ (istek), açılır liste ve ağaç oklarındaki `▼`/`▶`, `↳`, `◈`, `↵` metin sembolleri.
- **Hata düzeltmesi:** DrawingCanvas bölünürken "Çizim/Akış Şeması" mod düğmeleri sinyal yerine çubuğun kendi özelliğini değiştiriyordu; mod değişimi tuvale ulaşmıyordu. `modeSelected` sinyaline bağlandı, düğmeye tıklayan test eklendi. Pikselli karşılaştırma bu etkileşimi kapsamadığı için kaçmıştı.

## [2026-10-08] FIX | Koyu Tema Renk Hataları
- **Sarı satır:** Palet alfa değerleri CSS sırasıyla (`#RRGGBBAA`), Qt ise `#AARRGGBB` okuyor; `hover_overlay` (`#FFFFFF0D`) opak sarı çiziliyordu. `ThemeManager.color()` artık çıkışta çeviriyor (`*_alpha` tokenları da düzeldi).
- **Beyaz çubuk, okunmayan başlık:** `themeBridge.color("...")` slot çağrısı tema değişimini izlemiyordu; açıktan koyuya geçince bu alanlar eski renkte kalıyordu. 147 kullanım bildirimli property'ye çevrildi, tekrarını engelleyen test eklendi.
- **Kenar çubuğu:** Arama düğmesindeki emoji (yerelleştirme metninden) kaldırıldı; daralırken taşan yazı kısaltılıyor/kırpılıyor. Sürüm etiketi sabit `v0.1.1` yerine `appVersion`'dan okunuyor (`set_version.py` onu güncellemiyordu).
- **Arayüz:** Ayarlar'daki açık/koyu düğmeleri yalnızca emoji (ipucu metniyle); panodaki son fikirlerde emoji yerine SVG ikon.

## [2026-10-08] DOCS | Sürüm Yayınlama Süreci ve Kuralı
- `surum-yayinlama` wiki sayfası eklendi (sürüm numarası, yayın adımları, kontrol listesi, hata/geri alma tablosu, güvenlik).
- `Project_docs/RULES.md` §8 "Sürüm Yayınlama ve Güncelleme Kuralları" ve `CLAUDE.md` §11 eklendi: tek sürüm kaynağı, yalnızca etiketle yayın, yayınlanmış etiket değişmez, asistan açık istek olmadan etiket/push yapmaz.
- `kurallar-ve-sozlesmeler`, `guncelleme-sistemi`, `index` ve README güncellendi; yinelenen sürüm çıkarma anlatımı tek yere indirildi.

## [2026-10-07] FEATURE | Uygulama İçi Güncelleme
- **Akış:** Açılışta GitHub Releases denetimi, "Yeni güncelleme var" penceresi, boyut/SHA-256 doğrulamalı indirme, sessiz kurulum ve yeniden açılış. Ayrıntı: `guncelleme-sistemi`.
- **Kod:** `UpdateService`, `UpdateController`, `UpdateViewModel`, `UpdateDialog.qml`, Ayarlar'da "Güncellemeleri Denetle"; yerelleştirme anahtarları (tr/en) eklendi.
- **Yayın:** `scripts/set_version.py` (dört dosyada sürüm), `.github/workflows/release.yml` (etiketle derle ve yayınla), `installer/windows.iss` (kapatma ve sessiz kurulum sonrası yeniden açma).
- **CI:** `ruff` I001/F401/F811 bulguları giderildi (28 import bloğu); `uv.lock` `keyring` kaldırılınca yeniden üretildi.
- **İlk yayın:** `v0.1.1` GitHub Releases'te (161 MB installer, API SHA-256 özeti veriyor). İlk denemede PyInstaller spec'i vosk DLL'lerini sabit `.venv` yolunda arıyordu; yol kurulu paketten hesaplanır hale geldi. Etiket, yayın oluşmadan önce yeni commit'e taşındı.
- **Doğrulanmadı:** Gerçek güncelleme (installer'ın uygulamayı kapatıp yeniden açması) için eski sürümden yeniye geçiş denenmedi; bunun için `v0.1.1` kurulu iken `v0.1.2` yayınlanmalı.
- **Test takılması:** Çizim tuvali testi motoru silmeden bittiği için pytest kapanışta takılıyordu (CI'ı 15 dk kilitliyordu); test nesneleri açıkça siliyor, `faulthandler_timeout` ve CI zaman aşımı eklendi.

## [2026-10-07] REFACTOR | DrawingCanvas Bölündü
- **`DrawingCanvas.qml`** 1325 → 399 satır. Araç çubukları, metin düzenleme penceresi ve çizim mantığı `presentation/qml/views/memo/drawing/` altına taşındı (ayrıntı: `notlar-modulu`).
- Dışa açık API (`loadDrawingJson`, `getDrawingJson`, `undo`, `redo`, `clearCanvas`, `setBackgroundImage`) değişmedi; kullanılmayan `isEraser`, `lines`, `currentLine` takma adları kaldırıldı.
- **Doğrulama:** Bölmeden önce ve sonra 11 öğe türü, 11 canlı önizleme, şablon ve geri al/yinele sahneleri yazılım çizicisiyle piksel piksel karşılaştırıldı; özetler özdeş çıktı. Bu karşılaştırma geçici betikle yapıldı, depoya eklenmedi (font/platform farkıyla kırılgan olur). Kalıcı testler saf JS yardımcılarını kapsıyor.
- Fare ile gerçek sürükleme ve çift tıklama etkileşimi otomatik denenmedi; elle kontrol gerekir.

## [2026-10-07] REFACTOR | AnalyticsView Bölündü
- **`AnalyticsView.qml`** 640 → 274 satır. Bileşenler `presentation/qml/views/analytics/` altında: `KpiCard` (beş kopya KPI kartının yerine), `ProjectFilter` (proje açılır menüsü), `TimeSeriesChart` (zaman serisi çubuk grafiği).
- Dönem düğmeleri ve iki dağılım kartı yapıları farklı olduğundan (öncelik: renk noktası + toplam payı; proje: en büyüğe göre) ortak bileşene çevrilmedi.

## [2026-10-07] REFACTOR | IdeaViewModel Bölündü
- **`IdeaViewModel`** 250 → 151 satır, public üye 21 → 10: diyalog durumu ve kaydetme `IdeaDialogViewModel`'e (`ideaDialogViewModel` QML bağlamı) taşındı; `TaskDialogViewModel` ile aynı desen. Fikir önbelleğine `cached_idea()` ile erişilir.
- **Davranış:** Kayıttan sonraki fazladan `loadIdeas()` çağrısı kaldırıldı; liste zaten controller sinyalleri ve olay veri yoluyla yenileniyor.
- `IdeaDialog`, `IdeasView`, `IdeaDetailPanel` yeni bağlamı kullanıyor.
- Açık kalanlar: `DrawingCanvas.qml` (1325), `AnalyticsView.qml` (640).

## [2026-10-07] LINT | Ölü Kod Temizliği (Denetim Bulgusu 15) ve Arayüz Düzeltmeleri
- **Silinen modüller:** `core/workers/async_worker.py`, `domain/dtos/base_dto.py`, kökteki `quality.py` (kopya; `scripts/quality.py` kaldı), `presentation/qml/shell/TopHeader.qml`, `core/managers/secret_manager.py` + `keyring` bağımlılığı (DI kaydı, test, spec hiddenimport dahil; `uv.lock` yeniden üretilmeli: `uv lock`).
- **Silinen üyeler:** kullanılmayan controller senkron sarmalayıcıları, `load_all_tasks`/`all_tasks_loaded`, `TaskService.get_all_tasks`, `TaskRepository.get_all`, `IconManager.get_icon/Icons/try_instance`, `PreferenceManager` pencere-geometri ve son-proje metotları, `FontManager.loaded_families/mono_font`, `ThemeBridge.colors/accentHover/switchTheme`, kullanılmayan ViewModel property'leri, `config` UI sabitleri, `download_fonts.ensure_fonts`.
- **Dashboard:** `DashboardService` yedi gereksiz sorguyu (kullanılmayan sayaçlar ve listeler) artık çalıştırmıyor; sayaçlar tek `_count` yardımcısıyla hesaplanıyor.
- **Yerelleştirme:** Hiçbir yerde kullanılmayan 215 anahtar (eski Widgets arayüzü kalıntısı) iki dil dosyasından silindi; 221 anahtar kaldı, parite korunuyor.
- **Arayüz düzeltmeleri:** Geçmiş sekmesi metin taşması ve bölme sırasında kaybolan `anchors.fill` satırları; eksik `chevron-right.svg`; `StandardKey` kısayol uyarıları; büyütülen pencerede başlık çubuğunun ekran dışında kalması (`presentation/window_geometry.py`).
- **Bilinçli bırakılanlar:** `TaskViewModel.deleteChecklistItem`, `toggleChecklistItem`, `NavigationBridge.showToast`, `VoiceBridge.partialText` (özellik adayı API'ler); `resources/fonts` içindeki JetBrains Mono dosyaları (artık kullanılmıyor, indirme manifestinde duruyor).

## [2026-10-07] REFACTOR | Denetim Bulgusu 9'un Kalanı: Proje Detay Paneli ve Görev ViewModel'i Bölündü
- **`ProjectDetailPanel.qml`** 1786 → 126 satır. Bileşenler `presentation/qml/views/projects/detail/` altında: `ProjectHeader`, `ProjectStagesCard`, `ProjectTabBar`, yedi sekme (`ProjectSummaryTab`, `ProjectTasksTab`, `ProjectDecisionsTab`, `ProjectNotesTab`, `ProjectResourcesTab`, `ProjectOutputsTab`, `ProjectActivityTab`) ve dört modal (`ProjectDecisionDialog`, `ProjectNoteDialog`, `ProjectResourceDialog`, `ProjectOutputDialog`). Sekmeler `addRequested`/`editRequested` sinyalleriyle diyalogları panelden açar.
- **`TaskViewModel`** 448 → 296 satır: diyalog durumu ve kaydetme `TaskDialogViewModel`'e, panoya kopyalama metni `task_clipboard.collect_task_copy_lines` saf fonksiyonuna taşındı. QML'de `taskDialogViewModel` bağlamı eklendi.
- **`TasksView.qml`** araç çubuğu `tasks/TaskToolbar.qml` olarak ayrıldı (415 → 314 satır).
- **Paketleme:** PyInstaller spec dosyalarına `presentation/qml` veri klasörü eklendi (QML dosyaları pakete girmiyordu). Derleme denenmedi.
- Açık kalanlar: `DrawingCanvas.qml` (1325), `AnalyticsView.qml` (640), `IdeaViewModel` (30 metot).

## [2026-10-07] REVIEW+REFACTOR | Eski Qt Widgets Arayüzü ve QSS Altyapısı Kaldırıldı (Denetim Bulgusu 5)
- **Silindi:** `presentation/pages`, `widgets`, `dialogs`, `shell` (45 dosya, ~8,8 bin satır), `presentation/utils/{scroll_filter,ui_utils}.py`, `tests/test_ui_smoke.py`, `scripts/commit_all.py`, `resources/styles` (QSS), `resources/illustrations`, `resources/templates` (yalnızca eski sayfalar kullanıyordu).
- **Sadeleşti:** `main.py` yalnızca QML'i başlatır (`--legacy`/`--widgets` kolu yok); `FeaturePlugin` artık `factory` taşımaz, yalnızca navigasyon meta-verisi (`presentation/modules.py` veri tabanlı); `ThemeManager(themes_dir)` QSS üretimi, ikon token'ları ve `styles_dir` olmadan; `presentation/dimensions.py` yalnızca `FontFamily`; `config.STYLES_DIR` kalktı.
- **Dokümantasyon:** README, `tema-sistemi`, `gorevler-modulu`, `liste-siralama`, `sesli-komut`, `ikon-yonetimi`, `di-container`, `kurallar-ve-sozlesmeler`, `l10n-string-yonetimi`, `mimari-genel-bakis`, `index` güncellendi. `Project_docs/` altındaki tarihsel tasarım belgelerine dokunulmadı.
- **Bilinçli işlev kaybı:** Notlar/Fikirler/Projeler/Notlarım listelerindeki sürükle-bırak sıralama yalnızca eski arayüzdeydi; QML'de karşılığı yok. `reorder` altyapısı (kolonlar, servis/controller zinciri) korundu.

## [2026-10-07] REVIEW+FIX | Denetim Raporu Bulguları 6-10: Türkçe Arama, Kalite Kapıları, Testler, ViewModel Bölme
- **[6] Arama:** `core/text_normalization` (İ/I/ı/i katlama, LIKE joker kaçırma); SQLite bağlantısına `tr_fold` fonksiyonu; liste modelleri aynı yardımcıyı kullanıyor.
- **[7] Kalite:** mypy 87 hatadan 0'a; ruff F401/F821 açık; 20 kullanılmayan import temizlendi; `.github/workflows/ci.yml` (ruff, mypy, pytest); pre-commit mypy tüm paketlerde. `ruff.exe` bu makinede Uygulama Denetimi tarafından engelli olduğundan ruff ilk kez CI'da koşacak.
- **[7 ek] Dashboard hatası:** `DashboardViewModel` servis sözlüklerini ORM nesnesi sanıp süzüyordu; son fikirler boş, yüksek öncelikli görevler başlıksızdı. Düzeltildi.
- **[8] Test:** karar, kaynak, pano servisleri, controller hata yolları, çıktı ve not akışları (+12 test).
- **[9] ViewModel bölme:** karar, not, kaynak, çıktı ve etkinlik alt kayıtları `ProjectSubitemsViewModel`'e taşındı (QML bağlamı: `projectSubitemsViewModel`); `ProjectViewModel` 456 satırdan 289'a indi.
- **[10] Katman ve UI thread:** `ProjectViewModel` servise doğrudan gitmiyor, görevler `TaskController.load_tasks` ile arka planda; etkinlik ve ek yükleme/oluşturma `ProjectController` içinde `Worker` ile asenkron.

## [2026-10-07] REVIEW+FIX | Denetim Raporu Bulguları 1, 2, 4, 3: Yedek Bütünlüğü, Tam Dışa Aktarım, Hata Bildirimi, Üst Görev Durumu
`DENETIM_RAPORU_2026-10-07.md` bulgularından ilk dördü uygulandı:
- **[1] Yedek:** `BackupManager` artık `sqlite3.Connection.backup` kullanıyor; WAL modunda `-wal` dosyasındaki veri yedeğe giriyor (regresyon testi: `test_startup_backup_when_data_only_in_wal_should_include_it`). Ayarlar'daki "Veritabanını Yedekle" butonu ve `ExportService.backup_database`, `SettingsController.backup_database`, `SettingsViewModel.backupDatabase` kaldırıldı; otomatik açılış yedeği sürüyor.
- **[Ayarlar]** Veri Yönetimi kartındaki dosya yolu bilgi satırları (veritabanı, yedek, JSON konumu) ve `dbPath`/`getDefaultBackupPath` kaldırıldı.
- **[2] Dışa aktarım:** `ExportService.export_to_json` tüm kolonları yazıyor (`format_version: 2`): projeler (aşama, görev + checklist, karar, not, kaynak, ek, etiket, etkinlik), fikirler, proje-fikir bağları, memolar. Yeni kolonlar otomatik dışa aktarılır.
- **[4] Hata bildirimi:** `presentation/viewmodels/error_reporting.forward_errors_to_toast` ile görev, aşama, karar, not, kaynak, fikir ve memo controller hataları toast olarak gösteriliyor. Görev oluşturma başarısızsa "oluşturuldu" mesajı ve diyalog kapanışı artık yok.
- **[3] Üst görev durumu:** Alt görevi olan görevin durumu alt görevlerden türetilir; `TaskService` türetilen duruma elle geçişi `TaskValidationError` ile reddeder (yalnızca Engellendi/İptal elle verilebilir). Diyalogda üst görevler için "Otomatik / Engellendi / İptal" seçenekleri, satırda onay kutusu salt gösterge.

## [2026-10-07] FIX+FEATURE | QML Backend Uyumu: Görev Tipleri, Karar Durumları, Çıktılar, Düzenleme ve Geçmiş
Backend'de olup QML'de eksik ya da uyumsuz kalan alanlar giderildi:
- **[GÖREVLER]** Satır rozeti ve diyalog `TaskType` enum'u ile hizalandı (`GROUP`, `DOCUMENTATION`, `DESIGN`, `TEST`, `REVIEW` eklendi; enum'da olmayan `MILESTONE/EPIC/PHASE/SUBTASK` kaldırıldı). "Engellendi" durumunda `blocked_reason` alanı eklendi; öncelik ve tip filtreleri `TasksView`'a bağlandı. Hover butonları artık `HoverHandler` ile satırın tamamını izliyor.
- **[PROJE DETAY]** Karar, not ve kaynak kartlarına düzenleme eklendi (`updateDecision/updateNote/updateResource`). Karar durumları `DecisionStatus` enum'una çevrildi; eski `APPROVED/PROPOSED/REJECTED` kayıtlar gösterimde çevriliyor. Kaynak tipi `REPO` yerine `GITHUB`. Backend karar silmediği için karar kartındaki çöp kutusu "iptal et" (`x`) oldu. Yeni "Geçmiş" sekmesi `ActivityLog` kayıtlarını listeler.
- **[HATA]** Çıktılar sekmesi var olmayan `Attachment.file_name` alanını kullanıyordu; `caption` alanına geçirildi.
- **[ORTAM]** Conda kalıntıları temizlendi; çalışma ortamı proje kökündeki `.venv`. PyInstaller spec dosyalarından conda DLL listesi kaldırıldı.

## [2026-10-07] FEATURE+FIX | QML Notlar Çizim/Akış Şeması, Görevler Çoğaltma/Scroll, Header Sadeleştirme ve Analitik Listesi
QML modernizasyonu ve kullanıcı deneyimi odaklı kapsamlı özellik ve arayüz geliştirmeleri tamamlandı:
- **[NOTLAR & ÇİZİM] Zengin Çizim ve Algoritma Akış Şeması Araçları:**
  - `DrawingCanvas.qml` içine geometrik şekiller (dikdörtgen, yuvarlak dikdörtgen, daire, elips, eşkenar dörtgen/baklava, yıldız, üçgen) eklendi.
  - Algoritma/Akış Şeması blokları (Başla/Bitir terminali, İşlem kutusu, Karar/Koşul, Girdi/Çıktı paralelkenarı, Bağlayıcı çemberi ve Yön okları) eklendi.
  - Notlara ve çizim tuvaline resim ekleme desteği (`MemoViewModel.insertImage`, QML `FileDialog` ve tuval üzerine `drawImage` renderlama) entegre edildi.
  - Tuval araç çubuğu çift sıralı `Flickable` düzenine dönüştürülerek küçük pencere boyutlarında taşma ve buton ezilmeleri önlendi.
  - Metin düzenleme modalı (`textEditModal`) ekranın ortasına sabitlendi, "Tamam/İptal" butonlarının ekran dışına taşması engellendi.
- **[GÖREVLER] Kopyalama, Akıllı Daraltma ve Kaydırma Konumu:**
  - `TaskViewModel.copyTaskToClipboard` ve `duplicateTask` metodları ile Görev kartı butonları ve sağ tık menüsüne panoya kopyalama ve anında çoğaltma özellikleri eklendi.
  - `TaskListModel`: Alt görevleri bulunan ve alt görevleri dahil tamamlanmış (`DONE`) olan görev dallarının varsayılan olarak kapalı (collapsed) kalması sağlandı.
  - `TasksView.qml`: Durum değiştirme, silme ve kopyalama işlemlerinde model resetlendiğinde kullanıcının sayfa başına fırlatılmasını engelleyen `savedScrollY` kaydırma konumu koruyucusu eklendi.
- **[ERİŞİLEBİLİRLİK & METİN GİRİŞİ] AppTextInput ve Tooltipler:**
  - Tek satırlı metin alanlarında (`AppTextInput.qml`) yazı uzadığında metnin görünmez kalması sorunu `ensureVisible(cursorPosition)`, yatay fare tekerleği kaydırması ve hover tooltip ile çözüldü.
  - `TaskDialog`, `TaskItemDelegate` ve `ProjectListItem` bileşenlerindeki kırpılan uzun başlıklara `ToolTip` eklendi.
- **[ARAYÜZ TEMİZLİĞİ] Header Kaldırma & "Yeni Proje" Konsolidasyonu:**
  - `main.qml` içerisindeki gereksiz `TopHeader` bileşeni tamamen kaldırılarak sayfa kullanım alanı genişletildi.
  - `DashboardView`'e sayfa başlığı eklendi; ekranlardaki yinelenen "Yeni Proje" butonları temizlenerek sadece ana akışa bırakıldı.
- **[ANALİTİK] Proje Seçici Açılır Liste Görünümü:**
  - `AnalyticsView.qml` içindeki proje seçici açılır menüsünün Qt varsayılan stilinden kaynaklanan düşük kontrastlı yazı ve zifiri siyah hover sorunu giderildi; özel `contentItem`, `background`, seçili onay işareti (✓) ve genişletilmiş popup tasarımı uygulandı.

## [2026-07-02] PERF+FIX | Üretim öncesi denetim: lazy sayfa inşası, sessiz not hatası, Worker tutarlılığı
EXE paketlemeden önce başlangıç performansı + mimari/kod kalitesi denetimi yapıldı (3 paralel
keşif ajanı: başlangıç, mimari/kod kalitesi, algoritma/sorgu — algoritma tarafında gerçek sorun
bulunmadı, dokunulmadı). Bulunan ve düzeltilen gerçek sorunlar:
- **[EN BÜYÜK ETKİ] `MainWindow._setup_ui`** artık kayıtlı 9 sayfanın (Dashboard/Projeler/
  Fikirler/Görevler/Notlarım/Analitik/Arşiv/Bilgi/Ayarlar) TAMAMINI `window.show()`'dan önce
  inşa etmiyor — her biri kendi DB sorgusunu (`load_*`) tetikliyordu, kullanıcı aynı anda sadece
  1 sayfa görüyor. `_navigate_to` artık sayfayı yalnızca ilk ziyarette (`_build_and_register_page`)
  kuruyor, `ModuleRegistry.instance().plugins()` üzerinden `page_key` eşleşmesiyle buluyor.
- **[BLOCKER] `NoteController.error_occurred`** hiçbir yere bağlı değildi — not kaydetme/
  güncelleme/silme hatası kullanıcıya tamamen sessizce kayboluyordu. `NoteListWidget`'a
  `ideas_page.py`'deki mevcut desenle (`QMessageBox.critical`) bağlandı; regresyon testi eklendi.
- `project_list_item.py`'deki 2 `except Exception: pass` (sessiz hata yutma, CLAUDE.md ihlali)
  `logger.debug` ile görünür yapıldı.
- `alembic_runner.py::HEAD_REVISION` sabiti eskiydi (`0004`), gerçek head `0007_add_memo_sort_order`
  olarak düzeltildi (migration zinciri: 0001→...→0007).
- `note_service.py` artık plain `ValueError` yerine yeni `core/exceptions/note_exceptions.py`
  (`NoteValidationError`, `NoteNotFoundError`) fırlatıyor — Proje/Görev servisleriyle tutarlı.
- Not/Memo/Dashboard/Analitik controller'larının `load_*` metodları Worker'a taşındı
  ([[worker-altyapisi]]) — artık projenin kendi standardıyla tam tutarlı.

**Bilinçli olarak dokunulmayanlar:** `project_detail_panel.py`(441)/`settings_page.py`(433)/
`info_page.py`(413) satır sınırını hafif aşıyor, `PreferenceManager` 19 public metod (limit 15) —
çalışıyor/test edilmiş, bölünmesi gerçek fayda sağlamadan risk/süre maliyeti taşıyor, kullanıcı
kararıyla sadece not düşüldü. DEBUG log seviyesi, font/tema yükleme maliyeti, `OnboardingService`
tam tablo okuması — negligible.

## [2026-07-02] FEATURE | Yeni görev artık kardeş grubunun başına ekleniyor
`TaskService.create_task`, `order_index` belirtilmediğinde artık
`TaskRepository.first_order_index()` (yeni metod: en küçük `order_index - 1`, grup
boşsa `0`) çağırıyor — önceden `next_order_index()` (en büyük `order_index + 1`,
sona ekler) kullanılıyordu. WBS ağacında yeni görev artık en üstte görünüyor.
DONE'a geçen görevi kardeş grubunun sonuna alan `_apply_status_side_effects`
davranışı (aynı `next_order_index` metodunu kullanır) kasıtlı olarak
DEĞİŞTİRİLMEDİ — iki farklı semantik ("başa ekle" / "sona ekle") artık iki ayrı
repository metoduna ayrıldı, tek bir metodu iki amaç için paylaştırmak yerine.
`tests/test_mvp_core.py`'deki sıra testleri yeni beklenen değerlere (azalan/negatif
`order_index`) güncellendi.

## [2026-07-02] FEATURE | Rose+Violet tema paketleri, liste sıralama animasyonu, font buton grubu
`_THEME_PACKAGES`'e Rose (`#F43F5E`/`#E11D48`) ve Violet (`#8B5CF6`/`#7C3AED`)
eklendi (toplam 6 paket) — `resources/themes/{rose,violet}_{dark,light}.json`
`indigo_*` şablonunun kopyası, sadece accent+sidebar alanları farklı.
Notlar/Fikirler/Projeler/Notlarım listelerindeki sürükle-bırak sıralamaya
yumuşak geçiş eklendi: `DragReorderController._move_row` artık FLIP tekniğiyle
(`_capture_positions`/`_animate_shifted_rows`) konum değiştiren satırları
`QPropertyAnimation(b"pos")` ile 200ms'de kaydırıyor (önceden anlık zıplama
vardı). Native `QListWidget` kullanan Fikirler/Notlarım için önce `setAnimated(True)`
denendi, ama bu özellik PySide6 6.11'de `QListView`'da mevcut değilmiş
(`AttributeError`, üretimde yakalandı) — kaldırılıp yerine bırakma sonrası
taşınan satıra `fade_in_current_item()` ile opacity fade-in (0.4→1.0, 150ms)
eklendi. `DragReorderController._stop_existing_anim` içinde `shiboken6.isValid()`
kontrolü eklendi — `DeleteWhenStopped` politikasıyla doğal biten bir animasyona
tekrar `.stop()` çağrısı `RuntimeError` ile çöküyordu (üretimde yakalandı,
düzeltildi). Yeni `presentation/dimensions.py::Duration` sabiti
(`FAST/REFLOW/SLOW`) sadece yeni kodda kullanılıyor, mevcut animasyon kodu
(sidebar/toast/wbs_tree) dokunulmadı. Ayrıca: Roboto/Open Sans font kaynağı
jsDelivr `@fontsource` woff2'den google/fonts değişken (variable) TTF'lerine
çevrildi — woff2 dosyaları Qt'nin Windows DirectWrite arka ucunda yükleme
hatası veriyordu (`Failed to create DirectWrite face`, üretimde yakalandı).
Ayarlar sayfasında font "Uygula" butonu önizleme kutusuyla sıkı gruplandı
(`preview_group`, `Spacing.SM`).

## [2026-07-02] REFACTOR | Ayarlar sayfası: küratörlü tema paketleri + font boyutu kaldırma
"Ayarlar sayfasının esnekliği kullanışlı mı" tartışması sonucu tema/font sistemi
sadeleştirildi. 24 alanlı manuel `ThemeEditorDialog` + `ColorPickerButton` tamamen
silindi; `ThemeManager`'daki karşılıksız kalan CRUD metodları
(`is_builtin/list_themes/create_theme/update_theme/delete_theme/duplicate_theme/
export_theme/import_theme/get_palette_copy/preview_palette/restore_preview`)
kaldırıldı. "Hızlı Vurgu" gizli kopya mekanizması (`{isim}_vurgu_kopya` üreten
`_on_accent_quick_change`) kaldırıldı — bu, `light_vurgu_kopya`/`dark_vurgu_kopya`
karmaşasının kök nedeniydi. Yerine 4 küratörlü paket geldi: Slate/Indigo/Emerald/
Ocean × Koyu/Açık = 8 sabit builtin tema dosyası
(`resources/themes/{indigo,emerald,ocean}_{dark,light}.json`, yeni). Ölü/parçalı
dosyalar (`old_dark.json`, `old_light.json`, `yedek_light.json`,
`user/dark_vurgu_kopya.json`, `user/light_vurgu_kopya.json`) silindi;
`app/di_container.py`'deki tek seferlik `_migrate_legacy_theme_slots()` mevcut
kullanıcıların tercihlerini yeni paketlere sessizce taşıyor. Font boyutu ayarı
(fiilen ölüydü — 56+ QSS dosyasında sabit `font-size` px kuralı zaten
`QApplication.setFont()` boyutunu eziyordu) tamamen kaldırıldı; kullanıcı sadece
5 küratörlü aileden (Plus Jakarta Sans, Inter, Roboto, Open Sans, Segoe UI) seçim
yapıyor. Detay: [[tema-sistemi]].

## [2026-07-02] REFACTOR | Analitik KPI sadeleştirme ve görev tamamlanınca sıralama düzeltmesi
`AnalyticsService`'teki kullanılmayan tahmini/harcanan süre toplamları (`_time_total`,
`estimated_minutes_total`/`spent_minutes_total`) ve `analytics_page.py`'deki karşılık gelen
bant + `_fmt_minutes` yardımcı fonksiyonu kaldırıldı. `TaskService`: bir görev DONE
durumuna geçtiğinde `order_index`'i kardeş grubunun sonuna taşınıyor (WBS listesinde en
alta iner) — 2026-07-01'deki "Hızlı Görev Ekle" düzeltmesinin tamamlama akışına
genişletilmiş hali. `CLAUDE.md`'ye değişiklik sonrası `pytest` çalıştırma zorunluluğu
kural olarak eklendi.

## [2026-07-02] FIX + UX | Aşama tamamlama titremesi, rozet sadeleştirme, analitik tema senkronu
`ProjectsPage._on_stage_updated` bir aşama tamamlandığında tüm proje listesini ve detay
panelinin dört alt sekmesini (Görevler/Kararlar/Notlar/Kaynaklar) gereksiz yere yeniden
yüklüyordu — tıklamada tüm sayfa yenileniyormuş gibi titremeye yol açıyordu. Artık sadece
ilgili proje çekilip `ProjectListItem.update_project()` / `ProjectDetailPanel.refresh_header()`
ile yerinde güncelleniyor. Süreç aşamaları listesindeki ayrı durum rozeti (Tamamlandı/
Aktif/Bekliyor metni) kaldırıldı; tik ikonu + renkli nokta + glow zaten yeterli sinyal
veriyordu. Proje durum/öncelik rozetlerindeki dolgulu arka planlar kaldırıldı: durum artık
tek renkli nokta (`#status_dot`), öncelik kart çerçevesi rengiyle taşınıyor
(`card-priority`); erişilebilirlik için ikisi de tooltip'te metin olarak kalıyor. Proje
detay sekme çubuğunun seçili rengi "+ Ana Görev Ekle" ile aynı accent gradyana çekildi,
süreç aşamaları ile sekme çubuğu arasına ayraç çizgi eklendi. Analitik grafiklerinin arka
planı artık Qt'nin sabit koyu/açık temasına değil uygulamanın gerçek tema paletine bağlı
(dark modda beyaz kalma sorunu giderildi); grafik yükseklikleri ve panel boşlukları
daraltılarak sayfa scrollbar ihtiyacı azaltıldı; dönem butonlarının tanımsız `btn-toggle`
sınıfına stil eklendi. Detay: [[tema-sistemi]].

## [2026-07-02] FEATURE | Süreç aşamalarında tamamlanan aşamaya tik ikonu, aktif aşamaya glow
`StageTimelineWidget`: DONE durumundaki aşamalar artık daire yerine tik (checkmark) ikonu
gösteriyor (`IconManager.get_icon`, `try_instance()` ile headless/test ortamında güvenli
daireye düşüş); ACTIVE aşama kartına `stage_active` renginde accent glow
(`QGraphicsDropShadowEffect`) eklendi. `presentation/utils/ui_utils.apply_shadow`'a
opsiyonel `color` parametresi eklendi (varsayılan siyah gölge davranışı korunur).

## [2026-07-02] STYLE | Flat tasarım geçişi: renk paleti, rozetler, sidebar, buton/combobox durumları
Light temadaki bej/krem tonlar (`background`, `border`, `scrollbar_bg`, `sidebar_active`,
`h-sidebar_bg`) nötr gri palete çevrildi (kullanıcının aktif özel teması
`light_vurgu_kopya.json`'a da aynı düzeltme uygulandı). Kritik rozetler (Yüksek/Kritik
öncelik, Engellendi/İptal/Reddedildi durum) soluk alfa zeminden solid renk + beyaz metne
geçti. Sidebar aktif sekme sert çok duraklı gradyandan düz zemin + sol vurgu çubuğuna
geçti. `QComboBox`'a açık/kapalı/disabled/dropdown-item hover durumları, butonlara
`:pressed` durumu eklendi. Proje sekme çubuğundaki kutu modeli asimetrisi (checked/
unchecked arası border kalınlık farkı, dikey hizalama hatasına yol açıyordu) giderildi.
`section-header` tipografisi büyütüldü/koyulaştırıldı. WBS tablo başlığı font boyutu
artırıldı. Detay: [[tema-sistemi]].

## [2026-07-01] FIX | Notlarım (memo) sayfasında sürükle-sırala eksikti
Kullanıcı "Notlarım sayfasında sıralama çalışmıyor" diye bildirdi; incelemede
`MemoPage`'in hiç sıralama mekanizması olmadığı görüldü (önceki liste-sıralama
işi yalnızca Notlar/Fikirler/Projeler'i kapsamıştı). `Memo.sort_order` kolonu
eklendi (migration `007_add_memo_sort_order`, `updated_at` sırasına göre
backfill), `MemoRepository`/`MemoService`/`MemoController.reorder` zinciri ve
`MemoPage`'te `QListWidget.setDragDropMode(InternalMove)` + `model().rowsMoved`
(Fikirler ile aynı desen) eklendi. Detay: [[liste-siralama]].

## [2026-07-01] FEATURE + FIX | Liste sıralama, soluk proje kartı, hızlı ekle sıra düzeltmesi
Notlar/Fikirler/Projeler listelerinde sürükle-bırak sıralama: `Note`/`Idea` modellerine
`sort_order` kolonu (migration `006_add_list_sort_order`, backfill dahil), `Project`
zaten sahip olduğu `display_order`'ı kullanıyor. UI: manuel `QVBoxLayout` listeleri
(Notlar, Projeler) için yeniden kullanılabilir `DragReorderController`
(`presentation/widgets/drag_reorder.py`); Fikirler zaten `QListWidget` olduğundan
`InternalMove` moduyla çözüldü. Detay: [[liste-siralama]]. Ayrıca: Projeler sayfası kart
görünümü artık soluk dolgu zeminli (`project_list_item.qss`) — kartlar birbirinden
görsel olarak ayrışıyor. Bugfix: "Hızlı Görev Ekle" ile eklenen görev artık her zaman
kardeş grubunun sonuna ekleniyor (`TaskRepository.next_order_index`,
`TaskService.create_task` artık `order_index`'i hiç boş bırakmıyor); önceden hesaplanmadığı
için varsayılan `0` kalıp listenin başına/ortasına düşüyordu.

## [2026-06-30] FEATURE | Sesli komut (speech-to-text)
Vosk çevrimdışı motoru ile mikrofon dikteleme: `SpeechToTextService` (lazy model yükleme) →
`TranscriptionWorker` (`QThreadPool`, [[worker-altyapisi]] deseni, sürekli döngü + `stop()`) →
`VoiceInputButton`/`attach_voice_button` (`QLineEdit` + `QTextEdit` ortak destek). Görev/fikir
başlığı, hızlı görev ekle ve tüm uzun açıklama/not alanlarına 🎤 eklendi. Model
(`vosk-model-small-tr-0.3`, ~35 MB) `resources/models/` altında, repoya dahil değil. Hata
yolları (`SpeechModelNotFoundError`, `MicrophoneUnavailableError`) toast'a bağlandı, UI
bloklanmıyor. Detay: [[sesli-komut]].

## [2026-06-13] UX | Palet geçişi sonrası kontrast ve hiyerarşi onarımı
Sidebar yeni token seti (`sidebar_text`, `sidebar_text_active`, `sidebar_hover_bg`, `sidebar_active_bg`); aktif öğe 3px sol kenar + opak metin desenine geçti (alpha blend kaldırıldı). Koyu temada `text_secondary` lavanta, `border` ayrı ton, `stage_done` success yeşili. Stat kart KPI değeri primary + büyük punto. Stage row 36px sabit (`Size.STAGE_ROW_H`). Tab stili browser-tab desenine geçti. Stage butonları StringManager'a taşındı. Detay: [[tema-sistemi]], `Project_docs/UX_TEMA_GERI_BILDIRIMI_2026-06-13.md`.

## [2026-06-13] REFACTOR | Constructor injection UI'da tamamlandı
9 widget/sayfa + `Sidebar` + `Toast` + `SettingsPage` artık `theme/icons/strings/prefs/event_bus`'ı constructor parametresinden alıyor; modules.py factory'leri DI'den besler. `DIContainer`'a `strings` ve `icons` public property'leri eklendi. Sadece `MainWindow` (kompozisyon kökü) `getattr(di) or instance()` fallback'i tutuyor. Detay: [[di-container]], [[yol-haritasi]].

## [2026-06-13] FEATURE | Dil seçici ve İngilizce çeviri
`strings.en.json` (249 anahtar) + ayarlar sayfasında dil combobox'ı + `PreferenceManager.save/load_language` + bootstrap'te kalıcı dil uygulama. Locale parite testi eklendi (anahtar + placeholder eşleşmesi). Karar: canlı retranslate yerine yeniden başlatma. Detay: [[l10n-string-yonetimi]].

## [2026-06-13] UPDATE | L10N migrasyonu TAMAMLANDI
Kalan 16 dosya (3 küçük dialog, 4 liste widget'ı, dashboard/ideas/projects/info sayfaları, search, stage_timeline, project_list_item, main_window, modules) StringManager'a taşındı. Ratchet ALLOWLIST boşaldı; `strings.tr.json` 247 anahtar. SearchDialog sinyali dilden bağımsız tip koduna geçti; idea_dialog'daki sözlük→fonksiyon dönüşümünün ideas_page'de kırdığı import onarıldı. `# l10n: log` pragma'sı eklendi. Detay: [[l10n-string-yonetimi]].

## [2026-06-12] UPDATE | L10N migrasyonu 2. dalga
`project_detail_panel`, `idea_dialog`, `task_dialog`, `settings_page` StringManager'a taşındı; dialoglar `form_utils` (make_combo_column, select_combo_data, set_field_error) kullanacak şekilde sadeleştirildi. Ratchet allowlist 21→17. Detay: [[l10n-string-yonetimi]].

## [2026-06-12] UPDATE | P3 tamamlandı
DIContainer üç registry'ye bölündü (`di_registries.py`, `__getattr__` ile geriye dönük uyum); IconManager `QSvgRenderer` + `Icons` sabitleri + `try_instance()` aldı; `commit_all.py`/`download_assets.py` `scripts/` altına taşındı. Detay: [[di-container]], [[ikon-yonetimi]], [[yol-haritasi]].

## [2026-06-12] INGEST | Wiki bilgi tabanı kuruldu
İlk 11 sayfa oluşturuldu: mimari, DI, EventBus, worker, veritabanı, tema, L10N, ikon, görevler modülü, kurallar, yol haritası. Kaynak: senior analiz raporu (`Project_docs/SENIOR_ANALIZ_RAPORU_2026-06-12.md`) + P0-P2 refactor oturumu.

## [2026-06-12] UPDATE | P2 tamamlandı
`BaseRepository[T]` ile 12 repo sadeleştirildi; StringManager'a `language_changed` sinyali eklendi; L10N ratchet testi (`tests/test_l10n_no_hardcoded.py`) yazıldı; `project_dialog` string migrasyonu yapıldı. Detay: [[veritabani-katmani]], [[l10n-string-yonetimi]].

## [2026-06-12] UPDATE | P0-P1 tamamlandı
EventBus WeakMethod'a geçirildi ([[event-bus]]); `tasks_page` pakete bölündü ([[gorevler-modulu]]); monolitik `base.qss` 8 modüle ayrıldı ([[tema-sistemi]]); tema sözleşmesi bağlantıları eklendi.

## [2026-06-12] DECISION | Graphify zorunluluğu kaldırıldı
CLAUDE.md §3 silindi (kullanıcı kararı). Mimari dokümantasyon artık bu wiki üzerinde tutuluyor.

## [2026-06-12] DECISION | Yazma işlemleri senkron kalacak
SQLite WAL'de yazmalar ms seviyesinde; Worker'a taşımanın sinyal sıralaması riski kazancı aşıyor. Detay: [[worker-altyapisi]].
