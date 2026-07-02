# Görevler Modülü (WBS)

`presentation/pages/tasks/` paketi (2026-06-12'de 493 satırlık `tasks_page.py`'den bölündü):

- **`page.py` — TasksPage**: kompozisyon + controller köprüsü + CRUD dialog akışları. Test API'leri korunur: `_tree`, `_quick_add_edit`, `_on_quick_add_task` (bkz. `tests/test_ui_smoke.py`).
- **`filter_bar.py` — TaskFilterBar**: proje combo + durum/öncelik/tür/aşama filtreleri. Filtre mantığının tek sahibi: `apply(tasks)`, `filter_values()` (hızlı eklemede yeni göreve uygulanır), `reload_stage_filter(tasks)`. Sinyaller: `project_changed(object)`, `filters_changed()`, `add_root_requested()`.
- **`wbs_tree.py` — WBSTreeWidget**: render + sürükle-bırak + fade animasyonu. `task_moved = Signal(int, object, int)` (id, yeni parent|None, yeni sıra). `render_tasks()` renkleri döngü dışında bir kez çözer, `setUpdatesEnabled(False/True)` sarmalı kullanır; tema sözleşmesi gereği sayfa `theme_changed`'de yeniden render eder ([[tema-sistemi]]).

## Sıralama davranışı
`TaskService`: yeni görev (`create_task`) ve DONE'a geçen görev (`_apply_status_side_effects`,
`update_task`/`toggle_status` üzerinden çağrılır — 2026-07-02) `order_index`'i her zaman
`TaskRepository.next_order_index()` ile kardeş grubunun sonuna alır — WBS ağacında yeni/biten
görevler listenin en altına iner, elle hesaplanmayan `order_index` varsayılan `0`'da kalıp
başa/ortaya düşmez.

## Veri akışı
`TaskController.load_tasks` (Worker, async — [[worker-altyapisi]]) → `tasks_loaded` → sayfa `_on_tasks_loaded` → filtre + render. Görev değişiminde controller `task.*` olayını [[event-bus]]'a yayınlar; sayfa kendi sinyal bağlantısıyla listeyi yeniler.

## Import
`from presentation.pages.tasks import TasksPage` (eski `tasks_page` modülü silindi).

İlgili: [[mimari-genel-bakis]], [[l10n-string-yonetimi]]
