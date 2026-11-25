# EventBus (Pub/Sub)

`core/events/event_bus.py` — `EventBus.instance()` singleton; modüller arası gevşek bağ.

## Tasarım (2026-06-12 sonrası)
- **Bound method aboneleri `weakref.WeakMethod` ile tutulur**: sahibi (widget/controller) GC edilince abonelik publish sırasında otomatik düşer. `unsubscribe` çağrılmasa bile ölü Qt nesnesine yayın yapılmaz.
- **Lambda/serbest fonksiyonlar güçlü referans**: zayıf tutulsalar anında ölürlerdi.
- **`RuntimeError` yakalama**: PySide6'da C++ tarafı silinmiş nesneye çağrı `RuntimeError` üretir → abonelik düşürülür, diğer aboneler etkilenmez. Normal istisnalar (`ValueError` vb.) aboneliği DÜŞÜRMEZ, sadece loglanır.
- Yayın kopya liste üzerinde gezer (yayın sırasında subscribe/unsubscribe güvenli).

## Olay isimlendirme
`varlık.eylem` formatı: `task.created`, `task.updated`, `task.moved`, `task.deleted`, `project.created`, `idea.converted`, `toast.show`. Sayfalar arası istekler `core/events/app_events.py` sabitleriyle yayınlanır (`NEW_PROJECT_REQUESTED`, `PROJECT_DETAIL_REQUESTED`).

`DashboardController` `task.completed` olayına abonedir ancak kodda bu adla yayın yapılmıyor.

## Kullanım kuralı
- Yayın: controller katmanından (`EventBus.instance().publish(...)`).
- Abonelik: bound method tercih et (otomatik temizlik kazanırsın). Lambda abone olursan yaşam döngüsünü kendin yönet.
- Regresyon testleri: `tests/test_event_bus.py` (5 test: weak prune, unsubscribe, RuntimeError düşürme, generic exception koruması).

Gerekçe: toast/dashboard/stage controller'ları unsubscribe çağırmıyordu → silinmiş widget'a publish çökme riski (P0 bulgusu, [[yol-haritasi]]).

İlgili: [[mimari-genel-bakis]], [[di-container]], [[kurallar-ve-sozlesmeler]]
