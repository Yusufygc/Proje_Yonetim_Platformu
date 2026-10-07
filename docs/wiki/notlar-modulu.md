# Notlar ve Çizim Modülü

`presentation/viewmodels/memo_viewmodel.py` ve `presentation/qml/views/memo/` paketi:

Platform içerisindeki zengin not alma, serbest çizim, şekil ekleme ve algoritma akış şeması oluşturma mimarisini içerir.

## Bileşenler
- **`MemoViewModel`**: Notlar ve çizim verilerinin yönetimi, kaydedilmesi, sıralanması ve dışa/içe aktarımı. `insertImage(file_path)` metodu ile yerel sistemden resim seçilerek not içeriğine veya çizim tuvaline aktarılmasını sağlar.
- **`MemoEditor.qml`**: Markdown destekli metin düzenleyici, önizleme ve resim yerleştirme butonları.
- **`DrawingCanvas.qml`**: HTML5 Canvas tabanlı serbest el çizim, şekil araçları ve algoritma şeması motoru. Durumu (araç, renk, öğeler, geri al/yinele) tutar; dışa yalnızca `loadDrawingJson`/`getDrawingJson` sunar. Parçaları `views/memo/drawing/` altındadır:
  - `DrawingToolbar.qml`, `DrawingOptionsBar.qml`, `TextEditModal.qml`: durum tutmaz, seçimleri sinyalle bildirir.
  - `ShapeRenderer.js` (öğe ve canlı önizleme çizimi), `ShapeFactory.js` (sürüklemeden öğe üretimi), `HitTest.js` (çift tıklama isabeti), `FlowchartTemplate.js`, `DrawingSerializer.js`: `.pragma library` saf fonksiyonlardır; testleri `tests/test_drawing_logic.py` içindedir.

## Çizim ve Şema Yetenekleri
1. **Temel Çizim Araçları:**
   - Kalem, fosforlu kalem (vurgulayıcı), silgi, metin kutusu.
   - Çizgi, ok ve çift yönlü ok araçları.
2. **Geometrik Şekiller:**
   - Dikdörtgen, yuvarlak köşeli dikdörtgen, daire, elips.
   - Eşkenar dörtgen (baklava), yıldız ve üçgen.
3. **Algoritma ve Akış Şeması Blokları:**
   - **Başla / Bitir (Terminal):** Yuvarlatılmış hap şeklinde süreç başlangıç ve bitiş sembolü.
   - **İşlem (Process):** Standart hesaplama/eylem kutusu.
   - **Karar / Koşul (Decision):** Şartlı dallanma eşkenar dörtgeni.
   - **Girdi / Çıktı (Input/Output):** Veri okuma ve yazdırma paralelkenarı.
   - **Bağlayıcı (Connector):** Akış birleştirici dairesel sembol.
   - **Akış Okları:** Yönlendirme ve bağlantı okları.
4. **Resim Entegrasyonu:**
   - Dosya seçici (`FileDialog`) üzerinden PNG, JPG, BMP formatında resimler tuvale doğrudan eklenebilir ve taşınabilir.
5. **Araç Çubuğu ve UX:**
   - Çift sıralı `Flickable` düzeni sayesinde pencere daralsa bile araçlar taşmaz ve rahatça kaydırılabilir.
   - Metin girişi ve şekil özellikleri modal pencereleri pencere merkezinde tutulur, butonlar asla ekran dışına taşmaz.

İlgili: [[mimari-genel-bakis]], [[tema-sistemi]], [[gorevler-modulu]]
