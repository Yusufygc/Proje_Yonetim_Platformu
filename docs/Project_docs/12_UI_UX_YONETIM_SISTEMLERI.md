# 12. UI/UX ve Kaynak Yönetim Sistemleri

Bu doküman, uygulamanın arayüz kalitesini, sürdürülebilirliğini ve profesyonel görünümünü sağlamak için Faz 1 (Proje Temeli) kapsamında kurulacak merkezi yönetim mekanizmalarını detaylandırır. 

Uygulamanın ileride büyümesi, yeni temaların (örn. Dracula, Solarized) eklenmesi, farklı dillere çevrilmesi ve görsel bütünlüğünün korunması için bu altyapının baştan sağlam atılması kritik önem taşır.

---

## 1. Merkezi İkon Yönetim Mekanizması (IconManager)

PySide6'da ikonların temaya göre renk değiştirmesi en sık karşılaşılan zorluklardan biridir. Sabit PNG'ler yerine dinamik SVG'ler kullanılmalıdır.

**Gereksinimler ve Çözüm:**
* **Format:** Tüm ikonlar kesinlikle **SVG** formatında olmalıdır. SVG, XML tabanlı olduğu için kod içinden rengi (`fill` özelliği) değiştirilebilir.
* **İndirme ve Önbellekleme (Caching):** İstenen ikon lokal `resources/icons` klasöründe yoksa, uygulama Material Design Icons (veya belirlenen bir açık kaynak ikon seti) API'sinden SVG'yi anlık indirecek ve lokale kaydedecektir.
* **Dinamik Renklendirme:** İkonlar doğrudan kullanılmayacak, bir `IconManager.get_icon("icon_name", color=Theme.text_primary)` fonksiyonu üzerinden çağrılacaktır. Tema değiştiğinde ikonlar yeni renge göre anında tekrar boyanacaktır.

## 2. Tema ve Renk Yönetimi (ThemeManager)

Kullanıcının gözünü yormayan, okunaklı (kontrastı yüksek) ve genişletilebilir bir tema sistemi kurulacaktır.

**Gereksinimler ve Çözüm:**
* **Renk Paleti Sözlüğü:** Sadece "Dark" ve "Light" için değil, ileride "Ocean", "Forest" gibi temaların da eklenebilmesi için renkler kodun içine hardcode edilmeyecek, bir JSON veya Python Dictionary yapısında tutulacaktır.
* **Yüksek Kontrast (Okunabilirlik Kuralı):** Yazı renkleri asla soluk (çok düşük opacity veya arkaplana çok yakın gri) olmayacaktır. 
    * Örn. Dark modda arkaplan `#1E1E1E` ise, ana metinler kesinlikle `#F5F5F5` veya `#FFFFFF` (yüksek kontrast), ikincil metinler ise okunaklı bir `#BDBDBD` olacaktır.
* **Değişim Tetikleyicisi (Signal):** Tema değiştirildiğinde sistem `theme_changed` sinyali yayacak. Açık olan tüm pencereler, ikonlar ve grafikler bu sinyali dinleyip kendilerini yeni QSS (Qt Style Sheet) veya palet değerleriyle güncelleyecektir.

## 3. Tipografi ve Font Yönetimi (FontManager)

İşletim sisteminin varsayılan fontları (Windows'ta Segoe UI, Linux'ta Ubuntu font vb.) her zaman aynı profesyonel hissi vermeyebilir.

**Gereksinimler ve Çözüm:**
* **Gömülü (Embedded) Fontlar:** Projeye uygun, modern ve temiz bir font ailesi (örneğin **Inter**, **Roboto** veya **Poppins**) indirilecek ve uygulamanın `resources/fonts/` dizininde saklanacaktır.
* **QFontDatabase Entegrasyonu:** Uygulama başlarken işletim sistemine kurulmasına gerek kalmadan `QFontDatabase` ile bu lokal fontlar hafızaya (memory) yüklenecek ve uygulamanın ana fontu olarak atanacaktır.
* **Hiyerarşik Stil:** Başlıklar (H1, H2), Görev metinleri (Body) ve küçük notlar (Caption) için merkezi font boyutları ve font ağırlıkları (Bold, Regular, Medium) belirlenecektir.

## 4. Merkezi Metin Yönetimi (StringManager / i18n)

Uygulamanın ileride çoklu dil desteğine (İngilizce vb.) kolayca geçebilmesi ve metin güncellemelerinin tek bir yerden yapılabilmesi için metinler kodların içine gömülmeyecektir (hardcoded strings).

**Gereksinimler ve Çözüm:**
* **Konfigürasyon Dosyası:** Tüm metin ifadeleri, hata mesajları, buton isimleri ve diyalog uyarıları merkezi bir `strings.tr.json` (veya `.yaml`) dosyasından beslenecektir.
* **Kullanım:** Kod içerisinde bir butona isim verirken `button.setText("Kaydet")` yerine `button.setText(StringManager.get("btn_save"))` yapısı kullanılacaktır.
* **Avantajı:** İleride İngilizce desteği eklemek sadece bir `strings.en.json` dosyası oluşturmak kadar kolay olacaktır.

---

## 5. Mimari Birleşim (Örnek Katman Yapısı)

Bu sistemlerin PySide6'daki karşılığı şu şekilde klasörlenecektir:

```text
new_project_app/
  core/
    managers/
      icon_manager.py     # İkon indirme ve SVG renklendirme
      theme_manager.py    # Dark/Light paletleri, QSS üretimi
      font_manager.py     # QFontDatabase yüklemeleri
      string_manager.py   # JSON metin okuma
  resources/
    icons/
    fonts/
    themes/
    locales/            # strings.tr.json vb.