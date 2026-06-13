# L10N — Merkezi String Yönetimi

## Bileşenler
- `core/managers/string_manager.py` — `StringManager(QObject)`, JSON tabanlı; `language_changed = Signal(str)` (2026-06-12'de eklendi). `set_language` aynı dile çağrılırsa no-op.
- `resources/locales/strings.tr.json` — tek doğruluk kaynağı (247 anahtar).
- `presentation/utils/i18n.py` — `tr(key, default)` ortak yardımcısı. Dosya başına `_tr` tanımlamak YASAK (eski kopyalar birleştirildi).

## Anahtar isimlendirme
- Modül özel: `<modül>_<öğe>` → `project_dialog_title_label`, `task_quick_add_button`.
- Yeniden kullanılabilir genel: `action_*` (save/create/cancel/edit/delete), `label_*` (status/priority/health/tags...), `status_*`, `priority_*`, `health_*`, `project_type_*`, `nav_*`, `filter_*`.
- Yeni dialog migrate ederken ÖNCE genel anahtarları kullan, yoksa modül öneki aç.

## Ratchet regresyon testi
`tests/test_l10n_no_hardcoded.py` — AST ile `presentation/` tarar:
- Muaf: `tr()/_tr()/StringManager.get()` argümanları (bilinçli default'lar), docstring'ler ve pragma'lı satırlar: `# l10n: data` (saklanan veri — örn. DB'deki `project_type` değerleri, nav fallback'leri), `# l10n: log` (geliştiriciye dönük log mesajları).
- Çift yönlü kilit: ALLOWLIST dışı dosyada Türkçe literal → FAIL; ALLOWLIST'teki dosya temizlenince → FAIL (listeden çıkar).

## Migrasyon durumu: ✅ TAMAMLANDI (2026-06-13)
- `presentation/` altındaki TÜM dosyalar StringManager'a taşındı; **ALLOWLIST boş** ve boş kalmak zorunda — yeni dosyada hardcoded Türkçe metin testi anında kırar.
- Enum etiketleri paylaşımlı: `status_*`, `priority_*`, `task_status_*`, `task_type_*`, `idea_status_*`, `stage_status_*`, `health_*`; genel: `action_*`, `label_*`, `tab_*`, `search_type_*`.
- Desen notu: enum etiket sözlükleri modül seviyesinde sabit DEĞİL, fonksiyon olarak tanımlanır (`_status_labels()` vb.) — dil değişimi dialog/panel her açılışta yansır.
- SearchDialog `item_selected` artık dilden bağımsız tip kodu yayar ("project"|"task"|"idea") — eski hali Türkçe etiketle eşleşiyordu (kırılgan veri bağı giderildi, `main_window._on_search_item_selected` buna göre güncellendi).
## Dil seçici (2026-06-13)
- `strings.en.json` eklendi (TR ile birebir 249 anahtar). Parite testi `test_locale_files_have_matching_keys_and_placeholders`: tüm dil dosyalarında anahtar seti VE `{placeholder}` alanları eşleşmek zorunda — yeni anahtar eklerken her iki dosyaya da yaz.
- Ayarlar sayfasında dil combobox'ı (`_LANGUAGES` sabiti; dil adı kendi dilinde, `# l10n: data`). Seçim: `PreferenceManager.save_language` + `StringManager.set_language` + "yeniden başlatın" bilgisi.
- Kalıcılık: `di_container.bootstrap` UI kurulmadan ÖNCE `prefs.load_language()` uygular — açılışta tüm `tr()` çağrıları doğru sözlükle çözülür (tema kalıcılığıyla aynı desen).
- Bilinçli karar: canlı retranslate YOK. Statik metin kuran 30+ widget'a retranslate makinesi yazmak yerine değişiklik yeniden başlatmada etkinleşir; `language_changed` sinyali yine yayınlanır, ileride isteyen widget abone olabilir.

İlgili: [[kurallar-ve-sozlesmeler]], [[yol-haritasi]]
