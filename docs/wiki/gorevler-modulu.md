# Görevler Modülü (WBS)

QML arayüzü (eski Widgets `presentation/pages/tasks/` paketi 2026-10-07'de kaldırıldı):

- **`presentation/qml/views/TasksView.qml`** — istatistik çubuğu, görev ağacı ve hızlı ekleme; araç çubuğu (proje seçici, arama, durum/öncelik/tip filtreleri, ana görev ekleme) `tasks/TaskToolbar.qml` bileşenindedir.
- **`presentation/qml/views/tasks/TaskItemDelegate.qml`** — ağaç satırı: durum kutusu, WBS kodu, başlık, checklist rozeti, tip/öncelik/durum rozetleri ve hover'da beliren hızlı butonlar (`HoverHandler` ile satırın tamamını izler).
- **`presentation/qml/dialogs/TaskDialog.qml`** — oluşturma/düzenleme: başlık, açıklama, durum, öncelik, tip, engel nedeni (yalnızca Engellendi'de) ve checklist. Alt görevi olan görevlerde durum seçenekleri "Otomatik / Engellendi / İptal"dir.
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

## Veri akışı
`TaskController.load_tasks` (Worker, async — [[worker-altyapisi]]) → `tasks_loaded(project_id, tasks)` → `TaskViewModel._on_tasks_loaded` → `TaskListModel`. Görev değişiminde controller `task.*` olayını [[event-bus]]'a yayınlar; ViewModel'ler kendi sinyal/olay bağlantılarıyla listeyi yeniler.

## Durum kuralı
Alt görevi olan görevin durumu alt görevlerinden türetilir (`TaskService.recalculate_hierarchy`); `TaskService._assert_status_editable` türetilen duruma elle geçişi `TaskValidationError` ile reddeder, yalnızca Engellendi ve İptal elle verilebilir. Controller hataları `forward_errors_to_toast` ile kullanıcıya gösterilir.

## QML Sunum Katmanı ve Gelişmiş Özellikler (2026-10)

`presentation/viewmodels/task_viewmodel.py`, `presentation/viewmodels/task_list_model.py` ve `presentation/qml/views/TasksView.qml`:
- **Panoya Kopyalama ve Çoğaltma (Duplicate):** `TaskViewModel.copyTaskToClipboard(task_id)` ile görev detayları panoya kopyalanabilir; `TaskViewModel.duplicateTask(task_id)` ile alt görevleriyle birlikte klonlanarak listeye anında eklenebilir. UI'da sağ tık menüsü ve butonlar üzerinden erişilir.
- **Akıllı Ağaç Daraltma (Auto-Collapse):** `TaskListModel` hiyerarşi oluştururken, alt görevleri bulunan ve kendisi dahil tüm alt görevleri `DONE` (tamamlandı) durumunda olan görev dallarını varsayılan olarak kapalı tutar. Kullanıcı tamamlanan işlerin kalabalığı yerine açık kalan işlere odaklanır.
- **Kaydırma Konumunun Korunması (Scroll Preservation):** Görev durumu değiştirildiğinde veya silme/çoğaltma yapıldığında liste modeli resetlenirken `TasksView.qml` içerisindeki `savedScrollY` değişkeni mevcut kaydırma pozisyonunu saklar ve model yüklendiğinde otomatik olarak eski konuma geri döndürür.

## Hızlı görev ekleme
Görev listesinin altındaki satır (`TasksView.qml`): tek satırlık alan + mikrofon (`showVoiceInput`) + "Hızlı Ekle" düğmesi. Enter veya düğme `TaskViewModel.quickAddTask(title)` çağırır; bir görev seçiliyse yeni görev onun altına (alt görev), seçili değilse proje köküne eklenir; boş metin yok sayılır, başarıda toast gösterilir. Sesle dikte metni alana yazar, görevi kullanıcı onaylayarak ekler ([[sesli-komut]]).

## Import
`from presentation.viewmodels.task_viewmodel import TaskViewModel` (QML ViewModel).

İlgili: [[mimari-genel-bakis]], [[l10n-string-yonetimi]], [[notlar-modulu]]
