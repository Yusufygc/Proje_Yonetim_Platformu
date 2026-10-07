# Kapsamlı Sistem Denetim Raporu — 2026-10-07

Kaynak şablonlar: `AI-Gelistirme-Metodolojisi.md` (Bölüm 1-3, 5, 7: wiki, kod inceleme, mantık hatası analizi) ve `V2-GenelSablon.md` (ölçüm eşikleri, bulgu şablonu, rapor yapısı).
Kapsam: `qml` dalı, commit `8d3df99`. Bu rapor **bulguları raporlar, hiçbirini uygulamaz**; Metodoloji Bölüm 2.3 gereği onay beklenir.

## Uygulama Durumu

| Bulgu | Durum |
|-------|-------|
| 1 Yedekleme | ✅ Çözüldü (sqlite yedekleme API'si; arayüzdeki manuel yedek butonu kaldırıldı, otomatik açılış yedeği sürüyor) |
| 2 JSON dışa aktarım | ✅ Çözüldü (tüm tablolar, `format_version: 2`) |
| 4 Controller hata sinyalleri | ✅ Çözüldü (görev, aşama, karar, not, kaynak, fikir, memo); dashboard ve analytics yalnızca log |
| 3 Üst görev durumu | ✅ Çözüldü (servis reddediyor, arayüz "Otomatik" seçeneği sunuyor) |
| 5-20 | ⏳ Bekliyor |

Aşağıdaki bulgu metinleri denetim anındaki durumu anlatır.

## Tarama Planı ve Yöntem

- **Dizin ağacı (git takipli):** 189 kaynak `.py` (test ve migration hariç), 9 test dosyası, 7 Alembic sürümü, 36 `.qml`, 16 wiki sayfası, 12 tema JSON, 2 dil dosyası.
- **Giriş noktaları:** `main.py` (varsayılan QML, `--legacy` ile eski Widgets), `main_qml.py`, `app/di_container.py`, `app/di_registries.py`.
- **Ölçüm:** `ast` ile fonksiyon uzunluğu, siklomatik karmaşıklık, parametre sayısı, iç içe derinlik, sınıf ve dosya boyutu, import sayısı. Eşikler V2-GenelSablon.md tablosundaki değerler.
- **Çalıştırılarak doğrulananlar:** `mypy` (tüm paketler), `pytest` (63 test geçiyor), iki davranış denemesi (yedek bütünlüğü, ebeveyn görev durumu). Bu denemelerin çıktısı ilgili bulgularda yazıyor.
- **Çalıştırılamayanlar:** `ruff.exe`, Windows Uygulama Denetimi ilkesi tarafından engellendi (`WinError 4551`); F401/F841 sayımı yapılamadı.

---

## Bölüm A — Yönetici Özeti

Mimari iskelet sağlam: katmanlı yapı (Model → Repository → Service → Controller → ViewModel → QML), DI konteyneri, olay veri yolu, Alembic, tema ve l10n sistemi var ve dokümante. Asıl riskler dört yerde toplanıyor. Birincisi **veri güvenliği**: arayüzdeki "Veritabanını Yedekle" butonu uygulama açıkken **boş tablolu** dosya üretiyor, "JSON dışa aktar" ise notların içeriğini, kararların metnini ve görev açıklamalarını yazmıyor. İkincisi **iş mantığı**: ebeveyn görevin durumu elle değiştirilemiyor, her kayıtta alt görevlerden yeniden hesaplanıp eziliyor. Üçüncüsü **çift arayüz**: eski Widgets arayüzü (~8,8 bin satır) ve QML arayüzü (~13 bin satır) birlikte bakım yükü yaratıyor. Dördüncüsü **kalite kapıları**: ruff'ta F401/F821 kapalı, mypy tüm kodda 90 hata veriyor, CI yok, 12 controller'dan 9'unun hata sinyali hiçbir ViewModel'e bağlı değil.

| # | Bulgu | Öncelik | Boyut | Efor | Etki |
|---|-------|---------|-------|------|------|
| 1 | Yedekleme WAL modunda boş/eksik dosya üretiyor | 🔴 | Production | S | Çok yüksek |
| 2 | JSON dışa aktarım "tüm veri" diyor, çoğunu yazmıyor | 🟠 | Production | M | Yüksek |
| 3 | Ebeveyn görev durumu elle değiştirilemiyor | 🟠 | Mantık | M | Yüksek |
| 4 | Controller hata sinyalleri 12'den 9'unda bağlı değil | 🟠 | Test/Hata yönetimi | M | Yüksek |
| 5 | İki paralel arayüz (Widgets + QML) | 🟠 | Mimari | XL | Yüksek |
| 6 | Türkçe harflerde büyük/küçük harf duyarsız arama bozuk | 🟠 | Yerel bağlam | M | Orta-yüksek |
| 7 | Kalite kapıları devre dışı (ruff, mypy, CI) | 🟠 | Production | M | Yüksek |
| 8 | Test kapsamı dar; controller ve 4 servis hiç test edilmiyor | 🟠 | Test | L | Yüksek |
| 9 | God object ViewModel ve QML dosyaları | 🟠 | Mimari | L | Orta-yüksek |
| 10 | ViewModel katman atlıyor, UI thread'de senkron DB | 🟡 | Mimari | M | Orta |
| 11 | Çift migration sistemi, ham SQL | 🟡 | Mimari | M | Orta |
| 12 | Analitik günlük kovaları UTC | 🟡 | Yerel bağlam | S | Orta |
| 13 | Geniş `except Exception` ve controller kopyala-yapıştır | 🟡 | Kod kalitesi | M | Orta |
| 14 | Bağımlılık yönetimi (dev araçlar runtime'da, pin yok, çift liste) | 🟡 | Güvenlik/Dağıtım | S | Orta |
| 15 | Ölü kod ve ölü bağımlılık (`keyring`, `SecretManager`) | 🟡 | Kod kalitesi | S | Orta |
| 16 | `recalculate_hierarchy` her kayıtta tüm projeyi tarıyor | 🟡 | Performans | M | Orta |
| 17 | Eşik aşan fonksiyonlar ve sınıflar | 🟡 | Kod kalitesi | L | Orta |
| 18 | `Worker` `co_varnames` kontrolü kırılgan | 🟡 | Kod kalitesi | S | Düşük-orta |
| 19 | `os.startfile` ile rastgele yol açma | 🟡 | Güvenlik | S | Düşük-orta |
| 20 | Wiki ve CLAUDE.md metodolojiden sapıyor | 🟢 | Dokümantasyon | S | Düşük |

---

## Bölüm B — Korunması Gereken İyi Pratikler

1. **Katmanlı mimari ve DI.** `app/di_container.py` + `di_registries.py` ile servis, controller ve repository kurulumu tek yerde; repository'ler `ProjectScopedRepository` ile ortak sorgu davranışı paylaşıyor. Dokunma.
2. **Hardcoded metin koruması.** `tests/test_l10n_no_hardcoded.py` yeni Türkçe sabit metni CI'sız bile test ile yakalıyor. Bu yaklaşım yeni kural testlerine örnek olmalı.
3. **Wiki sağlığı.** 16 sayfa, kırık link 0, öksüz sayfa 0, tamamı `index.md`'de. Metodoloji Bölüm 1.3'ün istediği bağlantısallık sağlanmış.
4. **Veri katmanı.** `PRAGMA foreign_keys=ON`, WAL, `expire_on_commit=False`, açılışta `integrity_check` + yedek döndürme (`backup_manager.py`), `calculate_progress_percent` içinde tek SQL ile ilerleme hesabı.
5. **Logger kurulumu.** `RotatingFileHandler`, `print()` kullanımı sıfır, global exception hook var.

---

## Bölüm C — İncelenmedi Listesi

| Kapsam | Neden |
|--------|-------|
| `.venv/`, `build/`, `dist/`, `graphify-out/`, `*_cache/` | Şablonun hariç tutma listesi |
| `infrastructure/migrations/versions/` (7 dosya) | Şablon gereği sadece sayıldı |
| `resources/fonts`, `icons`, `styles`, `themes` | İkili/üretilmiş varlık; sadece varlığı sayıldı |
| `presentation/qml/views/memo/DrawingCanvas.qml` (1325 satır) | Satır satır okunmadı; yalnızca boyut ölçüldü |
| `AnalyticsView.qml`, `ProjectDetailPanel.qml` iç mantığı | Ölçüldü; bu oturumda değişen bölümler dışında satır satır incelenmedi |
| Git geçmişi (sır sızıntısı) | `git log -p` taraması yapılmadı; çalışma ağacında hardcoded sır bulunmadı |
| `ruff` çıktısı (F401/F841 sayısı) | `ruff.exe` Uygulama Denetimi tarafından engellendi |
| Gerçek görsel/etkileşim davranışı | Ekran görüntüsü alınamıyor; QML yalnızca yükleme ve `qmllint` düzeyinde doğrulandı |

---

## Bölüm D — Detaylı Bulgular

### [🔴] 1. Yedekleme WAL modunda boş/eksik dosya üretiyor
*Persona: SRE / DevOps*
- **Dosya/Konum:** `services/export_service.py:21-31`, `core/managers/backup_manager.py:36-37`
- **Kategori:** Production
- **Sorun:** DB `journal_mode=WAL` ile açılıyor (`db_manager.py:46`). Uygulama açıkken yazılan veri `-wal` dosyasındadır. `shutil.copy2(source, target)` yalnızca ana `.db` dosyasını kopyalar.
- **Etki:** Kullanıcı Ayarlar'dan "Veritabanını Yedekle"ye basar, dosyayı güvenli yere koyar, sonra geri yüklemek ister. Yedekte tablolar eksik ya da son değişiklikler yoktur. Denemede: yeni açılmış DB'ye kayıt eklenip düz kopya alındı, kopyada `no such table: memos` hatası alındı. Dosya listesi: `t.db`, `t.db-shm`, `t.db-wal`.
- **Kanıt:**
```python
shutil.copy2(source, target)   # export_service.py:30
```
- **Çözüm:**
```python
import sqlite3
with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
    src.backup(dst)   # WAL dahil tutarlı anlık görüntü
```
  `backup_manager.run_startup_backup` içinde de aynı API kullanılmalı (önceki oturumdan kalan `-wal` aynı sorunu yaratır).
- **Düzeltme Eforu:** S
- **Bağımlılık:** `backup_manager`, `export_service`; test için dosya tabanlı geçici DB gerekir (şu an testler `:memory:` kullanıyor).

### [🟠] 2. JSON dışa aktarım "tüm veri" diyor, çoğunu yazmıyor
*Persona: Kıdemli Yazılım Mimarı*
- **Dosya/Konum:** `services/export_service.py:38-110`
- **Kategori:** Production
- **Sorun:** Docstring "Tüm proje verilerini (ve alt ilişkileri)" diyor. Gerçekte: not için yalnızca `id/title` (içerik yok), karar için `id/title/status` (karar metni yok), görev için açıklama, öncelik, tip, checklist yok. Memo, ek, aşama, etiket, etkinlik geçmişi hiç yok.
- **Etki:** Kullanıcı bunu ikinci yedek sanır; geri dönüşte not ve karar içerikleri kaybolmuş olur. 72 satırlık tek fonksiyon.
- **Kanıt:**
```python
notes = sess.scalars(select(Note).where(Note.project_id == proj.id))
for n in notes:
    proj_data["notes"].append({"id": n.id, "title": n.title})   # body yok
```
- **Çözüm:** Her modele `to_export_dict()` (veya tek bir generic serileştirici: kolonları `inspect(model).columns` ile dolaştır) ekle; fonksiyonu varlık başına küçük fonksiyonlara böl. Ya da özelliğin adını "Özet Dışa Aktarım" yapıp kapsamı arayüzde açıkça belirt.
- **Düzeltme Eforu:** M
- **Bağımlılık:** Dışa aktarma biçimi değişirse eski dosyalarla uyum; içe aktarma özelliği yok, o yüzden risk düşük.

### [🟠] 3. Ebeveyn görev durumu elle değiştirilemiyor
*Persona: Kıdemli Yazılım Mimarı (Metodoloji Bölüm 3: mantık hatası)*
- **Dosya/Konum:** `services/task_service.py:133-152`
- **Kategori:** Kod Kalitesi / Mantık
- **Sorun:** `recalculate_hierarchy` her görev yazımından sonra çalışır ve alt görevi olan her görevin durumunu çocuklardan türetir (BLOCKED ve CANCELLED hariç).
- **Etki:** Denemede: bir ebeveyn + bir `TODO` alt görev. Ebeveyne elle `IN_PROGRESS` verildi, sonuç `TODO`. Elle `DONE` verildi, sonuç yine `TODO`. Kullanıcı arayüzde seçtiği durumun sessizce geri alındığını görür; hata mesajı yok. Görev diyaloğundaki durum seçimi ebeveynler için etkisiz.
- **Kanıt:**
```python
elif any(self._task_score(child, children) > 0 for child in child_tasks):
    task.status = TaskStatus.IN_PROGRESS.value
else:
    task.status = TaskStatus.TODO.value      # elle verilen durumu ezer
```
- **Çözüm:** İki seçenek. (a) Ebeveyn durumunu salt-okunur yap: diyalogda durum alanını devre dışı bırak ve nedenini göster. (b) Otomatik durumu yalnızca "tüm çocuklar tamam → DONE" ve "çocuk ilerledi → IN_PROGRESS" yönünde ilerlet, geri alma yapma. Karar ürün sahibinde.
- **Düzeltme Eforu:** M
- **Bağımlılık:** İlerleme yüzdesi ve dashboard sayıları bu durumlara bağlı; ilgili testler güncellenmeli.

### [🟠] 4. Controller hata sinyalleri çoğunlukla bağlı değil
*Persona: QA / Test Mühendisi*
- **Dosya/Konum:** `presentation/viewmodels/*.py` (yalnızca `archive`, `search`, `settings` ViewModel'lerinde `error_occurred.connect` var; `archive` yalnızca `project_controller` hatasını dinliyor, ana proje ViewModel'i dinlemiyor)
- **Kategori:** Test / Hata yönetimi
- **Sorun:** 12 controller'ın hepsi hatayı `error_occurred` sinyaliyle bildiriyor. Dinleyen yalnızca 3 ViewModel var; analytics, dashboard, decision, idea, memo, note, resource, stage ve task controller'larının hatasını kimse almıyor.
- **Etki:** Kullanıcı boş içerikli not eklerse servis `NoteValidationError` fırlatır, controller yakalayıp sinyal yayar, kimse dinlemez, form kapanır ve hiçbir şey olmaz. Bu oturumda not formunda yakaladığım hata aynı sebeple sessizdi.
- **Çözüm:** Ortak bir yardımcıyla her ViewModel'de `controller.error_occurred.connect(self._publish_error)`; hata `toast.show` olayına çevrilsin. Tek yerde (taban sınıf) toplanırsa 9 kopya olmaz.
- **Düzeltme Eforu:** M
- **Bağımlılık:** Toast metinleri l10n testine takılabilir (`# l10n: data` işareti gerekir).

### [🟠] 5. İki paralel arayüz
*Persona: Kıdemli Yazılım Mimarı*
- **Dosya/Konum:** `presentation/pages` (3697 satır), `widgets` (3019), `dialogs` (1455), `shell` (515), `modules.py` (154) ≈ 8,8 bin satır; QML + ViewModel ≈ 13 bin satır
- **Kategori:** Mimari
- **Sorun:** `main.py --legacy` hâlâ Widgets arayüzünü açıyor, README ve `test_ui_smoke.py` bu arayüze göre yazılmış. Her özellik iki yerde olmak zorunda; bu oturumda bile karar/not/kaynak düzenleme, filtre ve geçmiş sekmesi yalnızca QML'e girdi.
- **Etki:** Davranış sapması kaçınılmaz (zaten var: widget tarafı `ACCEPTED/DRAFT` karar durumlarını kullanıyordu, QML `APPROVED/PROPOSED` yazıyordu). Her refactor iki kat maliyetli.
- **Çözüm:** Yol haritası kararı: eski arayüzü bir sürümde "kullanımdan kaldırıldı" ilan et, sonra `presentation/{pages,widgets,dialogs,shell,modules.py}` ve ilgili testleri sil. Silmeden önce referans taraması (Metodoloji Bölüm 7).
- **Düzeltme Eforu:** XL
- **Bağımlılık:** Test paketi, README, wiki, PyInstaller spec.

### [🟠] 6. Türkçe harflerde duyarsız arama bozuk
*Persona: Kıdemli Yazılım Mimarı (Yerel Bağlam)*
- **Dosya/Konum:** `services/search_service.py:26,32-60`; `presentation/viewmodels/{idea,memo,project}_list_model.py` (`.lower()` ile süzme)
- **Kategori:** Kod Kalitesi / Yerel bağlam
- **Sorun:** Genel arama SQLite `ILIKE` (LIKE) kullanıyor; SQLite LIKE büyük/küçük harf duyarsızlığı yalnızca ASCII için geçerli. Python tarafında `"I".lower()` → `"i"` (Türkçede `ı` olmalı), `"İ".lower()` → birleşik noktalı iki karakter.
- **Etki:** "Şişli" kaydı "şişli" ile aranınca SQLite `Ş` ile `ş`'yi eşit saymadığı için bulunamaz; Python tarafındaki listelerde `"İstanbul".lower()` birleşik noktalı `i̇` üretir, "istanbul" yazan kullanıcı eşleşmez. Ayrıca `%` ve `_` kullanıcı girdisinde kaçırılmıyor (joker olarak çalışır).
- **Kanıt:**
```python
term = f"%{query.strip().lower()}%"
Project.title.ilike(term)
```
- **Çözüm:** Normalize edilmiş ikinci kolon ya da Python tarafında `casefold()` + Türkçe harita (`İ→i`, `I→ı`) ile ortak bir `normalize_search_text()` yardımcısı; `ilike(..., escape="\\")` ile joker kaçırma.
- **Düzeltme Eforu:** M
- **Bağımlılık:** Dört arama noktası tek yardımcıya bağlanmalı.

### [🟠] 7. Kalite kapıları devre dışı
*Persona: SRE / DevOps*
- **Dosya/Konum:** `pyproject.toml:35-40`, `.pre-commit-config.yaml`, `.github/` yok
- **Kategori:** Production
- **Sorun:** `ruff` yapılandırmasında `F401` (kullanılmayan import) ve `F821` (tanımsız isim) kapalı. `mypy strict = true` yazıyor ama pre-commit yalnızca 4 dosyayı kontrol ediyor. CI yapılandırması yok.
- **Etki:** `mypy` tüm paketlerde çalıştırıldığında **90 hata / 38 dosya** (ör. `analytics_viewmodel.py:150` `Property("QVariantList")` tip uyuşmazlığı). Kapalı `F821` tanımsız isim hatasını gizler; çalışma anında `NameError` olarak patlar. `CLAUDE.md` "mypy uyarıları hata sayılır" diyor, ama kimse çalıştırmıyor.
- **Çözüm:** `ignore` listesinden `F401/F821` çıkar; mevcut ihlalleri bir kerelik temizle. `mypy` için PySide `Property` kalıplarına `# type: ignore[arg-type]  # gerekçe` ekle ya da stub yaz. `pytest` + `ruff` + `mypy` çalıştıran bir GitHub Actions iş akışı ekle.
- **Düzeltme Eforu:** M
- **Bağımlılık:** `ruff.exe` bu makinede engelli; `python -m ruff` de aynı exe'yi çağırıyor. Uygulama Denetimi istisnası ya da CI gerekir.

### [🟠] 8. Test kapsamı dar
*Persona: QA / Test Mühendisi*
- **Dosya/Konum:** `tests/` (9 dosya, 63 test)
- **Kategori:** Test
- **Sorun:** 189 kaynak dosyaya 63 test. `controllers/` için doğrudan test yok. `dashboard_service`, `decision_service`, `resource_service`, `search_service` hiç import edilmiyor. Yeni ViewModel mantığı (`saveTask`, `update*`, `_load_activity`) test dışı.
- **Etki:** Bu oturumdaki `Attachment.file_name` hatası (var olmayan alana erişim) ve karar durumu uyuşmazlığı, ilgili slotlara tek test yazılsaydı ilk çalıştırmada yakalanırdı.
- **Test önerisi, en kritik 5 fonksiyon:**
  1. `TaskService.update_task` — ebeveyn görevde elle durum (Bulgu 3'ün regresyon testi).
  2. `ExportService.backup_database` — dosya tabanlı DB'de yedekten geri okuma.
  3. `SearchService.search_all` — `Ş/İ/ı` ve `%` içeren sorgular.
  4. `ProjectViewModel.addOutput/_load_outputs` — `caption` ile gidiş-dönüş.
  5. `StageService.complete_stage/_check_and_complete_project` — proje otomatik tamamlanma (cc=11).
- **Düzeltme Eforu:** L
- **Bağımlılık:** Dosya tabanlı geçici DB fixture'ı (`tmp_path`).

### [🟠] 9. God object ViewModel ve QML dosyaları
*Persona: Kıdemli Yazılım Mimarı*
- **Dosya/Konum:** `project_viewmodel.py` (418 satır, 57 metot), `task_viewmodel.py` (411, 46), `idea_viewmodel.py` (30 metot); `ProjectDetailPanel.qml` (~1700 satır), `DrawingCanvas.qml` (1325), `AnalyticsView.qml` (640)
- **Kategori:** Mimari
- **Sorun:** Eşikler: sınıf > 300 satır, metot > 20. `CLAUDE.md` §3.3 sınır 400 satır / 15 public metot; ikisi de aşıldı. `ProjectViewModel` proje listesi, seçili proje, aşamalar, görevler, kararlar, notlar, kaynaklar, çıktılar, geçmiş ve diyalog durumunu tek sınıfta tutuyor. `ProjectDetailPanel.qml` içinde 6 sekme ve 4 modal diyalog var.
- **Etki:** Her yeni alt özellik aynı dosyaya biniyor; birleştirme çakışması ve regresyon riski büyüyor.
- **Çözüm:** `ProjectViewModel`'i `ProjectSubitemsViewModel` (karar/not/kaynak/çıktı/geçmiş) ve `ProjectViewModel` (liste + seçim + diyalog) olarak ikiye böl. QML'de her sekmeyi ve her modal'ı ayrı dosyaya çıkar (`DecisionDialog.qml`, `NoteDialog.qml`, `ResourceDialog.qml`, `ActivityTab.qml`).
- **Düzeltme Eforu:** L
- **Bağımlılık:** `main_qml.py` içindeki context property kayıtları, `test_qml_bridges.py`.

### [🟡] 10. ViewModel katman atlıyor, UI thread'de senkron DB
*Persona: Kıdemli Yazılım Mimarı*
- **Dosya/Konum:** `presentation/viewmodels/project_viewmodel.py:232, 245`; `_load_activity`, `_load_outputs`
- **Kategori:** Mimari / Performans
- **Sorun:** ViewModel servise doğrudan gidiyor (`self._di.services.task.get_tasks`), `CLAUDE.md` §2 katman sırasını (ViewModel → Controller → Service) çiğniyor. Ayrıca `get_*_sync` çağrıları proje seçiminde UI thread'inde çalışıyor; `except Exception  # noqa: BLE001` hatayı sessizce yutuyor.
- **Etki:** Büyük bir projede proje seçimi arayüzü kısa süre dondurur; görev yükleme hatası kullanıcıya yansımaz, liste boş görünür.
- **Çözüm:** `TaskController.load_tasks` zaten `Worker` kullanıyor; `ProjectViewModel` onu kullansın. `get_*_sync` çağrılarını `Worker` ile sarmala.
- **Düzeltme Eforu:** M
- **Bağımlılık:** Bulgu 9 ile birlikte yapılırsa tek geçişte biter.

### [🟡] 11. Çift migration sistemi ve ham SQL
*Persona: Kıdemli Yazılım Mimarı*
- **Dosya/Konum:** `infrastructure/database/migration_runner.py:177-211`, `alembic_runner.py:12`
- **Kategori:** Mimari
- **Sorun:** Alembic (7 sürüm) ile birlikte eski "idempotent" `migration_runner` hâlâ çalışıyor ve `text(f"ALTER TABLE {table_name} ...")` ham SQL üretiyor. `db_manager.py` başlığı "ham SQL yasaktır" diyor, `CLAUDE.md` §2 aynı kuralı koyuyor.
- **Etki:** Enjeksiyon riski yok: tablo ve kolon adları sabit çağrılardan geliyor ve `_safe_identifier` ile doğrulanıyor. Sorun kural ve tutarlılık: şema iki yerde tanımlı, sürüm takibi yalnızca birinde.
- **Çözüm:** Eski runner'ın yaptığı işleri tek bir Alembic sürümüne taşı, runner'ı sil.
- **Düzeltme Eforu:** M
- **Bağımlılık:** Mevcut kullanıcı DB'leri; sürüm damgası (`alembic stamp`) gerekebilir.

### [🟡] 12. Analitik günlük kovaları UTC
*Persona: Kıdemli Yazılım Mimarı (Yerel Bağlam)*
- **Dosya/Konum:** `services/analytics_service.py:51, 67, 194`, `_time_series` (`func.strftime(fmt, Task.completed_at)`)
- **Kategori:** Kod Kalitesi / Yerel bağlam
- **Sorun:** `completed_at` UTC yazılıyor, `strftime` doğrudan UTC değerine uygulanıyor, anahtarlar ise `date.today()` (yerel) ile üretiliyor (satır 194). `backup_manager.py:29` ise naive `datetime.now()` kullanıyor.
- **Etki:** UTC+3'te saat 00:00-03:00 arasında tamamlanan görev önceki günün kovasına düşer; "bugün" ve "seri" göstergeleri yanlış gün sayar.
- **Çözüm:** Kovalamayı yerel saate çevir (`strftime(fmt, Task.completed_at, 'localtime')`) ve anahtarları aynı saat dilimiyle üret; zaman damgası politikasını wiki'ye yaz (kayıt UTC, gösterim yerel).
- **Düzeltme Eforu:** S
- **Bağımlılık:** Analitik testleri.

### [🟡] 13. Geniş `except Exception` ve controller kopyala-yapıştır
*Persona: QA / Test Mühendisi*
- **Dosya/Konum:** 44 yer; en çok `controllers/idea_controller.py` (5), `resource_controller.py` (4), `note_controller.py` (4), `memo_controller.py` (4)
- **Kategori:** Kod Kalitesi
- **Sorun:** `CLAUDE.md` §3.2 yalnızca beklenen istisnayı yakalamayı şart koşuyor. Controller'ların `create/update/delete` gövdeleri `try: ... except (AppBaseException, ValueError) ... except Exception: logger.error(...); error_occurred.emit("... hata oluştu")` kalıbının aynısı (DRY ihlali, ~11 dosya).
- **Etki:** Programlama hatası (ör. `AttributeError`) kullanıcıya "hata oluştu" olarak maskelenir, çözüm arayan kişi log'a bakmak zorunda kalır.
- **Çözüm:** Tek bir `@handle_errors("Not oluşturulamadı")` dekoratörü ya da `BaseController._run(callable)`; `except Exception` yalnızca en dış katmanda ve `logger.exception` ile.
- **Düzeltme Eforu:** M
- **Bağımlılık:** Bulgu 4 ile aynı taban sınıf kullanılabilir.

### [🟡] 14. Bağımlılık yönetimi
*Persona: DevSecOps Uzmanı*
- **Dosya/Konum:** `pyproject.toml:8-19`, `requirements.txt`
- **Kategori:** Güvenlik / Dağıtım
- **Sorun:** `pytest`, `pytest-qt`, `mypy`, `ruff`, `pyinstaller` çalışma bağımlılığı olarak listelenmiş; her yerde alt sınır (`>=`) var, üst sınır yok; aynı liste iki dosyada ayrı tutuluyor. `uv.lock` var (olumlu), ama `requirements.txt` ile senkron olduğu doğrulanmıyor. CVE taraması ve lisans taraması yapılmamış.
- **Etki:** Son kullanıcı kurulumunda gereksiz paketler yüklenir; kilitsiz kurulumda yeni major sürüm (ör. PySide6) sessizce kırabilir.
- **Çözüm:** Geliştirme araçlarını `[project.optional-dependencies] dev` altına taşı; `requirements.txt`'i `uv export` ile üret; `pip-audit` ya da `uv pip audit` adımını CI'a ekle.
- **Düzeltme Eforu:** S
- **Bağımlılık:** `scripts/build_installer.ps1`, PyInstaller spec.

### [🟡] 15. Ölü kod ve ölü bağımlılık
*Persona: Kıdemli Yazılım Mimarı*
- **Dosya/Konum:** `core/workers/async_worker.py`, `domain/dtos/base_dto.py`, `presentation/widgets/task_list_widget.py`, `scripts/commit_all.py`, `app/di_container.py:108`, `core/managers/secret_manager.py`
- **Kategori:** Kod Kalitesi
- **Sorun:** Dört modül projede hiçbir yerden import edilmiyor (import ve modül adı taraması). `SecretManager` DI'da kuruluyor ama `get_secret/set_secret` hiçbir yerde çağrılmıyor; `keyring` bağımlılığı fiilen ölü. `quality.py` kökte ve `scripts/quality.py` olarak iki kopya.
- **Etki:** Okuyucuyu yanıltır, paket boyutunu (keyring + backends) şişirir.
- **Çözüm:** Referans taramasından sonra sil; `keyring` ve `SecretManager` ya kaldırılır ya da gerçek bir kullanım senaryosuna bağlanır (karar gerekli).
- **Düzeltme Eforu:** S
- **Bağımlılık:** `scripts/commit_all.py` içindeki yol listesi, wiki sayfaları.

### [🟡] 16. `recalculate_hierarchy` her kayıtta tüm projeyi tarıyor
*Persona: SRE / DevOps*
- **Dosya/Konum:** `services/task_service.py:133` (cc=12), `task_repository.py:99` (61 satır)
- **Kategori:** Performans
- **Sorun:** Her görev oluşturma, güncelleme, checklist işareti sonrasında projenin bütün görevleri yüklenir, derinliğe göre sıralanır, `update_many` çağrılır, ardından ilerleme sorgusu çalışır. `calculate_progress_percent` içinde import'lar fonksiyon gövdesinde.
- **Etki:** Yüzlerce görevli projede her checkbox tıklaması O(n log n) Python işi + birkaç sorgu. Yerel SQLite'ta bugün sorun değil; 1000+ görevde algılanır.
- **Çözüm:** Yalnızca değişen görevin ata zincirini yeniden hesapla (parent_task_id yukarı yürü).
- **Düzeltme Eforu:** M
- **Bağımlılık:** Bulgu 3'ün kararı (durum türetme kuralı) önce verilmeli.

### [🟡] 17. Eşik aşan fonksiyonlar ve sınıflar
*Persona: Kıdemli Yazılım Mimarı*
- **Dosya/Konum ve değer:**

| Konum | Metrik |
|-------|--------|
| `presentation/pages/tasks/wbs_tree.py:128 render_tasks` | 92 satır, cc=17, derinlik=6 |
| `presentation/viewmodels/project_list_model.py:65 _get_field_by_role` | cc=22 |
| `presentation/viewmodels/idea_list_model.py:62 _extract_role_data` | cc=18 |
| `presentation/viewmodels/task_list_model.py:96 _extract_role_data` | cc=15 |
| `services/dashboard_service.py:27 get_dashboard_stats` | 106 satır, cc=14 |
| `main_qml.py:100 run_qml_app` | 125 satır |
| `presentation/dialogs/idea_dialog.py:64 _setup_ui` | 128 satır |
| `services/export_service.py:38 export_to_json` | 72 satır |
| `presentation/shell/sidebar.py:66 __init__` | 7 parametre |
| `services/analytics_service.py:86 _time_series` | 7 parametre |
| `app/di_registries.py` | 82 import (eşik 25) |
| `core/managers/preference_manager.py PreferenceManager` | 22 metot |

- **Etki:** Rol tabanlı `if` zincirleri (`_get_field_by_role`) her yeni rolde değiştirilmek zorunda; Open/Closed ihlali.
- **Çözüm:** Rol adı → okuyucu fonksiyon sözlüğü (`{ProjectIdRole: lambda p: p.id, ...}`); `run_qml_app`'i kurulum adımlarına böl; `di_registries` için import'lar fonksiyon içi tembel yüklemeyle kalabilir (bilinçli olarak mı yapıldığı belgelenmeli).
- **Düzeltme Eforu:** L
- **Bağımlılık:** Eski arayüz silinirse (Bulgu 5) listenin yarısı kendiliğinden düşer; önce onu karara bağla.

### [🟡] 18. `Worker` ilerleme geri çağrısı kontrolü kırılgan
*Persona: QA / Test Mühendisi*
- **Dosya/Konum:** `core/workers/worker.py:45`
- **Kategori:** Kod Kalitesi
- **Sorun:** `"progress_callback" in self.fn.__code__.co_varnames`. `co_varnames` yalnızca parametreleri değil yerel değişkenleri de içerir; `functools.partial` ve çağrılabilir nesnelerde `__code__` yoktur.
- **Etki:** `partial` ile verilen bir iş `AttributeError` ile hata sinyali üretir; yerel değişkeni `progress_callback` adlı bir fonksiyona yanlışlıkla geri çağrı enjekte edilir.
- **Kanıt:**
```python
if "progress_callback" in self.fn.__code__.co_varnames:
    self.kwargs["progress_callback"] = self.signals.progress.emit
```
- **Çözüm:** `inspect.signature(self.fn).parameters` kullan.
- **Düzeltme Eforu:** S
- **Bağımlılık:** Yok.

### [🟡] 19. `os.startfile` ile rastgele yol açma
*Persona: DevSecOps Uzmanı*
- **Dosya/Konum:** `presentation/viewmodels/project_viewmodel.py:373-381` (`openUrlOrPath`)
- **Kategori:** Güvenlik
- **Sorun:** Kaynak kaydındaki herhangi bir var olan yol `os.startfile` ile çalıştırılır; `.exe`, `.bat`, `.ps1` dahil. URL tarafı `http/https` ile sınırlı (olumlu).
- **Etki:** Kullanıcı kendi girdisini açıyor, bu yüzden doğrudan istismar zor. Ancak başkasından alınan bir `.db` yedeği (bu uygulama yedek dosyası paylaşımını teşvik ediyor) içinde bir `.bat` yolu olan kaynak varsa, tek tıkla çalışır.
- **Çözüm:** Çalıştırılabilir uzantılar için (`.exe .bat .cmd .ps1 .msi .vbs .js .lnk`) onay iste ya da `os.startfile` yerine klasörü göster (`explorer /select,`).
- **Düzeltme Eforu:** S
- **Bağımlılık:** Yok.

### [🟢] 20. Wiki ve CLAUDE.md metodolojiden sapıyor
*Persona: Kıdemli Yazılım Mimarı (Metodoloji Bölüm 1)*
- **Dosya/Konum:** `CLAUDE.md`, `docs/wiki/`
- **Kategori:** Dokümantasyon
- **Sorun:** Metodoloji 1.2/1.5: `docs/wiki/rules.md` var olmalı, `CLAUDE.md` "önce `docs/wiki/index.md` oku" demeli, log işlem tipleri `INGEST/REVIEW/LINT` olmalı. Projede `rules.md` yok (`kurallar-ve-sozlesmeler.md` var), `CLAUDE.md` yalnızca `Project_docs/RULES.md`'ye yönlendiriyor, log tipleri `FEATURE/FIX/PERF/REFACTOR`. `README.md` dizin ağacı `main.py`'yi "uygulama giriş noktası" diyor ama QML'in ayrı `main_qml.py`'si olduğunu söylemiyor.
- **Etki:** Yapay zeka her oturumda wiki'yi indeksten değil keşifle buluyor; log tipi sorgulanamıyor.
- **Çözüm:** `CLAUDE.md`'ye "önce `docs/wiki/index.md` oku" satırı ekle; log tip kümesini iki kümeden birine sabitle (mevcut kullanım korunacaksa metodoloji dosyasını güncelle).
- **Düzeltme Eforu:** S
- **Bağımlılık:** Yok.

---

## Bölüm E — Aksiyon Planı

### 🚨 24 Saat İçinde

1. **Yedeklemeyi düzelt (Bulgu 1).**
   - Eylem: `sqlite3.Connection.backup` ile hem arayüz yedeğini hem açılış yedeğini değiştir; dosya tabanlı bir test ekle.
   - Beklenen sonuç: Yedek dosyası açıkken alınsa bile tüm tabloları ve son kayıtları içerir.
   - Bağımlılık: Yok.
   - Risk: Yedek sırasında yazan bir işlem varsa `backup()` kısa süre bekler; arayüz thread'inde çağrılıyorsa `Worker`'a al.
2. **JSON dışa aktarım kapsamını belirle (Bulgu 2).**
   - Eylem: En azından not içeriği, karar metni, görev açıklaması ve checklist'i ekle; mümkün değilse arayüz metnini "özet dışa aktarım" olarak değiştir.
   - Beklenen sonuç: Kullanıcı yanlış güven duymaz.
   - Bağımlılık: Yok.
   - Risk: Dosya boyutu artar.
3. **Sessiz hataları görünür yap (Bulgu 4, ilk adım).**
   - Eylem: En az not, karar, kaynak ve görev ViewModel'lerine `error_occurred` bağlantısı ekle.
   - Beklenen sonuç: Doğrulama hatalarında toast çıkar.
   - Bağımlılık: Toast metinleri `# l10n: data` ile işaretlenmeli.
   - Risk: Eski arayüzle çift toast görünebilir.

### 📅 Bu Hafta

1. **Ebeveyn görev durum kuralı (Bulgu 3):** Karar ver, uygula, regresyon testi yaz. Risk: İlerleme yüzdesi değerleri değişebilir.
2. **Kalite kapıları (Bulgu 7):** `F401/F821` aç, ihlalleri temizle, CI iş akışı ekle. Risk: İlk temizlikte çok sayıda küçük diff.
3. **Eski arayüz kararı (Bulgu 5):** Kaldırma tarihi ve kapsamı belirle; README ve wiki'yi güncelle. Risk: Widget tabanlı testler düşer.
4. **Türkçe arama (Bulgu 6):** Ortak `normalize_search_text`, dört arama noktasına bağla, test ekle. Risk: Sonuç sırası değişebilir.
5. **Eksik servis testleri (Bulgu 8):** `decision`, `resource`, `search`, `dashboard` için en az birer temel test. Risk: Yok.

### 🗓 Bu Ay

1. **God object bölme (Bulgu 9, 10):** `ProjectViewModel` ikiye, `ProjectDetailPanel.qml` dosyalara. Risk: Context property adları değişirse QML kırılır; `test_qml_bridges.py` ile koru.
2. **Migration birleştirme (Bulgu 11):** Eski runner'ı Alembic sürümüne taşı. Risk: Mevcut kullanıcı DB'leri; `alembic stamp` planı gerekir.
3. **Zaman damgası politikası (Bulgu 12):** UTC kayıt, yerel gösterim; analitik düzeltmesi. Risk: Geçmiş grafiklerde kayma.
4. **Bağımlılık düzeni (Bulgu 14, 15):** Dev bağımlılıkları ayır, `uv export`, ölü kod ve `keyring` kararı. Risk: PyInstaller gizli import listesi.
5. **Controller taban sınıfı (Bulgu 13, 4 son adım):** Ortak hata yönetimi, `except Exception` temizliği. Risk: Controller imzaları değişmez, düşük.

---

## Bölüm F — Sonraki Adım

Hangi bulgudan başlamak istersin? Seçtiğin maddenin detaylı refactor planını, etkilenecek dosyaları ve örnek before/after kodunu üretebilirim. Önerim: **1 → 2 → 4 → 3** sırası (önce veri güvenliği, sonra sessiz hatalar, sonra mantık kuralı).

*Bu rapor hiçbir kodu değiştirmedi; yalnızca bu dosya eklendi.*
