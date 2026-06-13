# Senior Mimari ve Kod Kalitesi Analiz Raporu

**Tarih:** 2026-06-12 · **Kapsam:** 142 .py dosyası, ~11.380 satır · **Yöntem:** AST tabanlı statik analiz + desen taraması

---

## 1. Genel Değerlendirme

Proje, masaüstü PySide6 uygulaması için **olgun bir katmanlı mimariye** sahip:

```
presentation (pages/dialogs/widgets/shell)
    → controllers (QObject sinyal köprüsü)
        → services (iş kuralları)
            → repositories (SQLAlchemy)
                → DatabaseManager (engine + scoped_session)
```

Güçlü yönler:
- Presentation katmanı **hiçbir yerde** infrastructure veya SQLAlchemy import etmiyor (katman sızıntısı yok).
- DTO kullanımı (`TaskCreateDTO` vb.), EventBus pub/sub, DI container, Alembic migration zinciri mevcut.
- `Worker`/`QThreadPool` altyapısı GC-güvenli yazılmış (`_active_workers` seti + `setAutoDelete(False)`).
- Token tabanlı QSS tema sistemi (`@token` → JSON palet) doğru tasarım.
- Ham SQL yok; WAL modu ve `foreign_keys=ON` aktif.

Genel not: **Altyapı kaliteli, adaptasyon eksik.** StringManager, IconManager, dimensions.py gibi merkezi sistemler kurulmuş ama kod tabanının ~%90'ı bunları henüz kullanmıyor. Asıl borç "yanlış tasarım" değil, "yarım kalmış migrasyon".

---

## 2. God Object / Şişkin Dosya Tespiti (RULES.md: dosya ≤400 satır, sınıf ≤15 metod)

| İhlal | Ölçüm | Dosya |
|---|---|---|
| 🔴 Dosya >400 satır | 493 satır | `presentation/pages/tasks_page.py` |
| 🔴 Dosya >400 satır | 403 satır | `presentation/dialogs/project_dialog.py` |
| 🔴 Sınıf 41 metod | `DIContainer` | `di_container.py` |
| 🔴 Sınıf 24 metod | `ProjectsPage` | `presentation/pages/projects_page.py` |
| 🔴 Sınıf 22 metod | `TasksPage` | `presentation/pages/tasks_page.py` |
| 🔴 Sınıf 22 metod | `TaskService` | `services/task_service.py` |
| 🟡 Sınıf 19 metod | `ProjectDetailPanel` | `presentation/widgets/project_detail_panel.py` |
| 🟡 Sınıf 16 metod | `TaskDialog` | `presentation/dialogs/task_dialog.py` |

### Refactoring önerileri

