# UX/UI Rapor — Yeni Tema Palet Geçişi Sonrası

**Tarih:** 2026-06-13 · **Branch:** `update` · **Kapsam:** 5 ekran görüntüsü (3 dark, 2 light)

Mevcut paletler:
- **Dark**: Federal Blue zemin (#00044A), Amber/Gold/Goldenrod accent ailesi.
- **Light**: Swan Wing zemin (#F5F0E9), Sapphire/Royal Blue ana renk, Quicksand vurgu, Shellstone kenarlık.

---

## 🔴 P0 — Kritik (Kullanılamazlık)

### 1. Açık tema sidebar metinleri okunmuyor (WCAG AA fail)

**Belirti:** Sidebar arka planı Royal Blue (`#112250`), nav öğesi metni `text_secondary = Sapphire (#3C507D)`. İkisi de derin lacivert ailesinden → kontrast oranı ~3.2:1, normal metin için WCAG AA eşiği 4.5:1.

Etkilenen: "Projeler", "Fikirler", "Görevler", "Bilgilendirme", "Ayarlar" — beşi de gri sis gibi, başlıklar bilinmeden buton bulunamaz. "Açık Tema" etiketi de aynı sorundan görünmez.

**Kök neden:** `sidebar.qss` nav button metni `@text_secondary` token'ına bağlı. Açık temada `text_secondary` Royal Blue üzerinde işlemeyen bir koyu mavi.

**Öneri:**
- Sidebar koyu yüzey → metin paletinden değil "sidebar üstü metin" amacına özel token'dan beslenmeli. `light.json`'a `sidebar_text` ve `sidebar_text_active` eklenip QSS bu token'a bağlanmalı.
- Önerilen renkler: `sidebar_text = #D9CBC2` (Shellstone — yumuşak), `sidebar_text_active = #F5F0E9` (Swan Wing — beyaz vurgu).
- Aynı problem koyu temada `sidebar_bg = #00032E` + `text_secondary = #D1A309` ikilisi için yok, ama tutarlılık için her iki temaya da token eklenmeli.

### 2. Koyu temada "Tamamlandı" badge'i KIRMIZI

**Belirti:** Süreç Aşamaları kartında tüm satırlardaki "Tamamlandı" rozeti kırmızı arka planlı. Beklenen: yeşil (`success`).

**Kök neden:** Badge QSS'i muhtemelen `badge-value` property'sini `danger`/`danger_alpha` token'ına eşliyor; ya da bu badge'e özel sabit kırmızı kalmış. Geçişten önce de bu durum vardı, palet değiştiği için **daha** dikkat çekiyor.

**Etki:** Tamamlanmış aşama → kırmızı alarm = ters semantik. Kullanıcı her aşamayı sorunlu sanır.

**Öneri:**
- `resources/styles/widgets/badges.qss` ve `stage_timeline.qss` içinde `[badge-value="Tamamlandı"]`, `[badge-value="DONE"]`, `[badge-value="ACCEPTED"]` seçicilerini `@success`/`@success_alpha`'ya bağla.
- Statü → token eşlemesi tek bir yerde toplanmalı (kod tarafında `_STATUS_THEME_KEYS` ile QSS tarafı arasında uyum tablosu).

### 3. Koyu temada aktif sidebar öğesi KIRMIZI

**Belirti:** "Ana Panel" / "Görevler" aktif olduğunda arka planı kırmızımsı parlıyor. Beklenen: Amber alpha (`@accent_alpha = #FFBF1C22`).

**Kök neden:** Önceki commit'te `sidebar.qss` içindeki `rgba(99,102,241,0.18)` literal'i `@accent_alpha`'ya çevrilmişti — ama burada bir başka katmanda hâlâ sabit renk kalmış olabilir. Ekrandaki ton net Amber alpha değil; QSS'te `SidebarNavButton:checked` veya `[selected="true"]` için ayrı bir kural sızıntı yapıyor.

**Öneri:** [components/sidebar.qss](resources/styles/components/sidebar.qss) içindeki `SidebarNavButton:checked` kuralı + `ProjectListItem[selected="true"]` (base'den gelen) sabit `#6366F1` aramasıyla tekrar taranmalı; tüm renk değerleri token üzerinden gelmeli.

---

## 🟠 P1 — Yüksek (Bilgi Hiyerarşisi)

### 4. Koyu temada metin hiyerarşisi tek katmana çöktü

**Belirti:** `text_primary = #FAF6E8` (sıcak beyaz), `text_secondary = #D1A309` (Goldenrod). İkincil metinler (stat sayıları, sidebar nav, liste item'ları, tab başlıkları, sütun başlıkları, badge metinleri) hepsi Goldenrod tonunda — ekran "altın bombardımanı" hissi veriyor.

**Etki:** Vurgu (accent) ile ikincil bilgi (secondary) aynı renk ailesi → kullanıcı hangisinin tıklanabilir, hangisinin sadece bilgi olduğunu ayırt edemiyor.

**Öneri:**
- `text_secondary` Goldenrod yerine **nötr soluk lavanta**: `#9CA0C8` (Federal Blue zemin üzerinde okunabilir + accent ile çelişmez).
- Goldenrod → `accent_secondary` adıyla ayrılıp yalnızca "altın vurgu istenen" yerlerde kullanılsın (rozet, sekme aktif çizgisi).
- KPI sayıları (`2`, `0`, `1`, `4`, `10`) **`text_primary`'ye taşınmalı** — şu an Goldenrod ve görsel olarak başlıktan zayıf. Sayı başlıktan **daha** vurgulu olmalı.

### 5. Koyu temada kart kenarlığı görünmez

**Belirti:** `border = #1A2080` ile `surface_raised = #1A2080` birebir aynı. Kartların kenarı kayboluyor; stat kartları, paneller, badge'ler havada yüzüyor gibi.

**Öneri:** `border` daha açık bir tonda olmalı, örn. `#2A3590` (scrollbar_handle ile aynı aile) veya alpha'lı gold: `#FFBF1C22`.

### 6. Süreç Aşamaları satırları yarım ekran kaplıyor

**Belirti:** "Fikir", "Analiz", "Tasarım"... 8 aşama × ~60px → süreç paneli proje detayının yarısını yutuyor. Her satırın sağında "Tamamlandı" tek bir rozet var, geri kalan boşluk israfı.

**Öneri:** Yatay timeline'a geçirmek veya satır yüksekliğini 32–36px'e düşürmek. Mevcut WBS UI'ı ile rekabet ediyor.

---

## 🟡 P2 — Orta (Cila)

### 7. Stat kart numarası okunaklı ama vurgusuz

**Belirti:** Stat kartında başlık (örn. "Toplam Görev") `text_primary` beyaz, **sayı** ise `text_secondary` Goldenrod ve aynı punto. Hiyerarşi tersine dönmüş — başlık sayıdan baskın.

**Öneri:** Sayı `text_primary`, +30% font ağırlığı/boyut; başlık `text_secondary` veya `text_muted`. Dashboard KPI'sının ana mesajı **değerdir**, etiketi değil.

### 8. Inline scroll handle Amber accent

**Belirti:** Liste paneli scroll bar handle'ı `@accent_start = Amber`. Sayfada çok sayıda yatay/dikey scroll var, hepsi parlak altın → görsel parazit.

**Öneri:** Scroll handle `text_muted` veya `border`'in açık tonu. Hover'da accent'e geçsin.

### 9. WBS sütun başlıkları sütun değeriyle aynı renk

**Belirti:** "Durum", "Öncelik", "Tip" başlıkları Goldenrod; altındaki `TODO`, `MEDIUM`, `TASK` değerleri de Goldenrod. Başlık ile veri görsel olarak ayrılmıyor.

**Öneri:** Başlık `text_primary` + uppercase 12px (section-header sınıfı zaten var), veri `text_secondary`.

### 10. Açık tema kart border'ları Shellstone — fazla pembe

**Belirti:** `border = #D9CBC2` Shellstone bej-pembe. Açık tema'nın geneline sıcak ton katıyor ama proje yönetim aracı için fazla "wellness app" hissi veriyor.

**Öneri (opsiyonel):** Border `#C8C2BA` (nötr taş) — Shellstone surface_raised için kalabilir.

---

## 🟢 P3 — Düşük (İyileştirme Fırsatı)

### 11. Aktif tab altın çizgi yerine doldurma

**Belirti:** "Özet" tab'i aktifken arka planı tamamen Gold (`@accent_start`). Sekme grubu bir bütünken aktif sekme ortam'dan kopuyor.

**Öneri:** Aktif tab arka planı `@surface_raised` + alt 2px Gold çizgi; metin `@accent_start`. Geçişler daha "browser tab" hissi verir.

### 12. Tema toggle anahtar konumu — kullanıcı testi gerekli

**Belirti:** Sidebar en altında "Koyu Tema" toggle + altında küçük versiyon numarası. Kullanıcı tema değiştirmek için sidebar'ın en altına bakmak zorunda.

**Öneri:** Ayarlar sayfasındaki yerine değil **erişilebilirlik öncelik** bırakılmalı; ama açık temada Royal Blue zemin üstünde "Açık Tema" yazısı yine kontrast sorunu (P0/1 ile birleşik).

### 13. Listede uzun başlıklar kesiliyor

**Belirti:** "[dneemee] iilginç bir kullanımı var (TODO" — sağdan kesik, "(TODO" yarım kalıyor. Ana panel "Son Aktiviteler" listesi sığmıyor.

**Öneri:** Liste item'ı `word-wrap` veya `text-overflow: ellipsis` + tooltip.

---

## Eylem Önerisi (Öncelik Sırası)

| # | Aksiyon | Tahmini efor | Etki |
|---|---|---|---|
| P0-1 | `sidebar_text` + `sidebar_text_active` token ekle, QSS bağla, iki temaya değer | 30 dk | Açık tema kullanılabilir |
| P0-2 | "Tamamlandı"/"DONE" badge'lerini `success`'a bağla | 15 dk | Semantik onarım |
| P0-3 | Sidebar `:checked` kuralında sabit hex taraması, token'a çevir | 15 dk | Görsel tutarlılık |
| P1-4 | `text_secondary` koyu temada Goldenrod'dan nötr lavanta'ya | 5 dk + 2 ekran kontrol | Hiyerarşi geri gelir |
| P1-5 | `border` token'ı surface_raised'tan ayrıştır | 5 dk | Kart sınırları görünür |
| P1-6 | Stage satır yüksekliği 36px | dimensions.py | Yer kazanımı |
| P2-7 | Stat kart hiyerarşi swap | 10 dk | KPI vurgu |
| P2-8 | Scrollbar handle nötralleştir | 5 dk | Görsel parazit azalır |
| P2-9 | WBS sütun başlığı `section-header` sınıfı | 10 dk | Tablo okunaklı |
| P3-11/13 | Tab stili + text-ellipsis | 30 dk | Cila |

**Toplam P0+P1 efor:** ~80 dakika, kullanılabilirliği WCAG AA seviyesine çeker.
