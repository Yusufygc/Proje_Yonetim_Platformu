# 14. Premium UI/UX Tasarım ve Animasyon Planı

Bu doküman, uygulamanın geleneksel, sıkıcı ve donuk kurumsal masaüstü yazılımlarından (eski tip gri Qt ekranları) sıyrılarak; modern, premium, akıcı ve kullanıcıya "SaaS (Software as a Service)" veya "macOS native" kalitesinde hissettirecek tasarım standartlarını belirler.

---

## 1. Tasarım Dili ve Felsefesi

* **İlham Kaynakları:** Linear, Notion, Raycast ve modern macOS arayüzleri.
* **Ana Odak (Content-First):** UI elemanları (butonlar, paneller) kullanıcının gözüne batmamalı, içerik (projeler, görevler) ön planda olmalıdır.
* **Derinlik ve Katmanlar (Z-Index Hierarchy):** Arayüz düz bir kağıt gibi değil, üst üste binen katmanlar (arka plan, kartlar, dialoglar) şeklinde tasarlanacaktır.

---

## 2. Renk Paleti ve Gradyan Kullanımı

Standart düz renkler yerine uygulamanın kritik noktalarında derinlik katan renkler kullanılacaktır.

* **Zengin Arka Planlar (Rich Backgrounds):** Saf siyah (`#000000`) veya saf beyaz (`#FFFFFF`) yerine, göz yormayan derin tonlar kullanılacak.
    * *Dark Mode Önerisi:* Arka plan için Koyu Lacivert/Gri (`#12141A`), kartlar için bir tona açık (`#1C1F26`).
* **Vurgu Gradyanları (Accent Gradients):** Ana eylem butonları (Örn: "Yeni Proje" butonu) veya aktif sekme göstergeleri düz renk değil, hafif açılı gradyanlar olacaktır.
    * *Örnek CSS/QSS:* `qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #8B5CF6)` (İndigo'dan Mora pürüzsüz geçiş).
* **Cam Efekti (Glassmorphism İpuçları):** Sidebar veya üst bar gibi sabit alanlarda çok hafif saydamlık (`rgba`) kullanılarak modern bir dokunuş eklenecektir.

---

## 3. Gölgelendirme (Shadowing & Depth)

Eski nesil keskin ve koyu gölgeler yerine, modern arayüzlerdeki "soft ve dağınık" gölgelendirme teknikleri uygulanacaktır.

* **Soft Drop Shadows:** PySide6'daki `QGraphicsDropShadowEffect` kullanılarak kartlara, açılır menülere (dropdown) ve dialoglara derinlik katılacak.
* **Gölgelendirme Parametreleri (Premium His):**
    * *Kartlar (Task Cards):* Çok düşük blur, hafif dikey kayma. (Örn: `blurRadius=10`, `yOffset=2`, `color=rgba(0,0,0, 0.1)`)
    * *Dialog/Modal:* Yüksek blur, ekranın üstünde uçuyor hissi. (Örn: `blurRadius=40`, `yOffset=10`, `color=rgba(0,0,0, 0.25)`)
* **Hover Gölgeleri:** Bir proje kartının üzerine gelindiğinde (hover), gölgenin bulanıklık (blur) değeri ve Y eksenindeki kayması artarak kartın "kalktığı" hissi verilecektir.

---

## 4. Köşe Yumuşatma (Border Radius) ve Geometri

Keskin köşeler (`0px`) kurumsal, aşırı yuvarlak köşeler (`50px`) ise oyuncaklı hissettirir. Premium his, doğru orantıdadır.

* **Standart Radius Değerleri:**
    * **Ana Paneller & İçerik Alanları:** `border-radius: 12px;` veya `16px;`
    * **Görev Kartları ve Butonlar:** `border-radius: 8px;`
    * **Küçük Etiketler (Tags/Badges):** `border-radius: 6px;`
* **İç içe Yuvarlama Kuralı:** Bir dış panelin radius'u `16px` ise, içindeki butonun radius'u görsel boşluk (padding) çıkartılarak hesaplanmalı, köşeler birbiriyle estetik olarak uyumlu olmalıdır.

---

## 5. Animasyonlar ve Mikro-Etkileşimler (Hover Effects)

Arayüzdeki hiçbir değişim "anında" (0 milisaniye) olmamalıdır. Her durum değişimi akıcı olmalıdır.

* **Hover Geçişleri (Transitions):** Butonların üzerine gelindiğinde arka plan rengi anında değişmeyecek, QSS veya `QVariantAnimation` ile `200ms ease-in-out` süresinde yumuşakça değişecektir.
* **Büyüme/Küçülme (Scale Effects):** Tıklanabilir önemli öğelerin üzerine gelindiğinde, öğe %1 veya %2 oranında hafifçe büyüyecektir (PySide6 animasyonları ile scale up).
* **Açılış/Kapanış Animasyonları (Layout Animations):**
    * Sidebar daraltılırken/genişletilirken genişlik değeri (width) bir `QPropertyAnimation` ile `300ms` içinde kayarak değişecektir.
    * Ağaç yapısındaki (WBS) görevler açılırken "pat" diye belirmek yerine, opasiteleri (opacity) 0'dan 1'e doğru `150ms` içinde artarak belirecektir.

---

## 6. PySide6 İçin Teknik İmplementasyon Haritası

Bu modern tasarımı PySide6'da hayata geçirmek için kullanılacak araçlar:

1.  **QSS (Qt Style Sheets):** `border-radius`, `background: qlineargradient(...)`, ve padding ayarları için gelişmiş stylesheet'ler yazılacak.
2.  **QGraphicsDropShadowEffect:** Butonlara ve çerçevelere (QFrame) gölge vermek için donanım hızlandırmalı bu sınıf kullanılacak.
3.  **QPropertyAnimation:** Menü genişlemeleri, renk solmaları ve pozisyon kaydırmaları (slide in/out) için kullanılacak. Kurumsal hantallığı kıran en önemli sınıf bu olacaktır.
4.  **QSvgWidget / IconManager:** Önceki planda belirlenen SVG ikonların renkleri animasyonlu olarak değişecek.
