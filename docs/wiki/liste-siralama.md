# Liste Sıralama (Sürükle-Bırak)

Notlar, Fikirler, Projeler ve Notlarım (memo) listelerinde kullanıcı elemanları
sürükleyerek kendi sırasını belirleyebilir. Öncesinde bu dört liste sabit sırayla
(tarih/id) render ediliyordu; artık her modelde kalıcı bir sıra kolonu var.

> **Not:** Notlarım (memo) desteği ilk sürümde eksik bırakılmıştı (kullanıcı
> raporuyla fark edildi, 2026-07-01) — `MemoPage` zaten `QListWidget` olduğundan
> Fikirler ile aynı `InternalMove` çözümü uygulandı, bkz. aşağıdaki UI katmanı.

## Mimari zincir

```
satır widget (sürükle) → DragReorderController (UI) → Controller.reorder(ids)
  → Service.reorder(ids) → Repository.reorder(ids) → BaseRepository._apply_order
```

Desen, WBS görev ağacındaki (`wbs_tree.py`) `task_moved` sinyali → `move_task`
zincirinin (bkz. [[worker-altyapisi]]) sürükle-bırak kısmına paralel kurgulandı.

## UI katmanı

İki farklı liste bileşeni için iki farklı çözüm:

- **Notlar** (`presentation/widgets/note_list_widget.py`) ve **Projeler**
  (`presentation/pages/projects_page.py`): manuel `QScrollArea + QVBoxLayout`
  kullandıklarından `QListWidget`'in `InternalMove` moduna sahip değiller.
  Bunun için yeniden kullanılabilir `presentation/widgets/drag_reorder.py` →
  `DragReorderController` yazıldı: satır widget'larına `mousePress/mouseMove`
  ile `QDrag` başlatır (sürüklenen satırın %70 opaklıkta "ghost" kopyası),
  bırakma hedefinin üst/alt yarısına göre ekleme noktası hesaplar, layout
  içindeki widget sırasını `removeWidget`/`insertWidget` ile günceller ve
  güncel id listesini `on_reorder` callback'ine iletir.
- **Fikirler** (`presentation/pages/ideas_page.py`) ve **Notlarım**
  (`presentation/pages/memo_page.py`): zaten `QListWidget` olduğundan yerleşik
  `setDragDropMode(InternalMove)` + `model().rowsMoved` sinyali kullanıldı;
  helper'a ihtiyaç yok.

Her satır widget'ı kendi varlık id'sini taşır (`_NoteRow.note_id`,
`ProjectListItem.project_id` property, `IdeaListItem.idea.id`,
`MemoListItem` → `UserRole` üzerinde `memo.id`);
`DragReorderController` bu id'yi bir `Callable[[QWidget], int | None]`
üzerinden okur — widget tipine bağımlı değildir, üç listede de aynı sınıf
kullanılır.

## Veri katmanı

- `Note.sort_order`, `Idea.sort_order` ve `Memo.sort_order` yeni kolonlar
  (`Integer, default=0`). `Project.display_order` zaten mevcuttu, değişmedi.
- Migration `006_add_list_sort_order` (notes/ideas/projects) ve
  `007_add_memo_sort_order` (memos) — `infrastructure/database/migration_runner.py`
  (in-memory/test yolu) ve Alembic `infrastructure/migrations/versions/0006_*`,
  `0007_*` (gerçek DB yolu, bkz. [[veritabani-katmani]] — production DB
  `command.upgrade(cfg, "head")` kullanır, legacy runner sadece bellek-içi test
  DB'si ve eski-şema köprüleme için çalışır). Her ikisi de **backfill** yapar:
  yeni kolon eklendiğinde tüm satırlar aynı varsayılanı (0) taşıyacağından,
  önceki görsel sırayı (memos `updated_at`, diğerleri `created_at` azalan)
  koruyacak artan değerler atanır. Aksi halde ilk açılışta sıra rastgele
  görünürdü.
- `BaseRepository._apply_order(ordered_ids, order_field)`: id listesindeki
  sırayı 0'dan başlayarak ilgili kolona yazan generic yardımcı; her repository
  kendi kolon adını geçirir (`NoteRepository`/`IdeaRepository`/`MemoRepository`
  → `sort_order`, `ProjectRepository` → `display_order`).
- Repository `order_by` ifadeleri güncellendi: `Note`/`Idea`/`Memo` artık
  `(sort_order, id)`; `Project` zaten `(display_order, created_at)`.

## Servis / Controller

`NoteService`/`IdeaService`/`ProjectService`/`MemoService.reorder(ordered_ids)`
— boş liste guard clause'u, repo'ya delege. Controller'lar (`NoteController`/
`IdeaController`/`ProjectController`/`MemoController.reorder`) senkron çağırır
(WAL modunda birkaç UPDATE, `move_task` ile aynı "yazmalar senkron" kararına
uyar, bkz. [[worker-altyapisi]]); hata durumunda toast yerine `error_occurred`
sinyali (mevcut controller hata deseni).

## Kapsam dışı

- Sürükleme sırasında insertion-indicator çizgisi (MVP: yalnızca ghost +
  bırakınca anlık yeniden sıralama).
- Listeler arası sürükleme (ör. bir notu başka projeye taşıma) — kapsam dışı.

İlgili: [[worker-altyapisi]], [[veritabani-katmani]], [[log]]
