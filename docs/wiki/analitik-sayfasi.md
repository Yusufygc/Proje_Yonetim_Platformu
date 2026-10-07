# Analitik ve Metrikler Sayfası

`AnalyticsView.qml` → `AnalyticsViewModel` → `AnalyticsController` (asenkron) → `AnalyticsService` + `analytics_overview`. Dönem (günlük/haftalık/aylık/yıllık) ve proje filtresi (sağ üstte, dönem düğmeleriyle aynı satırda) tüm kartları etkiler; ısı haritası ve durum halkası dönemden bağımsızdır, yalnızca proje filtresine uyar.

## Bölümler
| Bölüm | Kaynak | Not |
|---|---|---|
| KPI kartları (`KpiCard`) | `kpis` haritası | Tamamlanan, oran, seri, **ortalama süre**, en iyi dönem |
| Zaman içinde tamamlananlar (`TimeSeriesChart`) | `timeSeries` | Haftalık etiket `40.Hafta` |
| Açılan ve tamamlanan (`FlowChart`) | `flowSeries` | İki çizgi; "Net birikim" = açılan − biten. Çizgiler ayrışıyorsa iş birikiyor |
| Aktivite ısı haritası (`ActivityHeatmap`) | `heatmap` | Son 12 hafta, sütun = hafta, satır = pazartesi-pazar; kare koyuluğu = o gün biten görev; üstüne gelince tarih ve sayı |
| Görev durumları (`StatusDonut`) | `statusDistribution` | Altı durum, ortada toplam |
| Öncelik / Proje dağılımı | `priorityDistribution`, `projectDistribution` | Dönemde biten görevler |

## Kararlar
- **Ortalama süre** (oluşturulmadan tamamlanmaya, gün) eski "Zamanında %" kartının yerini aldı: görev diyaloğundan bitiş tarihi alanı kalktığı için o kart hep 0 gösteriyordu.
- Haftalık anahtar `strftime("%W")` (pazartesi başlangıçlı, ISO değil); yılın ilk günleri `0.Hafta` çıkabilir.
- Günler UTC'ye göre gruplanır (tüm grafiklerde aynı); gece yarısına yakın tamamlananlar yerel takvimde bir gün kayık görünebilir.
- Grafik veri renkleri (durum, öncelik) tema-bağımsız sabit renklerdir; çizgi/ısı/halka zemin ve çerçeveleri tema property'lerinden gelir ve `themeChanged` ile yeniden çizilir ([[tema-sistemi]]).
- `AnalyticsViewModel` KPI değerlerini tek `kpis` haritasında toplar (sınıf üye sınırı).

## Dosyalar
`services/analytics_service.py` (dönem serileri, KPI), `services/analytics_overview.py` (ısı haritası, durum, akış, ortalama süre), `presentation/qml/views/analytics/` (bileşenler). Testler: `tests/test_analytics_overview.py`.

İlgili: [[worker-altyapisi]], [[tema-sistemi]]
