import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

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

    // Geriye dönük uyumluluk takma adları
    property bool isEraser: activeTool === "eraser"
    property alias lines: root.items
    property alias currentLine: root.currentPoints

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

    Connections {
        target: themeBridge
        function onIsDarkChanged() {
            canvas.requestPaint()
        }
    }

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

        // ── 1. Üst Araç Çubuğu (Mod Seçimi, Şekiller & Temel Eylemler) ──
        Flickable {
            Layout.fillWidth: true
            implicitHeight: 32
            contentWidth: Math.max(width, row1Layout.implicitWidth)
            contentHeight: 32
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            RowLayout {
                id: row1Layout
                width: Math.max(parent.width, implicitWidth)
                height: 32
                spacing: Theme.spacing.xs

                // Mod Seçici: [Çizim] / [Akış Şeması]
                Rectangle {
                    color: themeBridge.isDark ? "#282830" : "#F3F4F6"
                    radius: 6
                    implicitHeight: 28
                    implicitWidth: modeRow.implicitWidth + 6

                    RowLayout {
                        id: modeRow
                        anchors.centerIn: parent
                        spacing: 2

                        AppButton {
                            text: "✏️ " + i18nBridge.tr("tab_tools_draw", "Çizim")
                            btnVariant: root.toolMode === "draw" ? "primary" : "ghost"
                            implicitHeight: 24
                            onClicked: {
                                root.toolMode = "draw"
                                if (root.activeTool.startsWith("flow_")) root.activeTool = "pen"
                            }
                        }

                        AppButton {
                            text: "🔷 " + i18nBridge.tr("tab_tools_flowchart", "Akış Şeması")
                            btnVariant: root.toolMode === "flowchart" ? "primary" : "ghost"
                            implicitHeight: 24
                            onClicked: {
                                root.toolMode = "flowchart"
                                root.activeTool = "flow_process"
                            }
                        }
                    }
                }

                Rectangle { width: 1; height: 18; color: themeBridge.color("border") }

                // ── Çizim Araçları Grubu ──
                RowLayout {
                    visible: root.toolMode === "draw"
                    spacing: Theme.spacing.xs

                    AppButton {
                        text: "✏️ " + i18nBridge.tr("tool_pen", "Kalem")
                        btnVariant: root.activeTool === "pen" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "pen"
                    }

                    AppButton {
                        text: "➖ " + i18nBridge.tr("tool_line", "Çizgi")
                        btnVariant: root.activeTool === "line" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "line"
                    }

                    AppButton {
                        text: "➔ " + i18nBridge.tr("tool_arrow", "Ok")
                        btnVariant: root.activeTool === "arrow" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "arrow"
                    }

                    AppButton {
                        text: "▭ " + i18nBridge.tr("tool_rect", "Kutu")
                        btnVariant: root.activeTool === "rect" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "rect"
                    }

                    AppButton {
                        text: "▢ " + i18nBridge.tr("tool_round_rect", "Oval")
                        btnVariant: root.activeTool === "round_rect" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "round_rect"
                    }

                    AppButton {
                        text: "◯ " + i18nBridge.tr("tool_circle", "Daire")
                        btnVariant: root.activeTool === "circle" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "circle"
                    }

                    AppButton {
                        text: "⌫ " + i18nBridge.tr("tool_eraser", "Silgi")
                        btnVariant: root.activeTool === "eraser" ? "warning" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "eraser"
                    }
                }

                // ── Akış Şeması Blokları Grubu ──
                RowLayout {
                    visible: root.toolMode === "flowchart"
                    spacing: Theme.spacing.xs

                    AppButton {
                        text: "🟢 " + i18nBridge.tr("flow_terminator", "Başla/Bitir")
                        btnVariant: root.activeTool === "flow_start" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "flow_start"
                    }

                    AppButton {
                        text: "🟦 " + i18nBridge.tr("flow_process", "İşlem")
                        btnVariant: root.activeTool === "flow_process" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "flow_process"
                    }

                    AppButton {
                        text: "🔶 " + i18nBridge.tr("flow_decision", "Karar")
                        btnVariant: root.activeTool === "flow_decision" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "flow_decision"
                    }

                    AppButton {
                        text: "▱ " + i18nBridge.tr("flow_io", "Girdi/Çıktı")
                        btnVariant: root.activeTool === "flow_io" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "flow_io"
                    }

                    AppButton {
                        text: "➔ " + i18nBridge.tr("flow_arrow", "Akış Oku")
                        btnVariant: root.activeTool === "arrow" ? "primary" : "secondary"
                        implicitHeight: 28
                        onClicked: root.activeTool = "arrow"
                    }

                    AppButton {
                        text: "📋 " + i18nBridge.tr("flow_template", "Hazır Şema")
                        btnVariant: "secondary"
                        implicitHeight: 28
                        onClicked: root.insertFlowchartTemplate()
                    }
                }

                Item { Layout.fillWidth: true }

                Rectangle { width: 1; height: 18; color: themeBridge.color("border") }

                // Geri Al / İleri Al
                AppButton {
                    text: "↩"
                    btnVariant: "secondary"
                    implicitWidth: 32
                    implicitHeight: 28
                    enabled: root.canUndo
                    opacity: root.canUndo ? 1.0 : 0.4
                    onClicked: root.undo()
                }

                AppButton {
                    text: "↪"
                    btnVariant: "secondary"
                    implicitWidth: 32
                    implicitHeight: 28
                    enabled: root.canRedo
                    opacity: root.canRedo ? 1.0 : 0.4
                    onClicked: root.redo()
                }

                // Temizle Butonu
                AppButton {
                    text: i18nBridge.tr("action_clear", "Temizle")
                    btnVariant: "secondary"
                    implicitHeight: 28
                    onClicked: root.clearCanvas()
                }
            }
        }

        // ── 2. Özellikler, Renkler & Görsel Çubuğu ────────────────────
        Flickable {
            Layout.fillWidth: true
            implicitHeight: 32
            contentWidth: Math.max(width, row2Layout.implicitWidth)
            contentHeight: 32
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            RowLayout {
                id: row2Layout
                width: Math.max(parent.width, implicitWidth)
                height: 32
                spacing: Theme.spacing.xs

                Text {
                    text: i18nBridge.tr("label_color", "Renk:")
                    font.pixelSize: 12
                    color: themeBridge.color("text_muted")
                }

                Repeater {
                    model: [
                        themeBridge.isDark ? "#FFFFFF" : "#1E1E22",
                        "#EF4444", // Kırmızı
                        "#3B82F6", // Mavi
                        "#10B981", // Yeşil
                        "#F59E0B", // Sarı
                        "#8B5CF6"  // Mor
                    ]

                    Rectangle {
                        width: 22
                        height: 22
                        radius: 11
                        color: modelData
                        border.color: root.activeTool !== "eraser" && root.currentColor === modelData ? Theme.accent(themeBridge.currentTheme) : "#40888888"
                        border.width: root.activeTool !== "eraser" && root.currentColor === modelData ? 2.5 : 1

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (root.activeTool === "eraser") {
                                    root.activeTool = root.toolMode === "flowchart" ? "flow_process" : "pen"
                                }
                                root.currentColor = modelData
                            }
                        }
                    }
                }

                Rectangle { width: 1; height: 18; color: themeBridge.color("border") }

                // Kalınlık Seçimi
                RowLayout {
                    spacing: 2

                    Repeater {
                        model: [
                            { label: "2px", val: 2 },
                            { label: "4px", val: 4 },
                            { label: "8px", val: 8 }
                        ]

                        AppButton {
                            text: modelData.label
                            btnVariant: root.currentLineWidth === modelData.val ? "primary" : "secondary"
                            implicitWidth: 34
                            implicitHeight: 28
                            onClicked: root.currentLineWidth = modelData.val
                        }
                    }
                }

                // Dolgu Seçimi
                AppButton {
                    text: root.fillEnabled ? "■ " + i18nBridge.tr("label_fill", "Dolgulu") : "□ " + i18nBridge.tr("label_outline", "İçi Boş")
                    btnVariant: root.fillEnabled ? "primary" : "secondary"
                    implicitHeight: 28
                    onClicked: root.fillEnabled = !root.fillEnabled
                }

                Rectangle { width: 1; height: 18; color: themeBridge.color("border") }

                // Görsel Ekle / Arka Planı Kaldır
                AppButton {
                    text: "🖼️ " + i18nBridge.tr("tool_image", "Görsel")
                    btnVariant: "secondary"
                    implicitHeight: 28
                    onClicked: root.pickImage()
                }

                AppButton {
                    text: "❌"
                    btnVariant: "danger"
                    implicitWidth: 28
                    implicitHeight: 28
                    visible: root.backgroundImage !== ""
                    onClicked: root.clearBackgroundImage()
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: root.getToolHelpText()
                    font.pixelSize: 11
                    color: themeBridge.color("text_muted")
                }
            }
        }

        // ── 3. Çizim Tuvali Alanı ─────────────────────────────────────
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
                    var bgColor = themeBridge.isDark ? "#1E1E22" : "#FFFFFF"
                    if (root.backgroundImage !== "") {
                        ctx.clearRect(0, 0, width, height)
                    } else {
                        ctx.fillStyle = bgColor
                        ctx.fillRect(0, 0, width, height)
                    }

                    // Önceden çizilmiş tüm şekiller ve çizgiler
                    for (var i = 0; i < root.items.length; i++) {
                        root.renderItem(ctx, root.items[i], bgColor)
                    }

                    // Çizim esnasındaki canlı önizleme
                    if (root.isDrawing) {
                        root.renderLivePreview(ctx, bgColor)
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: root.activeTool === "eraser" ? Qt.CrossCursor : Qt.CrossCursor

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
                        var idx = root.findItemAt(mouse.x, mouse.y)
                        if (idx >= 0) {
                            root.openTextEditor(idx)
                        }
                    }

                    onReleased: function(mouse) {
                        if (!root.isDrawing) return
                        root.isDrawing = false

                        var newItem = null
                        var bgColor = themeBridge.isDark ? "#1E1E22" : "#FFFFFF"
                        var col = root.activeTool === "eraser" ? bgColor : root.currentColor
                        var lw = root.activeTool === "eraser" ? 18 : root.currentLineWidth

                        if (root.activeTool === "pen" || root.activeTool === "eraser") {
                            if (root.currentPoints.length > 0) {
                                newItem = {
                                    type: root.activeTool,
                                    color: col,
                                    width: lw,
                                    points: root.currentPoints.slice()
                                }
                            }
                        } else if (root.activeTool === "line") {
                            var distL = Math.hypot(root.currentX - root.startX, root.currentY - root.startY)
                            if (distL >= 3) {
                                newItem = {
                                    type: "line",
                                    color: col,
                                    width: lw,
                                    x1: root.startX,
                                    y1: root.startY,
                                    x2: root.currentX,
                                    y2: root.currentY
                                }
                            }
                        } else if (root.activeTool === "arrow") {
                            var distA = Math.hypot(root.currentX - root.startX, root.currentY - root.startY)
                            if (distA >= 3) {
                                newItem = {
                                    type: "arrow",
                                    color: col,
                                    width: lw,
                                    x1: root.startX,
                                    y1: root.startY,
                                    x2: root.currentX,
                                    y2: root.currentY,
                                    label: ""
                                }
                            }
                        } else if (root.activeTool === "rect") {
                            var rw = Math.abs(root.currentX - root.startX)
                            var rh = Math.abs(root.currentY - root.startY)
                            if (rw >= 3 && rh >= 3) {
                                newItem = {
                                    type: "rect",
                                    color: col,
                                    width: lw,
                                    x: Math.min(root.startX, root.currentX),
                                    y: Math.min(root.startY, root.currentY),
                                    w: rw,
                                    h: rh,
                                    fill: root.fillEnabled ? root.getFillColor(col) : "",
                                    text: ""
                                }
                            }
                        } else if (root.activeTool === "round_rect") {
                            var rrw = Math.abs(root.currentX - root.startX)
                            var rrh = Math.abs(root.currentY - root.startY)
                            if (rrw >= 3 && rrh >= 3) {
                                newItem = {
                                    type: "round_rect",
                                    color: col,
                                    width: lw,
                                    r: 8,
                                    x: Math.min(root.startX, root.currentX),
                                    y: Math.min(root.startY, root.currentY),
                                    w: rrw,
                                    h: rrh,
                                    fill: root.fillEnabled ? root.getFillColor(col) : "",
                                    text: ""
                                }
                            }
                        } else if (root.activeTool === "circle") {
                            var crx = Math.abs(root.currentX - root.startX) / 2
                            var cry = Math.abs(root.currentY - root.startY) / 2
                            if (crx >= 2 && cry >= 2) {
                                newItem = {
                                    type: "circle",
                                    color: col,
                                    width: lw,
                                    cx: (root.startX + root.currentX) / 2,
                                    cy: (root.startY + root.currentY) / 2,
                                    rx: crx,
                                    ry: cry,
                                    fill: root.fillEnabled ? root.getFillColor(col) : "",
                                    text: ""
                                }
                            }
                        } else if (root.activeTool === "flow_start") {
                            var sw = Math.max(40, Math.abs(root.currentX - root.startX))
                            var sh = Math.max(26, Math.abs(root.currentY - root.startY))
                            newItem = {
                                type: "flow_start",
                                color: col,
                                width: lw,
                                x: Math.min(root.startX, root.currentX),
                                y: Math.min(root.startY, root.currentY),
                                w: sw,
                                h: sh,
                                fill: root.getFillColor(col),
                                text: "Başla"
                            }
                        } else if (root.activeTool === "flow_process") {
                            var pw = Math.max(50, Math.abs(root.currentX - root.startX))
                            var ph = Math.max(30, Math.abs(root.currentY - root.startY))
                            newItem = {
                                type: "flow_process",
                                color: col,
                                width: lw,
                                x: Math.min(root.startX, root.currentX),
                                y: Math.min(root.startY, root.currentY),
                                w: pw,
                                h: ph,
                                fill: root.getFillColor(col),
                                text: "İşlem"
                            }
                        } else if (root.activeTool === "flow_decision") {
                            var dw = Math.max(50, Math.abs(root.currentX - root.startX))
                            var dh = Math.max(36, Math.abs(root.currentY - root.startY))
                            newItem = {
                                type: "flow_decision",
                                color: col,
                                width: lw,
                                x: Math.min(root.startX, root.currentX),
                                y: Math.min(root.startY, root.currentY),
                                w: dw,
                                h: dh,
                                fill: root.getFillColor(col),
                                text: "Koşul ?"
                            }
                        } else if (root.activeTool === "flow_io") {
                            var iow = Math.max(50, Math.abs(root.currentX - root.startX))
                            var ioh = Math.max(30, Math.abs(root.currentY - root.startY))
                            newItem = {
                                type: "flow_io",
                                color: col,
                                width: lw,
                                x: Math.min(root.startX, root.currentX),
                                y: Math.min(root.startY, root.currentY),
                                w: iow,
                                h: ioh,
                                fill: root.getFillColor(col),
                                text: "Girdi / Çıktı"
                            }
                        }

                        if (newItem) {
                            root.pushSnapshot()
                            root.items.push(newItem)
                            root.undoCount = root.undoStack.length
                            if (newItem.type.startsWith("flow_")) {
                                root.openTextEditor(root.items.length - 1)
                            }
                        }

                        root.currentPoints = []
                        canvas.requestPaint()
                    }
                }
            }

            // ── 4. Metin Düzenleme Arka Plan Karartması & Modalı ───────
            Rectangle {
                id: modalBackdrop
                anchors.fill: parent
                color: "#40000000"
                visible: root.editingItemIndex >= 0
                z: 99

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.applyBlockText(blockTextInput.text)
                }
            }

            Rectangle {
                id: textEditModal
                visible: root.editingItemIndex >= 0
                anchors.centerIn: parent
                width: Math.min(360, parent.width - 32)
                height: 146
                radius: Theme.radius.medium
                color: themeBridge.isDark ? "#24242A" : "#FFFFFF"
                border.color: Theme.accent(themeBridge.currentTheme)
                border.width: 1.5
                z: 100

                MouseArea {
                    anchors.fill: parent
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacing.md
                    spacing: Theme.spacing.sm

                    Text {
                        id: modalTitleText
                        text: i18nBridge.tr("title_edit_block_text", "Blok Metnini Düzenle")
                        font.pixelSize: Theme.typography.sizeBody
                        font.weight: Font.Medium
                        color: themeBridge.color("text_primary")
                    }

                    AppTextInput {
                        id: blockTextInput
                        Layout.fillWidth: true
                        placeholder: i18nBridge.tr("placeholder_block_text", "Metin girin...")
                        showVoiceInput: true
                        onAccepted: root.applyBlockText(blockTextInput.text)
                    }

                    RowLayout {
                        Layout.alignment: Qt.AlignRight
                        spacing: Theme.spacing.xs

                        AppButton {
                            text: i18nBridge.tr("action_cancel", "İptal")
                            btnVariant: "secondary"
                            implicitHeight: 28
                            onClicked: root.cancelTextEditor()
                        }

                        AppButton {
                            text: i18nBridge.tr("action_save", "Tamam")
                            btnVariant: "primary"
                            implicitHeight: 28
                            onClicked: root.applyBlockText(blockTextInput.text)
                        }
                    }
                }
            }
        }
    }

    // ── Çizim Yardımcı Fonksiyonları ──────────────────────────────────

    function renderItem(ctx, item, bgColor) {
        if (!item) return

        // 1. Serbest Çizgi veya Silgi (Points dizisi)
        if (item.points && (item.type === "pen" || item.type === "eraser" || !item.type)) {
            if (item.points.length === 1) {
                ctx.fillStyle = item.type === "eraser" ? bgColor : (item.color || root.currentColor)
                ctx.beginPath()
                ctx.arc(item.points[0].x, item.points[0].y, (item.width || 3) / 2, 0, 2 * Math.PI)
                ctx.fill()
            } else if (item.points.length > 1) {
                ctx.strokeStyle = item.type === "eraser" ? bgColor : (item.color || root.currentColor)
                ctx.lineWidth = item.width || 3
                ctx.lineCap = "round"
                ctx.lineJoin = "round"
                ctx.beginPath()
                ctx.moveTo(item.points[0].x, item.points[0].y)
                for (var j = 1; j < item.points.length; j++) {
                    ctx.lineTo(item.points[j].x, item.points[j].y)
                }
                ctx.stroke()
            }
            return
        }

        // 2. Düz Çizgi
        if (item.type === "line") {
            ctx.strokeStyle = item.color
            ctx.lineWidth = item.width || 3
            ctx.lineCap = "round"
            ctx.beginPath()
            ctx.moveTo(item.x1, item.y1)
            ctx.lineTo(item.x2, item.y2)
            ctx.stroke()
            return
        }

        // 3. Ok
        if (item.type === "arrow") {
            drawArrow(ctx, item.x1, item.y1, item.x2, item.y2, item.color, item.width || 3, item.label || "")
            return
        }

        // 4. Dikdörtgen
        if (item.type === "rect") {
            if (item.fill && item.fill !== "") {
                ctx.fillStyle = item.fill
                ctx.fillRect(item.x, item.y, item.w, item.h)
            }
            ctx.strokeStyle = item.color
            ctx.lineWidth = item.width || 3
            ctx.strokeRect(item.x, item.y, item.w, item.h)
            if (item.text) drawCenteredText(ctx, item.text, item.x + item.w / 2, item.y + item.h / 2, item.color)
            return
        }

        // 5. Oval / Yuvarlak Kutu
        if (item.type === "round_rect") {
            drawRoundRect(ctx, item.x, item.y, item.w, item.h, item.r || 8, item.color, item.width || 3, item.fill)
            if (item.text) drawCenteredText(ctx, item.text, item.x + item.w / 2, item.y + item.h / 2, item.color)
            return
        }

        // 6. Daire / Elips
        if (item.type === "circle") {
            drawEllipse(ctx, item.cx, item.cy, item.rx, item.ry, item.color, item.width || 3, item.fill)
            if (item.text) drawCenteredText(ctx, item.text, item.cx, item.cy, item.color)
            return
        }

        // 7. Akış Şeması: Başla / Bitir (Kapsül)
        if (item.type === "flow_start") {
            var r = Math.min(item.w, item.h) / 2
            drawRoundRect(ctx, item.x, item.y, item.w, item.h, r, item.color, item.width || 2, item.fill)
            drawCenteredText(ctx, item.text || "Başla", item.x + item.w / 2, item.y + item.h / 2, item.color)
            return
        }

        // 8. Akış Şeması: İşlem (Dikdörtgen)
        if (item.type === "flow_process") {
            if (item.fill && item.fill !== "") {
                ctx.fillStyle = item.fill
                ctx.fillRect(item.x, item.y, item.w, item.h)
            }
            ctx.strokeStyle = item.color
            ctx.lineWidth = item.width || 2
            ctx.strokeRect(item.x, item.y, item.w, item.h)
            drawCenteredText(ctx, item.text || "İşlem", item.x + item.w / 2, item.y + item.h / 2, item.color)
            return
        }

        // 9. Akış Şeması: Karar / Koşul (Baklava / Diamond)
        if (item.type === "flow_decision") {
            ctx.beginPath()
            ctx.moveTo(item.x + item.w / 2, item.y)
            ctx.lineTo(item.x + item.w, item.y + item.h / 2)
            ctx.lineTo(item.x + item.w / 2, item.y + item.h)
            ctx.lineTo(item.x, item.y + item.h / 2)
            ctx.closePath()
            if (item.fill && item.fill !== "") {
                ctx.fillStyle = item.fill
                ctx.fill()
            }
            ctx.strokeStyle = item.color
            ctx.lineWidth = item.width || 2
            ctx.stroke()
            drawCenteredText(ctx, item.text || "Koşul ?", item.x + item.w / 2, item.y + item.h / 2, item.color)
            return
        }

        // 10. Akış Şeması: Girdi / Çıktı (Paralelkenar)
        if (item.type === "flow_io") {
            var skew = Math.min(18, item.w * 0.18)
            ctx.beginPath()
            ctx.moveTo(item.x + skew, item.y)
            ctx.lineTo(item.x + item.w, item.y)
            ctx.lineTo(item.x + item.w - skew, item.y + item.h)
            ctx.lineTo(item.x, item.y + item.h)
            ctx.closePath()
            if (item.fill && item.fill !== "") {
                ctx.fillStyle = item.fill
                ctx.fill()
            }
            ctx.strokeStyle = item.color
            ctx.lineWidth = item.width || 2
            ctx.stroke()
            drawCenteredText(ctx, item.text || "Girdi/Çıktı", item.x + item.w / 2, item.y + item.h / 2, item.color)
            return
        }
    }

    function renderLivePreview(ctx, bgColor) {
        var col = root.activeTool === "eraser" ? bgColor : root.currentColor
        var lw = root.activeTool === "eraser" ? 18 : root.currentLineWidth

        if (root.activeTool === "pen" || root.activeTool === "eraser") {
            if (root.currentPoints.length > 1) {
                ctx.strokeStyle = col
                ctx.lineWidth = lw
                ctx.lineCap = "round"
                ctx.lineJoin = "round"
                ctx.beginPath()
                ctx.moveTo(root.currentPoints[0].x, root.currentPoints[0].y)
                for (var k = 1; k < root.currentPoints.length; k++) {
                    ctx.lineTo(root.currentPoints[k].x, root.currentPoints[k].y)
                }
                ctx.stroke()
            }
        } else if (root.activeTool === "line") {
            ctx.strokeStyle = col
            ctx.lineWidth = lw
            ctx.lineCap = "round"
            ctx.beginPath()
            ctx.moveTo(root.startX, root.startY)
            ctx.lineTo(root.currentX, root.currentY)
            ctx.stroke()
        } else if (root.activeTool === "arrow") {
            drawArrow(ctx, root.startX, root.startY, root.currentX, root.currentY, col, lw, "")
        } else if (root.activeTool === "rect") {
            var rx = Math.min(root.startX, root.currentX)
            var ry = Math.min(root.startY, root.currentY)
            var rw = Math.abs(root.currentX - root.startX)
            var rh = Math.abs(root.currentY - root.startY)
            if (root.fillEnabled) {
                ctx.fillStyle = root.getFillColor(col)
                ctx.fillRect(rx, ry, rw, rh)
            }
            ctx.strokeStyle = col
            ctx.lineWidth = lw
            ctx.strokeRect(rx, ry, rw, rh)
        } else if (root.activeTool === "round_rect") {
            var rrx = Math.min(root.startX, root.currentX)
            var rry = Math.min(root.startY, root.currentY)
            var rrw = Math.abs(root.currentX - root.startX)
            var rrh = Math.abs(root.currentY - root.startY)
            drawRoundRect(ctx, rrx, rry, rrw, rrh, 8, col, lw, root.fillEnabled ? root.getFillColor(col) : "")
        } else if (root.activeTool === "circle") {
            var crx = Math.abs(root.currentX - root.startX) / 2
            var cry = Math.abs(root.currentY - root.startY) / 2
            var ccx = (root.startX + root.currentX) / 2
            var ccy = (root.startY + root.currentY) / 2
            drawEllipse(ctx, ccx, ccy, crx, cry, col, lw, root.fillEnabled ? root.getFillColor(col) : "")
        } else if (root.activeTool === "flow_start") {
            var fsx = Math.min(root.startX, root.currentX)
            var fsy = Math.min(root.startY, root.currentY)
            var fsw = Math.max(40, Math.abs(root.currentX - root.startX))
            var fsh = Math.max(26, Math.abs(root.currentY - root.startY))
            var fsr = Math.min(fsw, fsh) / 2
            drawRoundRect(ctx, fsx, fsy, fsw, fsh, fsr, col, lw, root.getFillColor(col))
        } else if (root.activeTool === "flow_process") {
            var fpx = Math.min(root.startX, root.currentX)
            var fpy = Math.min(root.startY, root.currentY)
            var fpw = Math.max(50, Math.abs(root.currentX - root.startX))
            var fph = Math.max(30, Math.abs(root.currentY - root.startY))
            ctx.fillStyle = root.getFillColor(col)
            ctx.fillRect(fpx, fpy, fpw, fph)
            ctx.strokeStyle = col
            ctx.lineWidth = lw
            ctx.strokeRect(fpx, fpy, fpw, fph)
        } else if (root.activeTool === "flow_decision") {
            var fdx = Math.min(root.startX, root.currentX)
            var fdy = Math.min(root.startY, root.currentY)
            var fdw = Math.max(50, Math.abs(root.currentX - root.startX))
            var fdh = Math.max(36, Math.abs(root.currentY - root.startY))
            ctx.beginPath()
            ctx.moveTo(fdx + fdw / 2, fdy)
            ctx.lineTo(fdx + fdw, fdy + fdh / 2)
            ctx.lineTo(fdx + fdw / 2, fdy + fdh)
            ctx.lineTo(fdx, fdy + fdh / 2)
            ctx.closePath()
            ctx.fillStyle = root.getFillColor(col)
            ctx.fill()
            ctx.strokeStyle = col
            ctx.lineWidth = lw
            ctx.stroke()
        } else if (root.activeTool === "flow_io") {
            var fio_x = Math.min(root.startX, root.currentX)
            var fio_y = Math.min(root.startY, root.currentY)
            var fio_w = Math.max(50, Math.abs(root.currentX - root.startX))
            var fio_h = Math.max(30, Math.abs(root.currentY - root.startY))
            var fio_skew = Math.min(18, fio_w * 0.18)
            ctx.beginPath()
            ctx.moveTo(fio_x + fio_skew, fio_y)
            ctx.lineTo(fio_x + fio_w, fio_y)
            ctx.lineTo(fio_x + fio_w - fio_skew, fio_y + fio_h)
            ctx.lineTo(fio_x, fio_y + fio_h)
            ctx.closePath()
            ctx.fillStyle = root.getFillColor(col)
            ctx.fill()
            ctx.strokeStyle = col
            ctx.lineWidth = lw
            ctx.stroke()
        }
    }

    function drawArrow(ctx, x1, y1, x2, y2, color, width, label) {
        ctx.strokeStyle = color
        ctx.lineWidth = width
        ctx.lineCap = "round"
        ctx.lineJoin = "round"
        ctx.beginPath()
        ctx.moveTo(x1, y1)
        ctx.lineTo(x2, y2)
        ctx.stroke()

        var angle = Math.atan2(y2 - y1, x2 - x1)
        var headLen = Math.max(12, width * 3.5)
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.moveTo(x2, y2)
        ctx.lineTo(x2 - headLen * Math.cos(angle - Math.PI / 7), y2 - headLen * Math.sin(angle - Math.PI / 7))
        ctx.lineTo(x2 - headLen * Math.cos(angle + Math.PI / 7), y2 - headLen * Math.sin(angle + Math.PI / 7))
        ctx.closePath()
        ctx.fill()

        if (label && label.length > 0) {
            var mx = (x1 + x2) / 2
            var my = (y1 + y2) / 2
            ctx.save()
            ctx.font = "bold 11px sans-serif"
            ctx.fillStyle = color
            ctx.textAlign = "center"
            ctx.textBaseline = "bottom"
            ctx.fillText(label, mx, my - 4)
            ctx.restore()
        }
    }

    function drawRoundRect(ctx, x, y, w, h, r, color, width, fill) {
        if (w < 2 * r) r = w / 2
        if (h < 2 * r) r = h / 2
        ctx.beginPath()
        ctx.moveTo(x + r, y)
        ctx.arcTo(x + w, y, x + w, y + h, r)
        ctx.arcTo(x + w, y + h, x, y + h, r)
        ctx.arcTo(x, y + h, x, y, r)
        ctx.arcTo(x, y, x + w, y, r)
        ctx.closePath()
        if (fill && fill !== "") {
            ctx.fillStyle = fill
            ctx.fill()
        }
        ctx.strokeStyle = color
        ctx.lineWidth = width
        ctx.stroke()
    }

    function drawEllipse(ctx, cx, cy, rx, ry, color, width, fill) {
        if (rx <= 0.5 || ry <= 0.5) return
        ctx.save()
        ctx.beginPath()
        ctx.translate(cx, cy)
        ctx.scale(rx, ry)
        ctx.arc(0, 0, 1, 0, 2 * Math.PI, false)
        ctx.restore()
        if (fill && fill !== "") {
            ctx.fillStyle = fill
            ctx.fill()
        }
        ctx.strokeStyle = color
        ctx.lineWidth = width
        ctx.stroke()
    }

    function drawCenteredText(ctx, text, cx, cy, color) {
        if (!text || text.trim().length === 0) return
        ctx.save()
        ctx.font = "bold 12px sans-serif"
        ctx.fillStyle = color || (themeBridge.isDark ? "#FFFFFF" : "#1E1E22")
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"

        var lines = text.split("\n")
        var lineHeight = 15
        var totalH = lines.length * lineHeight
        var sy = cy - (totalH / 2) + (lineHeight / 2)

        for (var i = 0; i < lines.length; i++) {
            ctx.fillText(lines[i], cx, sy + (i * lineHeight))
        }
        ctx.restore()
    }

    function getFillColor(hexColor) {
        var c = Qt.color(hexColor || root.currentColor)
        return Qt.rgba(c.r, c.g, c.b, 0.18)
    }

    function getToolHelpText() {
        if (root.toolMode === "flowchart") {
            switch (root.activeTool) {
                case "flow_start": return i18nBridge.tr("hint_flow_start", "Başla/Bitir bloğu için sürükleyin (Çift tıkla düzenle)")
                case "flow_process": return i18nBridge.tr("hint_flow_process", "İşlem bloğu için sürükleyin (Çift tıkla düzenle)")
                case "flow_decision": return i18nBridge.tr("hint_flow_decision", "Karar/koşul bloğu için sürükleyin (Çift tıkla düzenle)")
                case "flow_io": return i18nBridge.tr("hint_flow_io", "Girdi/çıktı bloğu için sürükleyin (Çift tıkla düzenle)")
                case "arrow": return i18nBridge.tr("hint_flow_arrow", "Blokları bağlamak için akış oku çekin (Çift tıkla etiketle)")
                default: return ""
            }
        }

        switch (root.activeTool) {
            case "pen": return i18nBridge.tr("hint_tool_pen", "Serbest el çizim yapın")
            case "line": return i18nBridge.tr("hint_tool_line", "Düz çizgi için sürükleyip bırakın")
            case "arrow": return i18nBridge.tr("hint_tool_arrow", "Yönlü ok için sürükleyip bırakın")
            case "rect": return i18nBridge.tr("hint_tool_rect", "Kutu çizmek için sürükleyin")
            case "round_rect": return i18nBridge.tr("hint_tool_round_rect", "Oval kutu için sürükleyin")
            case "circle": return i18nBridge.tr("hint_tool_circle", "Daire/elips için sürükleyin")
            case "eraser": return i18nBridge.tr("hint_tool_eraser", "Silmek istediğiniz alanın üzerinden geçin")
            default: return ""
        }
    }

    function findItemAt(x, y) {
        for (var i = root.items.length - 1; i >= 0; i--) {
            var it = root.items[i]
            if (!it) continue
            if (it.type === "flow_start" || it.type === "flow_process" || it.type === "flow_decision" || it.type === "flow_io" || it.type === "rect" || it.type === "round_rect") {
                if (x >= it.x && x <= it.x + it.w && y >= it.y && y <= it.y + it.h) {
                    return i
                }
            } else if (it.type === "circle") {
                var dx = (x - it.cx) / (it.rx || 1)
                var dy = (y - it.cy) / (it.ry || 1)
                if (dx * dx + dy * dy <= 1) {
                    return i
                }
            } else if (it.type === "arrow" || it.type === "line") {
                var dist = distanceToSegment(x, y, it.x1, it.y1, it.x2, it.y2)
                if (dist <= 12) {
                    return i
                }
            }
        }
        return -1
    }

    function distanceToSegment(px, py, x1, y1, x2, y2) {
        var l2 = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
        if (l2 === 0) return Math.hypot(px - x1, py - y1)
        var t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2
        t = Math.max(0, Math.min(1, t))
        return Math.hypot(px - (x1 + t * (x2 - x1)), py - (y1 + t * (y2 - y1)))
    }

    // ── Metin Düzenleyici İşlemleri ────────────────────────────────────

    function openTextEditor(idx) {
        if (idx < 0 || idx >= root.items.length) return
        root.editingItemIndex = idx
        var it = root.items[idx]
        if (it.type === "arrow") {
            modalTitleText.text = i18nBridge.tr("title_edit_arrow_label", "Ok Etiketini Düzenle (örn: Evet / Hayır)")
            blockTextInput.text = it.label || ""
        } else {
            modalTitleText.text = i18nBridge.tr("title_edit_block_text", "Blok Metnini Düzenle")
            blockTextInput.text = it.text || ""
        }
    }

    function applyBlockText(newText) {
        if (root.editingItemIndex >= 0 && root.editingItemIndex < root.items.length) {
            root.pushSnapshot()
            var it = root.items[root.editingItemIndex]
            if (it.type === "arrow") {
                it.label = newText ? newText.trim() : ""
            } else {
                it.text = newText ? newText.trim() : ""
            }
            root.undoCount = root.undoStack.length
            canvas.requestPaint()
        }
        root.editingItemIndex = -1
    }

    function cancelTextEditor() {
        root.editingItemIndex = -1
    }

    // ── Hazır Akış Şeması Şablonu ──────────────────────────────────────

    function insertFlowchartTemplate() {
        root.pushSnapshot()
        var startCol = "#10B981"  // Yeşil
        var procCol = "#3B82F6"   // Mavi
        var decCol = "#F59E0B"    // Sarı / Turuncu
        var arrowCol = themeBridge.isDark ? "#A1A1AA" : "#4B5563"

        var templateItems = [
            // 1. Başla
            { type: "flow_start", x: 120, y: 30, w: 120, h: 44, color: startCol, width: 2, fill: root.getFillColor(startCol), text: "Başla" },
            // Ok
            { type: "arrow", x1: 180, y1: 74, x2: 180, y2: 110, color: arrowCol, width: 2, label: "" },
            // 2. Girdi
            { type: "flow_io", x: 100, y: 110, w: 160, h: 46, color: procCol, width: 2, fill: root.getFillColor(procCol), text: "Sayıyı Oku (N)" },
            // Ok
            { type: "arrow", x1: 180, y1: 156, x2: 180, y2: 195, color: arrowCol, width: 2, label: "" },
            // 3. Karar
            { type: "flow_decision", x: 100, y: 195, w: 160, h: 70, color: decCol, width: 2, fill: root.getFillColor(decCol), text: "N > 0 ?" },
            // Ok Sağa (Evet)
            { type: "arrow", x1: 260, y1: 230, x2: 340, y2: 230, color: arrowCol, width: 2, label: "Evet" },
            // 4. İşlem (Pozitif)
            { type: "flow_process", x: 340, y: 205, w: 150, h: 50, color: procCol, width: 2, fill: root.getFillColor(procCol), text: "'Pozitif' Yaz" },
            // Ok Aşağı (Hayır)
            { type: "arrow", x1: 180, y1: 265, x2: 180, y2: 310, color: arrowCol, width: 2, label: "Hayır" },
            // 5. İşlem (Negatif veya 0)
            { type: "flow_process", x: 95, y: 310, w: 170, h: 50, color: procCol, width: 2, fill: root.getFillColor(procCol), text: "'Negatif / 0' Yaz" },
            // Oklar Bitir'e
            { type: "arrow", x1: 180, y1: 360, x2: 180, y2: 400, color: arrowCol, width: 2, label: "" },
            { type: "arrow", x1: 415, y1: 255, x2: 415, y2: 422, color: arrowCol, width: 2, label: "" },
            { type: "arrow", x1: 415, y1: 422, x2: 240, y2: 422, color: arrowCol, width: 2, label: "" },
            // 6. Bitir
            { type: "flow_start", x: 120, y: 400, w: 120, h: 44, color: "#EF4444", width: 2, fill: root.getFillColor("#EF4444"), text: "Bitir" }
        ]

        for (var i = 0; i < templateItems.length; i++) {
            root.items.push(templateItems[i])
        }
        root.undoCount = root.undoStack.length
        canvas.requestPaint()
    }

    // ── Geri Al / İleri Al / Durum Yönetimi ─────────────────────────────

    // ── Resim / Arka Plan İşlemleri ────────────────────────────────────

    function pickImage() {
        if (memoViewModel) {
            var imgUrl = memoViewModel.pickAndSaveImage()
            if (imgUrl && imgUrl.length > 0) {
                root.setBackgroundImage(imgUrl)
            }
        }
    }

    function pasteImageFromClipboard() {
        if (memoViewModel && memoViewModel.hasClipboardImage()) {
            var imgUrl = memoViewModel.saveClipboardImage()
            if (imgUrl && imgUrl.length > 0) {
                root.setBackgroundImage(imgUrl)
            }
        }
    }

    function setBackgroundImage(url) {
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

    function pushSnapshot() {
        if (root.undoStack.length >= 40) {
            root.undoStack.shift()
        }
        root.undoStack.push(JSON.stringify({
            backgroundImage: root.backgroundImage,
            items: root.items
        }))
        root.redoStack = []
        root.undoCount = root.undoStack.length
        root.redoCount = 0
    }

    function undo() {
        if (root.undoStack.length === 0) return
        root.redoStack.push(JSON.stringify({
            backgroundImage: root.backgroundImage,
            items: root.items
        }))
        var prevRaw = root.undoStack.pop()
        var prev = JSON.parse(prevRaw)
        if (Array.isArray(prev)) {
            root.items = prev
            root.backgroundImage = ""
        } else if (prev) {
            root.items = prev.items || []
            root.backgroundImage = prev.backgroundImage || ""
        }
        root.undoCount = root.undoStack.length
        root.redoCount = root.redoStack.length
        canvas.requestPaint()
    }

    function redo() {
        if (root.redoStack.length === 0) return
        root.undoStack.push(JSON.stringify({
            backgroundImage: root.backgroundImage,
            items: root.items
        }))
        var nextRaw = root.redoStack.pop()
        var next = JSON.parse(nextRaw)
        if (Array.isArray(next)) {
            root.items = next
            root.backgroundImage = ""
        } else if (next) {
            root.items = next.items || []
            root.backgroundImage = next.backgroundImage || ""
        }
        root.undoCount = root.undoStack.length
        root.redoCount = root.redoStack.length
        canvas.requestPaint()
    }

    function clearCanvas() {
        if (root.items.length === 0 && root.backgroundImage === "") return
        root.pushSnapshot()
        root.items = []
        root.backgroundImage = ""
        root.currentPoints = []
        root.undoCount = root.undoStack.length
        root.redoCount = root.redoStack.length
        canvas.requestPaint()
    }

    function getDrawingJson() {
        if (root.backgroundImage !== "") {
            return JSON.stringify({
                version: 2,
                backgroundImage: root.backgroundImage,
                items: root.items
            })
        }
        return JSON.stringify(root.items)
    }

    function loadDrawingJson(jsonStr) {
        root.undoStack = []
        root.redoStack = []
        root.undoCount = 0
        root.redoCount = 0
        root.editingItemIndex = -1
        root.backgroundImage = ""

        if (!jsonStr || jsonStr.trim().length === 0) {
            root.items = []
        } else {
            try {
                var parsed = JSON.parse(jsonStr)
                if (Array.isArray(parsed)) {
                    // Eski veya yeni format dizi kontrolü
                    root.items = parsed.map(function(item) {
                        if (!item.type) {
                            return {
                                type: "pen",
                                color: item.color || (themeBridge.isDark ? "#FFFFFF" : "#1E1E22"),
                                width: item.width || 3,
                                points: item.points || []
                            }
                        }
                        return item
                    })
                } else if (parsed && parsed.items && Array.isArray(parsed.items)) {
                    root.backgroundImage = parsed.backgroundImage || ""
                    root.items = parsed.items
                } else {
                    root.items = []
                }
            } catch (e) {
                root.items = []
            }
        }
        root.currentPoints = []
        canvas.requestPaint()
    }
}
