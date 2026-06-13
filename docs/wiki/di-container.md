# DI Container ve Bootstrap

`di_container.py` — `DIContainer.instance()` singleton; tüm repo/servis/controller fabrikaları burada.

## Bootstrap sırası (kritik)
1. `DatabaseManager.instance(url)` — engine + WAL ([[veritabani-katmani]])
2. `ThemeManager.instance(themes_dir, styles_dir)` — sonra `prefs.load_theme()` ile kayıtlı tema uygulanır (`switch_theme`); yani tema kalıcılığı bootstrap'te çözülür ([[tema-sistemi]])
3. `IconManager.instance(icons_dir)` ([[ikon-yonetimi]])
4. `StringManager.instance(locales_dir)` ([[l10n-string-yonetimi]])
5. Migration: `db.run_migrations()` (Alembic)

## Registry mimarisi (2026-06-12'de bölündü)
`di_registries.py` üç katman registry'si içerir; her biri `@cached_property` ile lazy üretir:
- `RepositoryRegistry(db)` → `repos.task`, `repos.project`, ... (12 repo)
- `ServiceRegistry(repos, db)` → `services.task`, `services.project`, ... (10 servis)
- `ControllerRegistry(services, event_bus)` → `controllers.task_controller`, ... (10 controller)

`DIContainer` ince facade: `bootstrap()` + infra property'leri + `repos/services/controllers` erişimcileri. Geriye dönük uyumluluk: `di.task_controller` çağrıları `__getattr__` ile `controllers` registry'sine delege edilir — eski çağrı kodu değişmedi.

## Constructor injection (2026-06-13'te tamamlandı)
UI widget'ları artık manager'ları Service Locator yerine constructor parametresi olarak alır. Desen:
```python
def __init__(self, parent, theme: ThemeManager | None = None) -> None:
    self._theme = theme or ThemeManager.instance()  # test/standalone için fallback
```
Factory akışı:
- `presentation/modules.py` sayfa factory'leri `theme=di.theme`, `strings=di.strings`, `prefs=di.prefs` geçirir.
- Sayfa, child widget'lara forward eder: `WBSTreeWidget(theme=self._theme)`, `SkeletonLoader(theme=self._theme)`, `StageTimelineWidget(theme=self._theme)`, `ResourceListWidget(theme=self._theme)`, `SidebarNavButton(theme=..., icons=...)`.
- `Sidebar` artık `icons` ve `prefs`'i de constructor'dan alır; `Toast` `event_bus`'ı.
- `ProjectsPage` `event_bus`'ı `di_container.event_bus`'tan alır (eski `EventBus.instance()` çağrıları silindi).

Tek istisna: `MainWindow` kompozisyon kökü olduğu için DI'den `getattr(...) or ...instance()` fallback'iyle çeker — testte bootstrap olmadan da çalışır.

## Public erişimciler
`db`, `theme`, `fonts`, `prefs`, `secrets`, `icons` (2026-06-13'te eklendi), `strings` (2026-06-13'te eklendi), `event_bus`, `repos`, `services`, `controllers`.

İlgili: [[mimari-genel-bakis]], [[event-bus]]
