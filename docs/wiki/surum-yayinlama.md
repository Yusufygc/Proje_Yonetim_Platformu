# Sürüm Yayınlama Süreci

Uygulamanın yeni sürümü **etiket** ile yayınlanır: `vX.Y.Z` etiketi push edilince GitHub Actions installer'ı derler ve GitHub Releases'e yükler. Kurulu uygulamalar açılışta bu yayını görüp güncelleme teklif eder ([[guncelleme-sistemi]]). Kuralın bağlayıcı metni: `Project_docs/RULES.md` §8.

## Sürüm numarası

- Biçim: `MAJOR.MINOR.PATCH` (örn. `0.2.0`). Etiketin başına `v` konur (`v0.2.0`).
- Güncelleyici yalnızca bu üç sayılı biçimi tanır ve sayısal karşılaştırır (`0.10.0 > 0.9.0`). `1.0.0-beta` gibi ön sürüm adları yok sayılır.
- **Tek kaynak:** `app/config.py` içindeki `APP_VERSION`. Diğer üç yer (`pyproject.toml`, `packaging/version_info.txt`, `installer/windows.iss`) `scripts/set_version.py` ile aynı değere çekilir; elle düzenlenmez.
- Artış kuralı: hata düzeltme ve küçük iyileştirme → PATCH; yeni özellik → MINOR; geriye dönük uyumsuz veri/şema değişikliği → MAJOR.

## Yayın adımları

Ön koşul: yayınlanacak commit'te CI yeşil (`ruff`, `mypy`, `pytest`) ve çalışma ağacı temiz.

```powershell
python scripts/set_version.py 0.2.0
git commit -am "chore(surum): v0.2.0 sürümü hazırlandı"
git tag v0.2.0
git push origin <dal> v0.2.0          # --follow-tags KULLANMA: hafif etiketleri göndermez
gh run watch                          # Release iş akışını izle (~8 dk)
gh release view v0.2.0                # yayın, installer ve SHA-256 özeti oluştu mu
```

Release iş akışı (`.github/workflows/release.yml`) sırayla şunları yapar:

1. Etiket (`v0.2.0`) ile `APP_VERSION` aynı değilse **durur**.
2. `pytest` koşar; kırmızıysa yayın yapılmaz.
3. Vosk Türkçe modelini indirir (boyutu nedeniyle depoda yok).
4. PyInstaller ile klasör modunda derler (`packaging/proje_takip_platformu_dir.spec`).
5. Inno Setup ile `ProjeTakipPlatformuSetup.exe` üretir (`installer/windows.iss`).
6. `gh release create` ile yayınlar; sürüm notları commit mesajlarından otomatik üretilir. Bu yüzden commit mesajları kullanıcıya görünür: anlaşılır ve Türkçe yazılır.

## Kontrol listesi

- [ ] CI yeşil, `python -m pytest tests/ -q` yerelde geçiyor.
- [ ] Davranış değişikliği varsa `README.md` ve ilgili wiki sayfası güncel ([[kurallar-ve-sozlesmeler]]).
- [ ] `set_version.py` çalıştırıldı, dört dosya aynı sürümde.
- [ ] Etiket sürümle birebir aynı (`v` + `APP_VERSION`).
- [ ] Release iş akışı yeşil, `gh release view` installer ve `sha256:` özetini gösteriyor.
- [ ] Veritabanı şeması değiştiyse Alembic migration'ı pakete giriyor ve eski veriyle denendi (kullanıcı verisi güncellemede korunur).

## Hata ve geri alma

| Durum | Ne yapılır |
|---|---|
| Etiket ile `APP_VERSION` farklı, iş akışı durdu | Yayın oluşmadı. `set_version.py` ile düzelt, commit et, etiketi yeni commit'e taşı: `git tag -f vX.Y.Z` ve `git push -f origin vX.Y.Z`. |
| Derleme adımı düştü (yayın yok) | Sebebi düzelt, aynı yolla etiketi taşı. Yayın oluşmadığı için kimse etkilenmez. |
| Yayın oluştu ama sürüm hatalı | Etiketi taşıma. Yeni PATCH sürümü çıkar. Acilse `gh release delete vX.Y.Z --cleanup-tag`: güncelleyici `latest` yayına baktığından önceki sürüm tekrar "son sürüm" olur. |
| `git push --follow-tags` etiketi göndermedi | Hafif etiketler gitmez. `git push origin vX.Y.Z` ile etiketi ayrıca gönder. |
| `PyInstaller` vosk DLL'i bulamadı | Spec, DLL yolunu kurulu paketten bulur; sabit `.venv` yolu yazma. |
| CI'da `pytest` 15 dk sonra kesildi | Test nesnelerini (QML motoru, tuval) açıkça sil; takılan testin yığını `faulthandler_timeout` ile loga yazılır. |

## Güvenlik ve sınırlar

- Yayın, tüm kurulu kullanıcılara güncelleme penceresi çıkarır. **Yapay zeka asistanları kullanıcının açık isteği olmadan etiket oluşturmaz, etiket push etmez.**
- İndirme adresi yalnızca bu deponun `releases/download/` yolu olabilir; GitHub'ın verdiği SHA-256 özeti doğrulanır. Bu kontroller kaldırılmaz.
- Installer imzasızdır; Windows SmartScreen uyarı verebilir. Kod imzalama ayrı bir iştir.
- Yalnızca Windows. "Bu sürümü atla" ve otomatik güncellemeyi kapatma ayarı yoktur.

İlgili: [[guncelleme-sistemi]], [[kurallar-ve-sozlesmeler]], [[yol-haritasi]]