1. **TasksPage (493 satır / 22 metod):** Üç sorumluluğa bölünmeli:
   - `TaskTreeView` (ağaç render + renklendirme + fade animasyonu → `_render_tree`, `_on_tasks_loaded`)
   - `TaskFilterBar` (durum/öncelik/tip/aşama filtre combobox'ları → `_reload_stage_filter`, `_filtered_tasks`)
   - `TasksPage` yalnızca kompozisyon + controller bağlama.
2. **ProjectDialog (403 satır):** Form bölümlerini (`_build_*` metodları) ayrı bölüm widget'larına çıkar; validasyonu form sınıfından ayır.
3. **DIContainer (41 metod):** Doğası gereği factory yoğun, ancak modül bazlı alt-container'lara bölünebilir: `RepositoryRegistry`, `ServiceRegistry`, `ControllerRegistry`. Böylece her yeni modülde tek dev sınıf büyümez (Open/Closed).
4. **TaskService (22 metod):** Checklist ve move/WBS operasyonları ayrı servislere (`ChecklistService`, `TaskHierarchyService`) çıkarılabilir.

---

## 3. SOLID / OOP / Design Pattern Analizi

### Tespit edilen desenler (doğru kullanım)
- **Repository** (12 adet), **Singleton** (6 adet), **Pub/Sub** (EventBus), **DI Container**, **Command-benzeri Worker**, **DTO**, **Token-Template** (tema QSS).

### Sorunlar

**3.1 — Çifte erişim yolu: DI Container + Singleton karışımı (DIP ihlali)**
Manager'lar hem DI container'dan hem `X.instance()` ile erişiliyor. Örnek: `tasks_page._render_tree` içinde `ThemeManager.instance()` lokal import ile çağrılıyor — bu **Service Locator anti-pattern** ve DI'ı baypas ediyor. Karar verilmeli: ya constructor injection (önerilen) ya da bilinçli singleton; ikisi birden test edilebilirliği bozuyor.

**3.2 — BaseRepository yok (DRY ihlali)**
12 repository'de `create` 9, `get_by_project` 9, `get_by_id` 7, `update` 7, `delete` 7 kez kopyalanmış. Generic `BaseRepository[T]` (SQLAlchemy 2.0 `session.get`, `select(T)`) ile ~150-200 satır tekrar silinir, yeni modül ekleme maliyeti düşer.

**3.3 — Encapsulation ihlali**
`theme_manager._generate_icon_tokens()` → `IconManager._instance` private alanına doğrudan erişiyor. `IconManager.is_ready()` / `try_instance()` gibi public API eklenmeli.

**3.4 — Geniş exception yakalama**
36 adet `except Exception` (yoğunluk: controller katmanı). Controller'larda hata→sinyal dönüşümü için kabul edilebilir, ancak servis/repo katmanında spesifik exception tipleri (`SQLAlchemyError`, `IntegrityError`) yakalanıp `AppBaseException` hiyerarşisine sarılmalı; aksi halde programlama hataları (AttributeError vb.) sessizce "kullanıcı hatası" gibi toast'a düşüyor.

**3.5 — `_tr` fonksiyonu iki dosyada ayrı tanımlı**
`tasks_page.py` ve `sidebar.py` kendi `_tr` yardımcısını tanımlıyor — tek modüle (`presentation/utils/i18n.py` veya doğrudan `StringManager.get`) taşınmalı.

---

## 4. Bellek Yönetimi

| Durum | Bulgu |
|---|---|
| ✅ İyi | Worker GC koruması (`_active_workers` + `finished→_cleanup`) doğru kurgulanmış. |
| ✅ İyi | `parent` parametresi widget'larda yaygın olarak geçiliyor (tek istisna aşağıda). |
| ✅ İyi | `theme_changed` Qt sinyali — alıcı QObject silinince Qt bağlantıyı otomatik düşürür, sızıntı yok. |
| 🔴 Risk | **EventBus dangling handler:** `dashboard_controller`, `stage_controller` ve özellikle `toast.py` (widget!) `subscribe` ediyor ama hiç `unsubscribe` yok. EventBus saf Python listesi tuttuğu için silinen widget'ın bound method'u listede kalır → ölü C++ objesi üzerinde çağrı = `RuntimeError: Internal C++ object already deleted` çökmesi. `projects_page` doğru örnek (2 sub / 2 unsub). **Çözüm:** EventBus'a `weakref.WeakMethod` desteği ekle veya `QObject.destroyed` sinyaline bağlı otomatik unsubscribe. |
| 🟡 Küçük | `IdeaListItem` (`ideas_page.py`) `__init__`'te `parent` parametresi almıyor. |
| 🟡 Küçük | `IconManager._cache` sınırsız; ikon sayısı az olduğundan pratik sorun değil, ancak `theme × renk` kombinasyonu büyürse `lru` benzeri sınır düşünülebilir. |
| 🟡 Küçük | `ThemeManager._generate_icon_tokens` her `build_global_qss` çağrısında diske SVG cache dosyası yazıyor — idempotent ama gereksiz I/O; dosya varsa atlanabilir. |

---

## 5. Performans / Donma Analizi

| Durum | Bulgu |
|---|---|
| ✅ İyi | Okuma işlemleri (`load_tasks`, `load_all_tasks` vb.) Worker ile arka planda — UI kilitlenmiyor. |
| ✅ İyi | SQLite WAL + `scoped_session` + `finally: remove()` — thread havuzunda session sızıntısı yok. |
| 🔴 Hata | **`tasks_page._render_tree`: `from core.managers.theme_manager import ThemeManager` satırı `for task in filtered_tasks` döngüsünün İÇİNDE.** Her görev için import + `instance()` çağrısı. Modül başına taşınmalı. |
| 🟡 Orta | Yazma işlemleri (`create_task`, `update_task`, `toggle_status`, `delete_task`) UI thread'inde **senkron** çalışıyor. Küçük SQLite işlemlerinde fark edilmez; ancak kademeli silme (WBS alt ağacı) veya migration sonrası büyük tablolarda mikro donmalar üretir. Tutarlılık için yazmalar da Worker'a alınmalı veya bilinçli olarak senkron bırakıldığı belgelenmeli. |
| 🟡 Orta | `_render_tree` her yüklemede `clear()` + tam yeniden kurulum + `expandAll()`. 500+ görevde gözle görülür takılma yapar. Öneri: render bloğunu `self._tree.setUpdatesEnabled(False) … True` ile sarmak (ucuz kazanım); uzun vadede diff tabanlı güncelleme. |
| 🟡 Küçük | `build_global_qss` her tema değişiminde tüm `.qss` dosyalarını diskten okuyor — tema başına önbelleklenebilir; değişim nadir olduğundan düşük öncelik. |

---

## 6. Tema Değişimi Analizi

Mimari sağlam: JSON palet → `@token` interpolasyonu → global QSS → `main_window.setStyleSheet`.

**Tespit edilen boşluk — programatik renkler tema değişiminde güncellenmiyor:**

`theme_changed` sinyalini yalnızca 4 bileşen dinliyor: `main_window`, `sidebar`, `info_page`, `stage_timeline_widget`. Oysa QSS dışında **kod ile** renk atayan yerler var:

1. `tasks_page._render_tree` — ağaç item'larının `setForeground` renkleri (`_STATUS_THEME_KEYS`). Tema değişince mevcut ağaç **eski temanın renkleriyle kalır**; ancak bir sonraki veri yüklemesinde düzelir. → `theme_changed`'e bağlanıp `_render_tree()` tetiklenmeli.
2. `services/stage_service.py` — **8 hardcoded hex renk**. Servis katmanında renk olması başlı başına katman ihlali (iş kuralı ≠ sunum); bu renkler `dark.json`/`light.json` paletine veya bir `presentation` sabitine taşınmalı. Açık temada kontrast garanti edilemiyor.
3. `project_list_item.py`, `domain/models/project_stage.py` — benzer programatik renk noktaları gözden geçirilmeli.

**Öneri:** "Tema sözleşmesi" kuralı: *Renk yalnızca iki yerden gelir — QSS token'ı veya `ThemeManager.color(key)` çağrısı; `ThemeManager.color` kullanan her widget `theme_changed`'e abone olmak zorundadır.* Bu kural RULES.md'ye eklenmeli.

Ayrıca: tema tercihi kalıcılığı (`PreferenceManager` üzerinden açılışta `switch_theme`) doğrulanmalı — `ThemeManager.__init__` sabit `"dark"` ile başlıyor.

---

## 7. Merkezi Icon ve String Yönetimi (L10N)

### Mevcut durum
- `StringManager` + `resources/locales/strings.tr.json` **var** ama yalnızca **38 anahtar** içeriyor.
- `_tr` kullanımı sadece 2 dosyada (tasks_page: 31, sidebar: 7).
- Üretim kodunda **~600+ hardcoded Türkçe string** 30+ dosyaya dağılmış. En yoğun: `project_dialog` (37), `project_detail_panel` (28), `stage_service` (28), `task_dialog` (25), `idea_dialog` (24).
- `IconManager` var ve SVG renklendirme + cache yapıyor; ancak `get_svg_content` ile `get_icon` içinde aynı replace mantığı **iki kez** yazılmış (DRY).

### Yol haritası

1. **StringManager'ı QObject yap, `language_changed = Signal(str)` ekle.** Şu an `set_language` çağrılsa bile hiçbir UI yenilenmez — sinyal olmadan L10N çalışmaz.
2. **Tek erişim noktası:** `presentation/utils/i18n.py` içinde `tr(key, default)` tanımla; iki kopya `_tr` silinsin.
3. **Anahtar isimlendirme standardı:** `<modül>.<bağlam>.<öğe>` (örn. `projects.dialog.title`, `tasks.filter.status`). Mevcut düz anahtarlar (`nav_dashboard`) migrasyonda öneklensin.
4. **Kademeli migrasyon planı** (dosya başına PR, öncelik = string yoğunluğu):
   `project_dialog` → `task_dialog` → `idea_dialog` → `project_detail_panel` → sayfalar → widget'lar → controller hata mesajları → `stage_service` aşama adları.
5. **Doğrulama testi:** Tüm `.py` dosyalarında Türkçe karakter içeren string literal arayan bir CI/pytest kontrolü (`tests/test_l10n_no_hardcoded.py`) — migrasyon tamamlanan dosyalar allowlist'ten çıkarılır, regresyon engellenir.
6. **IconManager:** `get_icon` içi `get_svg_content`'i çağırsın (tek renklendirme yolu); `QPixmap.loadFromData` yerine `QSvgRenderer` ile boyut bağımsız render (yüksek DPI'da bulanıklık önlenir). İkon adları için `Icons` sabit sınıfı (`Icons.SEARCH = "search"`) — string typo'ları derleme öncesi yakalanır.

