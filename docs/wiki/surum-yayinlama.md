# Sürüm Yayınlama Süreci

Uygulamanın yeni sürümü **etiket** ile yayınlanır: `vX.Y.Z` etiketi push edilince GitHub Actions testleri koşar, kararlı exe kapısından geçirerek kurulum dosyasını derler ve GitHub Releases'e yükler. Kurulu uygulamalar açılışta bu yayını görüp güncelleme teklif eder ([[guncelleme-sistemi]]). Kuralın bağlayıcı metni: `docs/Project_docs/RULES.md` §8.

## Sürüm numarası

- Biçim: `MAJOR.MINOR.PATCH` (örn. `0.2.0`). Etiketin başına `v` konur (`v0.2.0`).
- Güncelleyici yalnızca bu üç sayılı biçimi tanır ve sayısal karşılaştırır (`0.10.0 > 0.9.0`). `1.0.0-beta` gibi ön sürüm adları yok sayılır.
- **Tek kaynak:** `version.py` içindeki `__version__` (ve `APP_NAME`, `DISPLAY_NAME`, `RELEASE_REPO`). `app/config.py` ve `build_installer.py` doğrudan `version.py`'den okur; `README.md` rozeti `tools/release.py` ile güncellenir (elle düzenlenmez).
- **Sabit exe sürüm kaynağı:** `packaging/launcher_version_info.txt` SAC kararlılığı için her sürümde `1.0.0.0` kalır ([[exe-dagitim-rehberi]]). Ürün sürümü kurulum dosyası adında, Inno Uninstall kaydında (`/DAppVersion`) ve uygulama ayarlarında görünür.
- Artış kuralı: hata düzeltme ve küçük iyileştirme → PATCH; yeni özellik → MINOR; geriye dönük uyumsuz veri/şema değişikliği → MAJOR.

## Yayın adımları

Ön koşul: yayınlanacak commit'te CI yeşil (`ruff`, `mypy`, `pytest`), çalışma ağacı temiz, aktif dal `main`.

```powershell
python tools/release.py 0.2.0          # version.py + README rozeti -> "chore(release): v0.2.0" commit + v0.2.0 etiketi (itmez)
git push origin main
git push origin v0.2.0                 # --follow-tags KULLANMA: hafif etiketleri göndermez
gh run watch                           # Release iş akışını izle
gh release view v0.2.0                 # yayın, ProjeTakipPlatformu-Setup-0.2.0.exe ve .sha256 oluştu mu
```

Release iş akışı (`.github/workflows/release.yml`) sırayla şunları yapar:

1. Etiket (`v0.2.0`) ile `version.py` aynı değilse **durur** (`tools/release.py --check-tag "$env:TAG"`).
2. Sabitlenen bağımlılıkları (`-c requirements-lock.txt`) kurar; `ruff check .` ve `pytest tests/ -q` koşar (kırmızıysa yayın yapılmaz).
3. Vosk Türkçe modelini `resources/models/vosk-model-small-tr-0.3` altına indirir.
4. `python build_installer.py`: PyInstaller `--onedir --debug=noarchive` ile derler, **exe özetini `packaging/launcher.sha256` ile doğrular**, Inno Setup 6 ile `ProjeTakipPlatformu-Setup-X.Y.Z.exe` ve `.sha256` üretir.
5. `gh release create`: kurulum dosyası ve `.sha256` dosyasını `--verify-tag` ile yayınlar; `-` içeren etiket ön sürüm (`--prerelease`) olur.

## Kontrol listesi

- [ ] CI yeşil (`ruff`, `mypy`, `pytest`), çalışma ağacı temiz, dal `main`.
- [ ] Davranış değişikliği varsa `README.md` ve ilgili wiki sayfası güncel ([[kurallar-ve-sozlesmeler]]).
- [ ] `tools/release.py X.Y.Z` çalıştırıldı, `version.py` ve `README.md` rozeti aynı sürümde.
- [ ] CI günlüğünde `[kapı] Kararlı exe özeti onaylananla aynı` satırı var.
- [ ] Etiket sürümle birebir aynı (`v` + `__version__`).
- [ ] Release iş akışı yeşil, `gh release view` kurulum dosyasını ve `.sha256` dosyasını gösteriyor.
- [ ] Yayınlanan (MOTW'li) kurulum dosyası SAC'lı makinede indirilip denendi.

## Hata ve geri alma

| Durum | Ne yapılır |
|---|---|
| Etiket ile `__version__` farklı, iş akışı durdu | Yayın oluşmadı. Düzelt, commit et, etiketi taşı: `git tag -f vX.Y.Z` ve `git push -f origin vX.Y.Z`. |
| Kapı "Kararlı exe özeti DEĞİŞTİ" dedi | Derleme/yayın durur: [[exe-dagitim-rehberi]] §2 uyarınca nedeni incele veya yeni özeti yerelde test edip onayla. |
| Yayın oluştu ama sürüm hatalı | Yayınlanmış etiketi taşıma. Yeni PATCH sürümü çıkar. Acilse `gh release delete vX.Y.Z --cleanup-tag`: güncelleyici `latest` yayına baktığından önceki sürüm tekrar "son sürüm" olur. |
| `git push --follow-tags` etiketi göndermedi | `git push origin vX.Y.Z` ile etiketi ayrıca gönder. |
| Kurulu kullanıcıda güncelleme başlamadı | `%TEMP%\ProjeTakipUpdate\install.log` dosyasını kontrol et. |

## Güvenlik ve sınırlar

- Yayın, tüm kurulu kullanıcılara güncelleme penceresi çıkarır. **Yapay zeka asistanları kullanıcının açık isteği olmadan etiket oluşturmaz, etiket push etmez.**
- İndirme adresi yalnızca bu deponun `releases/download/` yolu olabilir; boyut ve SHA-256 özeti doğrulanır, özet yoksa güncelleme reddedilir.
- Kurulum dosyası imzasızdır; Windows SmartScreen ve SAC davranışı [[exe-dagitim-rehberi]] kapsamındadır.

İlgili: [[guncelleme-sistemi]], [[exe-dagitim-rehberi]], [[kurallar-ve-sozlesmeler]], [[yol-haritasi]]
