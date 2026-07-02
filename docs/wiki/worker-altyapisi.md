# Worker Altyapısı (Asenkron İşlem)

`core/workers/worker.py` — `Worker(QRunnable)` + `WorkerSignals(QObject)`; `QThreadPool.globalInstance()` üzerinde çalışır.

## GC güvenliği
- `setAutoDelete(False)` + sınıf seviyesi `_active_workers` seti: worker, `finished` sinyali işlenene kadar GC'den korunur; `_cleanup` referansı bırakır.

## Kullanım deseni (controller'larda)
```python
worker = Worker(self._service.get_tasks, project_id)
worker.signals.result.connect(self.tasks_loaded.emit)
worker.signals.error.connect(self._on_error)
worker.start()
```

## Karar: okumalar async, yazmalar senkron (2026-06-12)
- `load_*` çağrıları Worker ile arka planda → UI kilitlenmez.
- `create/update/delete/toggle` UI thread'inde senkron: SQLite WAL'de ms seviyesinde; async geçişin sinyal sıralaması riski kazancı aşıyor. Büyük toplu işlem (WBS alt ağaç silme) yavaşlarsa yeniden değerlendirilecek ([[log]]).

**Tutarlılık düzeltmesi (2026-07-02):** `NoteController.load_project_notes`, `MemoController.load_all`,
`DashboardController.load_stats`, `AnalyticsController.load_analytics` üretime hazırlık denetiminde
senkron kaldıkları tespit edildi (standart o zamana kadar sadece Proje/Görev/Fikir controller'larında
uygulanmıştı) — dördü de aynı closure deseniyle Worker'a taşındı. Özellikle `DashboardController`
10 farklı domain olayında (`project.*`/`task.*`/`idea.*`) tetiklendiğinden, art arda gelen olaylarda
UI thread'in kilitlenmemesi en çok burada fayda sağlıyor.

## Thread + DB uyumu
`check_same_thread=False` + `scoped_session` + `finally: remove()` → havuz thread'lerinde session sızıntısı yok ([[veritabani-katmani]]).

İlgili: [[mimari-genel-bakis]], [[event-bus]]
