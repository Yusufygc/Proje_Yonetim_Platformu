# DI Container ve Bootstrap

`app/di_container.py` — `DIContainer.instance()` singleton; repo/servis/controller fabrikaları `app/di_registries.py` içindedir.

## Bootstrap sırası (kritik)
1. Veri dizinleri (`config.ensure_data_dirs`) ve loglama
2. `DatabaseManager.instance(url)` + `run_migrations()` ([[veritabani-katmani]])
3. `PreferenceManager`; eski tema adları yeni paketlere çevrilir
4. `ThemeManager`; kayıtlı tema `switch_theme` ile uygulanır ([[tema-sistemi]])
5. `FontManager`, `IconManager` ([[ikon-yonetimi]])
6. `StringManager`; kayıtlı dil UI kurulmadan önce uygulanır ([[l10n-string-yonetimi]])
7. `EventBus` ([[event-bus]])

Veri dizini taşıma (`config.migrate_legacy_data_dir`) bootstrap'ten önce, `main_qml.py` içinde çalışır.

## Registry mimarisi (2026-06-12'de bölündü)
`di_registries.py` üç katman registry'si içerir; her biri `@cached_property` ile lazy üretir:
- `RepositoryRegistry(db)` → `repos.task`, `repos.project`, ... (13 repo)
- `ServiceRegistry(repos, db)` → `services.task`, `services.project`, ... (14 servis)
- `ControllerRegistry(services, event_bus)` → `controllers.task_controller`, ... (13 controller)

`DIContainer` ince facade: `bootstrap()` + infra property'leri + `repos/services/controllers` erişimcileri. Geriye dönük uyumluluk: `di.task_controller` çağrıları `__getattr__` ile `controllers` registry'sine delege edilir — eski çağrı kodu değişmedi.

## Constructor injection
ViewModel ve köprü sınıfları (`presentation/viewmodels/`) bağımlılıklarını `DIContainer`'dan constructor parametresiyle alır (`ProjectViewModel(di)`, `SettingsViewModel(container)`); `main_qml.py` bunları oluşturup QML bağlamına (`setContextProperty`) kaydeder. Controller/servis/manager erişimi `di.<ad>` üzerinden yapılır; ViewModel'ler servislere doğrudan değil controller'lar üzerinden gider.

## Public erişimciler
`db`, `theme`, `fonts`, `prefs`, `icons` (2026-06-13'te eklendi), `strings` (2026-06-13'te eklendi), `event_bus`, `speech_service`, `repos`, `services`, `controllers`.

İlgili: [[mimari-genel-bakis]], [[event-bus]]
