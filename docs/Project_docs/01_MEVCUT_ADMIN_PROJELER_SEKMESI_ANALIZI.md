# Mevcut Admin Projeler Sekmesi Analizi

Bu analiz, mevcut uygulamadaki `portfolio_app/presentation/admin/pages/projects_page.py`, `ProjectController`, `ProjectService`, `ProjectRepository`, `TaskRepository`, `Project`, `Task`, `ProjectStatus` ve `TaskType` yapılarından çıkarılmıştır.

## Mevcut Mantığın Özeti

Admin tarafındaki projeler sayfası şu temel modeli kullanıyor:

- Sol tarafta proje listesi.
- Sağ tarafta seçili projenin detay alanı.
- Proje oluşturma, düzenleme ve silme.
- Projeye bağlı görev/fikir/tasarım kartları.
- Her task kartının içinde küçük bir todo listesi.
- Task açıklamasının JSON formatında todo listesi olarak saklanması.
- Proje durumları: `Devam Ediyor`, `Tamamlandı`, `Beklemede`, `İptal`.
- Task türleri: `Görev`, `Fikir`, `Tasarım`.
- Task durumları: `Bekliyor`, `Devam Ediyor`, `Tamamlandı`.

Bu yapı, tek kişinin portfolyo projelerini yönetmesi için yeterli ve pratik. Yeni ürün için en değerli fikir, "proje ana kayıt, altına türlendirilmiş çalışma öğeleri bağlama" modelidir.

## Güçlü Taraflar

Mevcut sayfadan korunması gereken fikirler:

- Sol liste + sağ detay düzeni hızlı seçim ve bağlam değiştirme sağlıyor.
- Proje ile ilişkili tüm kayıtların aynı detay ekranında görünmesi iyi bir odak yaratıyor.
- Görev, fikir ve tasarımın aynı task altyapısı içinde tür alanıyla ayrılması basit ve anlaşılır.
- Todo listesinin task içinde hızlı düzenlenmesi kullanıcıyı ayrı sayfaya göndermiyor.
- Controller -> Service -> Repository ayrımı bağımsız ürün için de iyi bir mimari temel.
- SQLite tabanlı yerel depolama, kişisel proje takip uygulaması için hızlı başlangıç sağlar.
- Enum tabanlı durumlar, UI renkleri ve filtreler için net bir kaynak oluşturuyor.

## Sınırlılıklar

Yeni ürün bu sınırlılıkları aşmalı:

- Task açıklamasında todo JSON saklamak kısa vadede pratik ama uzun vadede sorgulanabilirlik zayıf.
- Fikir, tasarım ve görev aynı yapıda tutulduğu için her türün özel alanları yok.
- Proje süreci aşama bazlı izlenmiyor; sadece proje genel durumu var.
- Zaman çizelgesi, karar geçmişi, risk, kaynak, çıktı ve kilometre taşı takibi yok.
- Proje içi arama, etiket filtreleme, durum filtreleme ve görünüm seçenekleri sınırlı.
- Dashboard yalnızca sayısal özet veriyor; proje sağlığı veya süreç akışı göstermiyor.
- Görseller var fakat doküman, link, toplantı notu, karar kaydı gibi proje bilgileri için ayrı model yok.
- Tek kullanıcı varsayımı var; ileride ekip kullanımı istenirse sorumlular, roller ve yorumlar gerekir.

## Yeni Ürüne Taşınacak Kavramlar

Mevcut sayfadan yeni ürüne doğrudan taşınabilecek kavramlar:

- `Project`: Ana çalışma alanı.
- `ProjectStatus`: Projenin genel yaşam durumu.
- `Task`: Yapılabilir iş öğesi.
- `TaskType`: İş öğesinin doğasını belirtme.
- `TaskStatus`: İş öğesinin ilerleme durumu.
- `ProjectTag`: Sınıflandırma ve filtreleme.
- `ProjectImage`: Kanıt, ekran görüntüsü, tasarım veya çıktı görseli.
- `display_order`: Manuel sıralama.

Yeni üründe bunlar genişletilmeli:

- `Task` sadece görev olarak kalmalı; fikir ve tasarım ayrı varlıklar olabilir.
- Todo listesi ayrı `ChecklistItem` modeli olarak tutulmalı.
- Proje aşamaları `ProjectStage` veya `WorkflowStage` olarak modellenmeli.
- Kararlar `DecisionRecord`, riskler `Risk`, kaynaklar `Resource`, notlar `Note` olarak ayrılmalı.
- Proje geçmişi için `ActivityLog` eklenmeli.

## Esinlenilecek UI Deseni

Yeni projede korunacak ana ekran fikri:

- Sol panel: Projeler, filtreler, hızlı arama.
- Orta/ana panel: Seçili projeye ait özet ve aktif çalışma.
- Sağ panel veya sekmeler: Detay, süreç, görevler, fikirler, kararlar, kaynaklar.

Mevcut sayfadaki "accordion task kartı" fikri daha güçlü hale getirilebilir:

- Görev kartı açıldığında açıklama, checklist, yorum/not, bağlı fikir/karar ve tarih bilgisi görünebilir.
- Fikir kartı açıldığında problem, çözüm, fayda, efor, öncelik ve dönüştürme aksiyonu olabilir.
- Tasarım kartı açıldığında ekran, karar gerekçesi, görsel, kabul notları ve revizyon geçmişi olabilir.

## Temel Tasarım Sonucu

Yeni ürünün çekirdeği şu olmalı:

> Her proje, bir "çalışma merkezi"dir. Bu merkezde işler, fikirler, süreç adımları, kararlar, notlar, kaynaklar ve çıktılar birlikte yönetilir. Kullanıcı, proje durumunu hem liste seviyesinde hem de seçili proje detayında hızlıca anlayabilmelidir.

