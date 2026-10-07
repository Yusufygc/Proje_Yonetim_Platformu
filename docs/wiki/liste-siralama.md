# Liste Sıralama (Sürükle-Bırak)

> **Durum (2026-10-07):** Notlar, Fikirler, Projeler ve Notlarım listelerindeki sürükle-bırak
> sıralama arayüzü eski Widgets arayüzüyle birlikte kaldırıldı. QML arayüzünde karşılığı
> **yoktur**; listeler `sort_order` / `display_order` değerine göre sıralı gelir ama kullanıcı
> sırayı değiştiremez. Altyapı (kolonlar, `reorder` zinciri) bilinçli olarak korunuyor; QML'de
> sürükle-bırak yeniden eklenirse doğrudan kullanılabilir.

## Mimari zincir (backend, hâlâ geçerli)

```
Controller.reorder(ids) → Service.reorder(ids) → Repository.reorder(ids) → BaseRepository._apply_order
```

## Veri katmanı

- `Note.sort_order`, `Idea.sort_order` ve `Memo.sort_order` kolonları (`Integer, default=0`). `Project.display_order` ayrıca mevcuttur.
- Alembic `0006_add_list_sort_order` (notes/ideas) ve `0007_add_memo_sort_order` (memos); in-memory test yolu için `infrastructure/database/migration_runner.py` eşleniği çalışır ([[veritabani-katmani]]). Migration'lar **backfill** yapar: önceki görsel sırayı (memos `updated_at`, diğerleri `created_at` azalan) koruyacak artan değerler atanır.
- `BaseRepository._apply_order(ordered_ids, order_field)`: id listesindeki sırayı 0'dan başlayarak ilgili kolona yazar (`NoteRepository`/`IdeaRepository`/`MemoRepository` → `sort_order`, `ProjectRepository` → `display_order`).
- Repository `order_by` ifadeleri: `Note`/`Idea`/`Memo` için `(sort_order, id)`; `Project` için `(display_order, created_at)`.

## Servis / Controller

`NoteService`/`IdeaService`/`ProjectService`/`MemoService.reorder(ordered_ids)` — boş liste guard clause'u, repo'ya delege. Controller `reorder` metotları senkron çağırır ("yazmalar senkron" kararı, bkz. [[worker-altyapisi]]); hata durumunda `error_occurred` sinyali.

İlgili: [[worker-altyapisi]], [[veritabani-katmani]], [[log]]
