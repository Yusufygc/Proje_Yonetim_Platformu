# 11. Hiyerarşik Görev Yönetimi (İş Kırılım Yapısı - WBS)

## İhtiyaç ve Tanım
Projelerde sadece düz bir görev listesi (flat list) kullanmak, detaylı projelerde organizasyonu zorlaştırır. Kullanıcının bir proje içerisinde modüller, alt modüller ve spesifik görevler şeklinde **başlıklandırma ve iç içe todo listesi** (hiyerarşi) oluşturabilmesi gerekir.

Yazılım ve proje yönetimi terminolojisinde bu profesyonel yaklaşıma **Work Breakdown Structure (WBS) - İş Kırılım Yapısı** denir.

## Örnek Hiyerarşi Senaryosu
Kullanıcının talep ettiği yapı şu şekildedir:
- 📁 **Desktop Uygulaması** (Proje)
  - 📂 **Ana Sayfa** (Modül / Ana Görev Grubu)
    - 📂 **1. Sekme** (Alt Modül / Alt Görev Grubu)
      - ⬜ Yazı boyutlarını artır (Görev)
      - ⬜ Padding ayarlarını yap (Görev)
    - 📂 **2. Sekme** (Alt Modül)
      - ⬜ Renk değiştir (Görev)
  - 📂 **Ayarlar Sayfası** (Modül)
    - ⬜ Tema seçeneği ekle (Görev)

## Veri Modeli Çözümü
Bu yapıyı kurmanın en esnek ve modern yolu, `tasks` (görevler) tablosuna **Self-Referencing (Kendi Kendine Referans Veren)** bir alan eklemektir. Ayrı ayrı "Klasör", "Alt Klasör" tabloları oluşturmak yerine, bir görevin başka bir görevin "çocuğu" (child) olabilmesine izin verilir.

### Güncellenmiş `tasks` Tablosu
- `id`: integer primary key
- `project_id`: integer (Projeye bağlantı)
- **`parent_task_id`: integer nullable** (Hiyerarşi için eklendi. Null ise bu bir ana başlıktır)
- `title`: text
- `type`: text (`GROUP`, `TASK`, `BUG` vb.)
- `status`: text
- `display_order`: integer (Aynı başlık altındaki sırayı tutmak için)
- ...diğer alanlar

*Profesyonel Dokunuş:* `type` alanı `GROUP` (veya Başlık/Modül) olan kayıtlar, bir işten ziyade alt görevleri gruplamak için kullanılır. En alt seviyedeki işler ise `TASK` veya `BUG` olur. Bir `TASK`'ın içinde de minik adımlar için `ChecklistItem` kullanılmaya devam edilebilir.

## UX ve UI Akışları (PySide6 Yansımaları)
1. **Ağaç Görünümü (Tree View):** Görevler sayfası artık düz bir liste değil, yanındaki ok (chevron) ile daraltılıp genişletilebilir (collapsible) bir ağaç yapısında tasarlanmalıdır. PySide6'daki `QTreeView` veya iç içe tasarlanmış `QFrame` widget'ları bu iş için idealdir.
2. **Sürükle-Bırak (Drag & Drop):** Kullanıcı bir görevi tutup (örneğin "Renk değiştir") başka bir başlığın altına sürükleyebilmelidir.
3. **Satır İçi Ekleme (Inline Add):** Bir başlığın yanındaki `[+]` ikonuna tıklandığında, anında o başlığın altına yeni bir boş satır açılıp hızlıca alt görev yazılabilmelidir.

## İş Kuralları (Business Rules)
- **Yukarı Doğru İlerleme Hesabı (Roll-up Progress):** Bir başlığın (örneğin 1. Sekme) tamamlanma yüzdesi, altındaki görevlerin bitme oranına göre otomatik hesaplanır. Projenin genel ilerlemesi de ağacın en üstündeki başlıkların ağırlığına göre hesaplanır.
- **Otomatik Durum Değişimi:** Bir başlığın altındaki tüm görevler `DONE` (Tamamlandı) durumuna geçerse, üst başlığın durumu da otomatik olarak `DONE` yapılır.
- **Silme Kuralı (Cascade Delete):** Bir üst başlık (örneğin "Ana Sayfa") silinirse, yazılım kullanıcıya "Altındaki 15 görev de silinecek, emin misiniz?" diye uyarı verir.
