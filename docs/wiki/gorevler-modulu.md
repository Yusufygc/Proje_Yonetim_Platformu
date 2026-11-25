# Görevler Modülü (WBS)

QML arayüzü (eski Widgets `presentation/pages/tasks/` paketi 2026-10-07'de kaldırıldı):

- **`presentation/qml/views/TasksView.qml`** — istatistik çubuğu (`tasks/TaskStatsBar.qml`), görev ağacı, sürükle-bırak durumu ve hızlı ekleme; araç çubuğu (proje seçici, arama, durum/öncelik/tip filtreleri, ana görev ekleme) `tasks/TaskToolbar.qml` bileşenindedir.
- **`presentation/qml/views/tasks/TaskItemDelegate.qml`** — ağaç satırı: durum kutusu, WBS kodu, başlık, sürükleme tutamacı, checklist rozeti (`TaskChecklistBadge.qml`), tip/öncelik/durum rozetleri ve hover'da beliren hızlı butonlar (`HoverHandler` ile satırın tamamını izler). Satır altı checklist paneli `TaskChecklistPanel.qml`, sağ tık menüsü `TaskContextMenu.qml` bileşenindedir.
- **`presentation/qml/dialogs/TaskDialog.qml`** — oluşturma/düzenleme: başlık, açıklama, durum, öncelik, tip, engel nedeni (yalnızca Engellendi'de) ve checklist (`TaskChecklistSection.qml`). Alt görevi olan görevlerde durum seçenekleri "Otomatik / Engellendi / İptal"dir.
- **`presentation/viewmodels/task_viewmodel.py` + `task_list_model.py`** — filtre ve seçim durumu, ağaç düzleştirme, WBS kodu üretimi, kopyalama/çoğaltma (`task_clipboard.py` saf yardımcı).
- **`presentation/viewmodels/task_dialog_viewmodel.py`** — diyalog durumu (`taskDialogViewModel` QML bağlamı), form → servis alanı dönüşümü ve kaydetme; seçili proje ve görev önbelleğini `TaskViewModel.current_project_id()` / `cached_tasks()` ile okur.

## Sıralama davranışı
`TaskService.create_task` yeni görevi `TaskRepository.first_order_index()` ile kardeş
grubunun BAŞINA alır (kardeş grubundaki en küçük `order_index - 1`; grup boşsa `0`) —
WBS ağacında yeni görev en üste çıkar (2026-07-02, önceden sona ekleniyordu). DONE'a
geçen görev (`_apply_status_side_effects`, `update_task`/`toggle_status` üzerinden
çağrılır) ise ayrı ve DEĞİŞMEYEN bir mekanizmayla, `TaskRepository.next_order_index()`
(kardeş grubunun en büyük `order_index + 1`) ile kardeş grubunun SONUNA alınır —
tamamlanan görevler listenin en altına inmeye devam eder. İki metod kasıtlı olarak
ayrı tutulur: aynı `order_index` hesaplayıcısı hem "başa ekle" hem "sona ekle" için
kullanılamaz.

## Sürükle-bırak ile taşıma
Fare sol tuşla satırda yaklaşık 6 px sürüklenince taşıma başlar. Satırın üst kenarı (ilk 14 px) hedefin **önüne**, orta bölümü hedefin **altına** (alt görev, çocukların sonuna), 34 px'in altı hedefin **arkasına** bırakır. Önüne/arkasına bırakmada araya çizgi çizilir, alta bırakmada hedef satır vurgulanır; imleci hayalet kart izler, kaynak satır soluklaşır. Liste kenarına 28 px yaklaşınca otomatik kaydırılır. Sürükleme sırasında model sıfırlanırsa taşıma iptal edilir.

Zincir: `TasksView.finishDrag` → `TaskViewModel.moveTaskRelative(dragged, target, position)` → `task_reorder.compute_relative_move` (saf fonksiyon) → `TaskController.move_task` → `TaskService.move_task`.

- Görev kendisine veya kendi alt soyuna bırakılamaz: `compute_relative_move` `None` döner (sessizce yok sayılır); servis ayrıca `_validate_parent` ile denetler.
- `move_task` yeni kardeş grubunu `0`'dan yeniden numaralar; üst görev değiştiyse eski grubu da numaralar, `TASK_MOVED` etkinliğini yazar ve hiyerarşiyi yeniden hesaplar (aşağıdaki "Durum kuralı").
- Alta bırakmada hedef düğüm açık tutulur (`TaskListModel.expand_node`).

## Checklist
- Maddesi olan görevde satıra sol tıklamak veya `tamamlanan/toplam` rozetine tıklamak satır altı paneli açıp kapatır. Panelde madde işaretlenir ve (hover'daki düğmeyle) silinir; yeni madde görev diyaloğundan eklenir.
- Açık paneller `TaskListModel` içinde tutulur: liste yenilenince korunur, proje değişince sıfırlanır. Model rolleri: `checklistItems`, `isChecklistExpanded`.
- Düzenleme diyaloğundaki ekleme, silme ve işaretlemeler **Kaydet** ile uygulanır: `TaskDialogViewModel._sync_checklist_items` mevcut maddeleri id ile eşler, listeden çıkanları siler.

## Veri akışı
`TaskController.load_tasks` (Worker, async — [[worker-altyapisi]]) → `tasks_loaded(project_id, tasks)` → `TaskViewModel._on_tasks_loaded` → `TaskListModel`. Görev değişiminde controller `task.*` olayını [[event-bus]]'a yayınlar; ViewModel'ler kendi sinyal/olay bağlantılarıyla listeyi yeniler.

## Durum kuralı
Alt görevi olan görevin durumu alt görevlerinden türetilir (`TaskService.recalculate_hierarchy`): hiçbiri başlamadıysa Yapılacak, biri bile ilerlediyse Devam Ediyor. **Tüm alt görevler bitse bile üst görev kendiliğinden Tamamlandı olmaz**; onay kutusuyla (ya da diyalogdan Tamamlandı seçerek) kullanıcı kapatır, ancak o zaman kök listenin sonuna iner. Biten alt görev yalnızca kendi kardeş grubunun sonuna geçer. `TaskService._assert_status_editable` türetilen duruma (Yapılacak/Devam Ediyor/Bekliyor) elle geçişi `TaskValidationError` ile reddeder; elle yalnızca Tamamlandı, Engellendi ve İptal verilebilir ve bu üç durum yeniden hesaplamada korunur. Controller hataları `forward_errors_to_toast` ile kullanıcıya gösterilir.

## QML Sunum Katmanı ve Gelişmiş Özellikler (2026-10)

`presentation/viewmodels/task_viewmodel.py`, `presentation/viewmodels/task_list_model.py` ve `presentation/qml/views/TasksView.qml`:
- **Panoya Kopyalama ve Çoğaltma (Duplicate):** `TaskViewModel.copyTaskToClipboard(task_id)` ile görev detayları panoya kopyalanabilir; `TaskViewModel.duplicateTask(task_id)` ile görev ve checklist maddeleri (işaretsiz olarak) aynı üst görevin altına çoğaltılır; alt görevler kopyalanmaz. UI'da sağ tık menüsü ve butonlar üzerinden erişilir.
- **Akıllı Ağaç Daraltma (Auto-Collapse):** `TaskListModel` hiyerarşi oluştururken, alt görevleri bulunan ve kendisi dahil tüm alt görevleri `DONE` (tamamlandı) durumunda olan görev dallarını varsayılan olarak kapalı tutar. Kullanıcı tamamlanan işlerin kalabalığı yerine açık kalan işlere odaklanır.
- **Kaydırma Konumunun Korunması (Scroll Preservation):** Görev durumu değiştirildiğinde veya silme/çoğaltma yapıldığında liste modeli resetlenirken `TasksView.qml` içerisindeki `savedScrollY` değişkeni mevcut kaydırma pozisyonunu saklar ve model yüklendiğinde otomatik olarak eski konuma geri döndürür.
- **Son Seçili Proje Kalıcılığı ve Proje Sekmesinden WBS Geçişi:** `TaskViewModel` seçili projeyi `PreferenceManager` (`ui/last_task_project_id`) üzerinden saklar ve Görevler sayfasına her dönüşte (ve uygulama yeniden açıldığında) en son kalınan projeyi yükler. Projeler sayfasındaki Görevler sekmesinden (`ProjectTasksTab.qml`) "WBS Sayfasında Aç" butonuna basıldığında doğrudan o projenin WBS ağacı açılır.

## Hızlı görev ekleme
Görev listesinin altındaki satır (`TasksView.qml`): tek satırlık alan + mikrofon (`showVoiceInput`) + "Hızlı Ekle" düğmesi. Enter veya düğme `TaskViewModel.quickAddTask(title)` çağırır; bir görev seçiliyse yeni görev onun altına (alt görev), seçili değilse proje köküne eklenir; boş metin yok sayılır, başarıda toast gösterilir. Sesle dikte metni alana yazar, görevi kullanıcı onaylayarak ekler ([[sesli-komut]]).

## Import
`from presentation.viewmodels.task_viewmodel import TaskViewModel` (QML ViewModel).

İlgili: [[mimari-genel-bakis]], [[l10n-string-yonetimi]], [[notlar-modulu]]
