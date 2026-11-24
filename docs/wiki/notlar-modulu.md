# Notlar ve Çizim Modülü

`presentation/viewmodels/memo_viewmodel.py` ve `presentation/qml/views/memo/` paketi:

Platform içerisindeki otomatik kaydedilen zengin Markdown not alma, serbest çizim ve geometrik şekil ekleme mimarisini içerir.

## Bileşenler
- **`MemoViewModel`**: Notlar ve çizim verilerinin yönetimi, kaydedilmesi (`saveMemo`), sessiz otomatik kayıt (`autoSaveMemo`), sıralanması ve görsel ekleme işlemleri (`pickAndSaveImage`, `saveClipboardImage`).
- **`MemoEditor.qml`**: Markdown destekli metin düzenleyici, önizleme, resim yerleştirme ve 800 ms debounce'lu otomatik kayıt (`autoSaveTimer`) + sayfa/not değişiminde bekleyen değişiklikleri diske yazma (`flushPendingAutoSave`).
- **`DrawingCanvas.qml`**: HTML5 Canvas tabanlı serbest el çizim ve şekil araçları motoru. Durumu (araç, renk, öğeler, geri al/yinele) tutar; dışa `loadDrawingJson`/`getDrawingJson` ve değişikliklerde `drawingModified` sinyali sunar. Parçaları `views/memo/drawing/` altındadır:
  - `DrawingToolbar.qml`, `DrawingOptionsBar.qml`, `TextEditModal.qml`: durum tutmaz, seçimleri sinyalle bildirir.
  - `ShapeRenderer.js` (öğe ve canlı önizleme çizimi), `ShapeFactory.js` (sürüklemeden öğe üretimi), `HitTest.js` (çift tıklama isabeti), `DrawingSerializer.js`: `.pragma library` saf fonksiyonlardır; testleri `tests/test_drawing_logic.py` içindedir.

## Çizim Yetenekleri
1. **Temel Çizim Araçları:**
   - Kalem, düz çizgi, yönlü ok ve silgi.
2. **Geometrik Şekiller:**
   - Dikdörtgen (kutu), yuvarlak köşeli dikdörtgen (oval) ve daire/elips; çift tıklama ile şekil içi metin/ok etiketi düzenleme.
3. **Resim Entegrasyonu:**
   - Dosya seçici (`FileDialog`) veya pano (Ctrl+V) üzerinden PNG, JPG, BMP formatında resimler nota veya tuvale arka plan olarak eklenebilir.
4. **Araç Çubuğu ve UX:**
   - Çift sıralı `Flickable` düzeni sayesinde pencere daralsa bile araçlar taşmaz ve rahatça kaydırılabilir.
   - Metin düzenleme modalı (`TextEditModal.qml`) pencere merkezinde tutulur; Enter ile onaylanır, Esc ile iptal edilir.

İlgili: [[mimari-genel-bakis]], [[tema-sistemi]], [[gorevler-modulu]]
