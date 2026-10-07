import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"
import "drawing"
import "drawing/ShapeRenderer.js" as Shapes
import "drawing/ShapeFactory.js" as Factory
import "drawing/HitTest.js" as HitTest
import "drawing/FlowchartTemplate.js" as Template
import "drawing/DrawingSerializer.js" as Serializer

Rectangle {
    id: root

    radius: Theme.radius.medium
    color: themeBridge.isDark ? "#1E1E22" : "#FFFFFF"
    border.color: themeBridge.color("border")
    border.width: 1
    clip: true

    // Araç modu: "draw" (Çizim) veya "flowchart" (Akış Şeması)
    property string toolMode: "draw"

    // Aktif Araç:
    // Çizim: "pen", "line", "arrow", "rect", "round_rect", "circle", "eraser"
    // Akış Şeması: "flow_start", "flow_process", "flow_decision", "flow_io", "arrow"
    property string activeTool: "pen"
    property string currentColor: themeBridge.isDark ? "#FFFFFF" : "#1E1E22"
    property int currentLineWidth: 3
    property bool fillEnabled: false

    // Çizilen tüm nesneler
    property var items: []
    property var currentPoints: []

    // Çizim esnası koordinatları
    property real startX: 0
    property real startY: 0
    property real currentX: 0
    property real currentY: 0
    property bool isDrawing: false

    // Geri Al / İleri Al Yığınları
    property var undoStack: []
    property var redoStack: []
    property int undoCount: 0
    property int redoCount: 0
    property bool canUndo: undoCount > 0
    property bool canRedo: redoCount > 0

    // Metin düzenleme durumu (-1: kapalı, >= 0: düzenlenen öğe indeksi)
    property int editingItemIndex: -1
    property string backgroundImage: ""

    // Zemin rengi tema ile değişir; tuval yeniden çizilmezse eski zeminle kalır.
    onColorChanged: canvas.requestPaint()

    // Klavye kısayolları
    Shortcut {
        sequences: [StandardKey.Undo]
        enabled: root.visible && root.canUndo && root.editingItemIndex < 0
        onActivated: root.undo()
    }

    Shortcut {
        sequences: [StandardKey.Redo]
        enabled: root.visible && root.canRedo && root.editingItemIndex < 0
        onActivated: root.redo()
    }

    Shortcut {
        sequences: [StandardKey.Paste]
        enabled: root.visible && root.editingItemIndex < 0
        onActivated: root.pasteImageFromClipboard()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.xs

        DrawingToolbar {
            toolMode: root.toolMode
            activeTool: root.activeTool
            canUndo: root.canUndo
            canRedo: root.canRedo
            onModeSelected: function(mode) { root.selectMode(mode) }
            onToolSelected: function(tool) { root.activeTool = tool }
            onTemplateRequested: root.insertFlowchartTemplate()
            onUndoRequested: root.undo()
            onRedoRequested: root.redo()
            onClearRequested: root.clearCanvas()
        }

        DrawingOptionsBar {
            toolMode: root.toolMode
            activeTool: root.activeTool
            currentColor: root.currentColor
            currentLineWidth: root.currentLineWidth
            fillEnabled: root.fillEnabled
            hasBackgroundImage: root.backgroundImage !== ""
            onColorSelected: function(color) { root.selectColor(color) }
            onLineWidthSelected: function(width) { root.currentLineWidth = width }
            onFillToggled: root.fillEnabled = !root.fillEnabled
            onImagePickRequested: root.pickImage()
            onImageClearRequested: root.clearBackgroundImage()
        }

        // ── Çizim Tuvali Alanı ─────────────────────────────────────────
        Item {
            id: canvasArea
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            Image {
                id: bgImage
                anchors.fill: parent
                anchors.margins: 4
                fillMode: Image.PreserveAspectFit
                source: root.backgroundImage
                visible: root.backgroundImage !== ""
                smooth: true
                asynchronous: true
            }

            Canvas {
                id: canvas
                anchors.fill: parent

                onPaint: {
                    var ctx = getContext("2d")
                    var palette = root.palette()
                    if (root.backgroundImage !== "") {
                        ctx.clearRect(0, 0, width, height)
                    } else {
                        ctx.fillStyle = palette.background
                        ctx.fillRect(0, 0, width, height)
                    }

                    // Önceden çizilmiş tüm şekiller ve çizgiler
                    for (var i = 0; i < root.items.length; i++) {
                        Shapes.renderItem(ctx, root.items[i], palette)
                    }

                    // Çizim esnasındaki canlı önizleme
                    if (root.isDrawing) {
                        Shapes.renderLivePreview(ctx, root.dragState(), palette)
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.CrossCursor

                    onPressed: function(mouse) {
                        if (root.editingItemIndex >= 0) {
                            root.cancelTextEditor()
                            return
                        }

                        root.isDrawing = true
                        root.startX = mouse.x
                        root.startY = mouse.y
                        root.currentX = mouse.x
                        root.currentY = mouse.y

                        if (root.activeTool === "pen" || root.activeTool === "eraser") {
                            root.currentPoints = [{ x: mouse.x, y: mouse.y }]
                        }
                        canvas.requestPaint()
                    }

                    onPositionChanged: function(mouse) {
                        if (root.isDrawing) {
                            root.currentX = mouse.x
                            root.currentY = mouse.y

                            if (root.activeTool === "pen" || root.activeTool === "eraser") {
                                root.currentPoints.push({ x: mouse.x, y: mouse.y })
                            }
                            canvas.requestPaint()
                        }
                    }

                    onDoubleClicked: function(mouse) {
                        var idx = HitTest.findItemAt(root.items, mouse.x, mouse.y)
                        if (idx >= 0) {
                            root.openTextEditor(idx)
                        }
                    }

                    onReleased: function(mouse) {
                        if (!root.isDrawing) return
                        root.isDrawing = false

                        var newItem = Factory.createItem(root.activeTool, root.dragState(), root.fillFor)
                        if (newItem) {
                            root.pushSnapshot()
                            root.items.push(newItem)
                            root.syncHistoryCounts()
                            if (newItem.type.startsWith("flow_")) {
                                root.openTextEditor(root.items.length - 1)
                            }
                        }

                        root.currentPoints = []
                        canvas.requestPaint()
                    }
                }
            }

            TextEditModal {
                id: textEditor
                active: root.editingItemIndex >= 0
                onApplied: function(text) { root.applyBlockText(text) }
                onCanceled: root.cancelTextEditor()
            }
        }
    }

    // ── Çizim Yardımcıları ────────────────────────────────────────────

    function bgColor() {
        return themeBridge.isDark ? "#1E1E22" : "#FFFFFF"
    }

    // Çizim fonksiyonlarına verilen tema renkleri.
    function palette() {
        return { background: bgColor(), pen: root.currentColor, text: themeBridge.isDark ? "#FFFFFF" : "#1E1E22" }
    }

    function fillFor(hexColor) {
        return Shapes.fillColor(hexColor, root.currentColor)
    }

    // Sürüklenen şeklin rengi, kalınlığı ve koordinatları; silgi zemin rengiyle ve kalın çizer.
    function dragState() {
        var eraser = root.activeTool === "eraser"
        return {
            tool: root.activeTool,
            color: eraser ? bgColor() : root.currentColor,
            lineWidth: eraser ? 18 : root.currentLineWidth,
            startX: root.startX,
            startY: root.startY,
            currentX: root.currentX,
            currentY: root.currentY,
            points: root.currentPoints,
            fillEnabled: root.fillEnabled
        }
    }

    function selectMode(mode) {
        root.toolMode = mode
        if (mode === "flowchart") {
            root.activeTool = "flow_process"
        } else if (root.activeTool.startsWith("flow_")) {
            root.activeTool = "pen"
        }
    }

    // Renk seçmek silgiden çıkarır; silgi seçiliyken rengin bir anlamı olmaz.
    function selectColor(color) {
        if (root.activeTool === "eraser") {
            root.activeTool = root.toolMode === "flowchart" ? "flow_process" : "pen"
        }
        root.currentColor = color
    }

    // ── Metin Düzenleyici İşlemleri ────────────────────────────────────

    function openTextEditor(idx) {
        if (idx < 0 || idx >= root.items.length) return
        root.editingItemIndex = idx
        var it = root.items[idx]
        var isArrow = it.type === "arrow"
        textEditor.open(
            isArrow ? i18nBridge.tr("title_edit_arrow_label", "Ok Etiketini Düzenle (örn: Evet / Hayır)")
                    : i18nBridge.tr("title_edit_block_text", "Blok Metnini Düzenle"),
            (isArrow ? it.label : it.text) || "")
    }

    // Oklarda düzenlenen alan etiket, bloklarda metindir.
    function applyBlockText(newText) {
        if (root.editingItemIndex >= 0 && root.editingItemIndex < root.items.length) {
            root.pushSnapshot()
            var it = root.items[root.editingItemIndex]
            it[it.type === "arrow" ? "label" : "text"] = newText ? newText.trim() : ""
            root.syncHistoryCounts()
            canvas.requestPaint()
        }
        root.editingItemIndex = -1
    }

    function cancelTextEditor() {
        root.editingItemIndex = -1
    }

    function insertFlowchartTemplate() {
        root.pushSnapshot()
        var templateItems = Template.createItems(themeBridge.isDark, root.fillFor)
        for (var i = 0; i < templateItems.length; i++) {
            root.items.push(templateItems[i])
        }
        root.syncHistoryCounts()
        canvas.requestPaint()
    }

    // ── Resim / Arka Plan İşlemleri ────────────────────────────────────

    function pickImage() {
        if (memoViewModel) root.setBackgroundImage(memoViewModel.pickAndSaveImage())
    }

    function pasteImageFromClipboard() {
        if (memoViewModel && memoViewModel.hasClipboardImage()) root.setBackgroundImage(memoViewModel.saveClipboardImage())
    }

    function setBackgroundImage(url) {
        if (!url || url.length === 0) return
        root.pushSnapshot()
        root.backgroundImage = url
        canvas.requestPaint()
    }

    function clearBackgroundImage() {
        root.pushSnapshot()
        root.backgroundImage = ""
        canvas.requestPaint()
    }

    // ── Geri Al / İleri Al / Durum Yönetimi ─────────────────────────────

    function snapshotJson() {
        return Serializer.snapshot(root.items, root.backgroundImage)
    }

    function restoreSnapshot(raw) {
        var drawing = Serializer.restoreSnapshot(raw)
        root.items = drawing.items
        root.backgroundImage = drawing.backgroundImage
        root.syncHistoryCounts()
        canvas.requestPaint()
    }

    function syncHistoryCounts() {
        root.undoCount = root.undoStack.length
        root.redoCount = root.redoStack.length
    }

    function pushSnapshot() {
        if (root.undoStack.length >= 40) {
            root.undoStack.shift()
        }
        root.undoStack.push(snapshotJson())
        root.redoStack = []
        root.syncHistoryCounts()
    }

    function undo() {
        if (root.undoStack.length === 0) return
        root.redoStack.push(snapshotJson())
        restoreSnapshot(root.undoStack.pop())
    }

    function redo() {
        if (root.redoStack.length === 0) return
        root.undoStack.push(snapshotJson())
        restoreSnapshot(root.redoStack.pop())
    }

    function clearCanvas() {
        if (root.items.length === 0 && root.backgroundImage === "") return
        root.pushSnapshot()
        root.items = []
        root.backgroundImage = ""
        root.currentPoints = []
        root.syncHistoryCounts()
        canvas.requestPaint()
    }

    function getDrawingJson() {
        return Serializer.serialize(root.items, root.backgroundImage)
    }

    function loadDrawingJson(jsonStr) {
        root.undoStack = []
        root.redoStack = []
        root.syncHistoryCounts()
        root.editingItemIndex = -1

        var drawing = Serializer.parse(jsonStr, themeBridge.isDark ? "#FFFFFF" : "#1E1E22")
        root.items = drawing.items
        root.backgroundImage = drawing.backgroundImage
        root.currentPoints = []
        canvas.requestPaint()
    }
}