---

## 8. Diğer Tespitler

- `commit_all.py` (129 satır, 84 TR string) ve `download_assets.py` repo kökünde — `scripts/` altına taşınmalı; `commit_all.py` üretim importlarından izole olduğu doğrulanmalı.
- `dimensions.py` (yeni) iyi bir adım — ancak henüz tüm magic number'lar taşınmadıysa, tema sözleşmesine benzer şekilde "yeni kodda sayısal margin/spacing yasak" kuralı RULES.md'ye eklenmeli.
- `core/` katmanı PySide6'ya bağımlı (theme/icon/font/log manager). Pragmatik olarak kabul edilebilir; ancak "core = framework bağımsız" hedefleniyorsa bu manager'lar `presentation/managers/` altına aittir. Graphify haritası bu karar sonrası güncellenmeli (CLAUDE.md §3).
- Test kapsamı: smoke + MVP core + quality systems mevcut; servis katmanı birim testleri (özellikle `TaskService.move_task` WBS senaryoları) eksik görünüyor.

---

## 9. Önceliklendirilmiş Aksiyon Listesi

| # | Öncelik | İş | Etki | Durum |
|---|---|---|---|---|
| 1 | 🔴 P0 | EventBus'a weakref/otomatik unsubscribe (toast çökme riski) | Güvenilirlik | ✅ Yapıldı (2026-06-12) |
| 2 | 🔴 P0 | `_render_tree` döngü içi import'u modül seviyesine al | Performans | ✅ Yapıldı + `setUpdatesEnabled` sarmalı |
| 3 | 🔴 P1 | `tasks_page` ve `project_dialog` refactor (RULES.md ihlali) | Bakım | ✅ Yapıldı (`pages/tasks/` paketi, `form_utils`) |
| 4 | 🔴 P1 | Tema sözleşmesi: programatik renk kullanan widget'lar `theme_changed`'e bağlansın | Tema | ✅ Yapıldı (tasks, dashboard, resource_list) |
| 5 | 🟡 P2 | `BaseRepository[T]` ile 12 repo'daki CRUD tekrarını sil | Bakım | ✅ Yapıldı (`base_repository.py`) |
| 6 | 🟡 P2 | StringManager'a `language_changed` sinyali + kademeli string migrasyonu + CI regresyon testi | L10N | ✅ Sinyal + ratchet testi + `project_dialog` migrate; 21 dosya allowlist'te bekliyor |
| 7 | 🟡 P2 | Yazma işlemlerini de Worker'a taşı | Performans | 📝 Karar: senkron bırakıldı — SQLite WAL'de yazmalar ms seviyesinde; async geçiş sinyal sıralaması riskine değmez. Büyük toplu işlem (WBS alt ağacı silme) yavaşlarsa yeniden değerlendirilecek. |
| 8 | 🟡 P3 | DIContainer'ı registry'lere böl | Mimari | ✅ Yapıldı (`di_registries.py`); constructor injection uzun vadeli kuyrukta |
| 9 | 🟢 P3 | IconManager DRY + QSvgRenderer + `Icons` sabitleri | İkon | ✅ Yapıldı (+ `try_instance()`, cache I/O fix) |
| 10 | 🟢 P3 | Script'leri `scripts/` altına taşı; `_tr` kopyalarını birleştir | Hijyen | ✅ Yapıldı |

Not (2026-06-12, 2): Wiki bilgi tabanı kuruldu — `docs/wiki/` (13 sayfa, index + log). Mimari/karar dokümantasyonu artık orada sürdürülüyor.

Not (2026-06-12): QSS modülerleştirme tamamlandı — monolitik `base.qss` 8 modüle bölündü (`resources/styles/base/`), widget'a özgü kurallar kendi dosyalarına taşındı. CLAUDE.md'deki Graphify zorunluluğu kaldırıldı.
