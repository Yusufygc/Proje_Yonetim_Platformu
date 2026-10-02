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

    property string currentColor: themeBridge.isDark ? "#FFFFFF" : "#1E1E22"
    property int currentLineWidth: 3
    property bool isEraser: false
    property var lines: []
    property var currentLine: []

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.xs

        // Çizim Araç Çubuğu
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            // Renk Seçiciler
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
                    border.color: !root.isEraser && root.currentColor === modelData ? Theme.accent(themeBridge.currentTheme) : "#40888888"
                    border.width: !root.isEraser && root.currentColor === modelData ? 2.5 : 1

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            root.isEraser = false
                            root.currentColor = modelData
                        }
                    }
                }
            }

            Rectangle { width: 1; height: 18; color: themeBridge.color("border") }

            // Kalem / Silgi Geçişi
            AppButton {
                text: root.isEraser ? i18nBridge.tr("tool_eraser", "Silgi") : i18nBridge.tr("tool_pen", "Kalem")
                btnVariant: root.isEraser ? "warning" : "secondary"
                implicitHeight: 26
                onClicked: {
                    root.isEraser = !root.isEraser
                }
            }

            // Temizle Butonu
            AppButton {
                text: i18nBridge.tr("action_clear", "Temizle")
                btnVariant: "secondary"
                implicitHeight: 26
                onClicked: root.clearCanvas()
            }

            Item { Layout.fillWidth: true }
        }

        // Çizim Alanı
        Canvas {
            id: canvas
            Layout.fillWidth: true
            Layout.fillHeight: true

            onPaint: {
                var ctx = getContext("2d")
                ctx.fillStyle = themeBridge.isDark ? "#1E1E22" : "#FFFFFF"
                ctx.fillRect(0, 0, width, height)

                // Önceden çizilen çizgiler
                for (var i = 0; i < root.lines.length; i++) {
                    var l = root.lines[i]
                    if (l.points && l.points.length > 1) {
                        ctx.strokeStyle = l.color
                        ctx.lineWidth = l.width
                        ctx.lineCap = "round"
                        ctx.lineJoin = "round"
                        ctx.beginPath()
                        ctx.moveTo(l.points[0].x, l.points[0].y)
                        for (var j = 1; j < l.points.length; j++) {
                            ctx.lineTo(l.points[j].x, l.points[j].y)
                        }
                        ctx.stroke()
                    }
                }

                // Şu an çizilmekte olan çizgi
                if (root.currentLine.length > 1) {
                    ctx.strokeStyle = root.isEraser ? (themeBridge.isDark ? "#1E1E22" : "#FFFFFF") : root.currentColor
                    ctx.lineWidth = root.isEraser ? 16 : root.currentLineWidth
                    ctx.lineCap = "round"
                    ctx.lineJoin = "round"
                    ctx.beginPath()
                    ctx.moveTo(root.currentLine[0].x, root.currentLine[0].y)
                    for (var k = 1; k < root.currentLine.length; k++) {
                        ctx.lineTo(root.currentLine[k].x, root.currentLine[k].y)
                    }
                    ctx.stroke()
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: root.isEraser ? Qt.CrossCursor : Qt.ArrowCursor

                onPressed: function(mouse) {
                    root.currentLine = [{ x: mouse.x, y: mouse.y }]
                    canvas.requestPaint()
                }

                onPositionChanged: function(mouse) {
                    if (pressed) {
                        root.currentLine.push({ x: mouse.x, y: mouse.y })
                        canvas.requestPaint()
                    }
                }

                onReleased: {
                    if (root.currentLine.length > 0) {
                        var col = root.isEraser ? (themeBridge.isDark ? "#1E1E22" : "#FFFFFF") : root.currentColor
                        var w = root.isEraser ? 16 : root.currentLineWidth
                        root.lines.push({ color: col, width: w, points: root.currentLine.slice() })
                        root.currentLine = []
                        canvas.requestPaint()
                    }
                }
            }
        }
    }

    function clearCanvas() {
        root.lines = []
        root.currentLine = []
        canvas.requestPaint()
    }

    function getDrawingJson() {
        return JSON.stringify(root.lines)
    }

    function loadDrawingJson(jsonStr) {
        if (!jsonStr || jsonStr.trim().length === 0) {
            root.lines = []
        } else {
            try {
                root.lines = JSON.parse(jsonStr)
            } catch (e) {
                root.lines = []
            }
        }
        root.currentLine = []
        canvas.requestPaint()
    }
}
