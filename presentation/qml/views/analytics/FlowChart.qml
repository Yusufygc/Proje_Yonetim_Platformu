import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../../components"

// Dönem başına açılan ve tamamlanan görevler; çizgiler birbirinden uzaklaşıyorsa iş birikiyordur.
AppCard {
    id: root
    height: 270

    readonly property var series: analyticsViewModel.flowSeries
    readonly property color createdColor: themeBridge.accentStart
    readonly property color completedColor: themeBridge.success
    readonly property int maxValue: {
        var m = 1
        for (var i = 0; i < series.length; i++) {
            m = Math.max(m, series[i].created, series[i].completed)
        }
        return m
    }
    // Dönem boyunca açılan eksi biten: pozitifse açık iş artmıştır.
    readonly property int netOpen: {
        var net = 0
        for (var i = 0; i < series.length; i++) {
            net += series[i].created - series[i].completed
        }
        return net
    }
    readonly property bool hasData: maxValue > 1 || (series.length > 0 && (series[0].created > 0 || series[0].completed > 0))
    // Çok sayıda etiket üst üste binmesin diye her k. etiket gösterilir.
    readonly property int labelStep: Math.max(1, Math.ceil(series.length / 8))

    onSeriesChanged: chart.requestPaint()

    Connections {
        target: themeBridge
        function onThemeChanged() { chart.requestPaint() }
    }

    // Uçlardaki noktalar ve çizgi kalınlığı kırpılmasın diye çizim alanının iki yanında pay bırakılır.
    readonly property int plotPad: 10

    function xAt(index, width) {
        if (series.length <= 1) return width / 2
        return plotPad + index * (width - 2 * plotPad) / (series.length - 1)
    }

    function yAt(value, height) {
        return height - 6 - (value / maxValue) * (height - 12)
    }

    Column {
        anchors.fill: parent
        spacing: 10

        RowLayout {
            width: parent.width
            spacing: 14

            Text {
                text: i18nBridge.tr("analytics_panel_flow_title", "Açılan ve Tamamlanan Görevler")
                font.pixelSize: 14
                font.weight: Font.DemiBold
                color: themeBridge.textPrimary
                Layout.fillWidth: true
                elide: Text.ElideRight
            }

            Repeater {
                model: [
                    { label: i18nBridge.tr("analytics_flow_created", "Açılan"), color: root.createdColor },
                    { label: i18nBridge.tr("analytics_flow_completed", "Tamamlanan"), color: root.completedColor }
                ]

                Row {
                    spacing: 6
                    Rectangle { width: 10; height: 10; radius: 5; color: modelData.color; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: modelData.label; font.pixelSize: 11; color: themeBridge.textSecondary }
                }
            }

            Text {
                text: i18nBridge.tr("analytics_flow_net", "Net birikim") + ": " + (root.netOpen > 0 ? "+" : "") + root.netOpen
                font.pixelSize: 11
                font.weight: Font.DemiBold
                color: root.netOpen > 0 ? themeBridge.warning : themeBridge.success
            }
        }

        Item {
            id: plot
            width: parent.width
            height: parent.height - 34

            Text {
                anchors.centerIn: parent
                text: i18nBridge.tr("analytics_no_data", "Bu dönemde kayıt bulunmuyor.")
                font.pixelSize: 13
                color: themeBridge.textMuted
                visible: !root.hasData
            }

            Text {
                x: 0
                y: 0
                text: root.maxValue.toString()
                font.pixelSize: 10
                color: themeBridge.textMuted
                visible: root.hasData
            }

            Text {
                x: 0
                y: chart.height - height
                text: "0"
                font.pixelSize: 10
                color: themeBridge.textMuted
                visible: root.hasData
            }

            Canvas {
                id: chart
                x: 28
                // Sağda son etiketin (56 px, ortalı) sığacağı boşluk kalır.
                width: parent.width - 28 - 28
                height: parent.height - 20
                visible: root.hasData

                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()

                onPaint: {
                    var ctx = getContext("2d")
                    ctx.clearRect(0, 0, width, height)
                    ctx.lineWidth = 1
                    ctx.strokeStyle = themeBridge.border
                    for (var g = 0; g <= 2; g++) {
                        var gy = Math.round(6 + g * (height - 12) / 2) + 0.5
                        ctx.beginPath()
                        ctx.moveTo(0, gy)
                        ctx.lineTo(width, gy)
                        ctx.stroke()
                    }
                    drawLine(ctx, "created", themeBridge.accentStart)
                    drawLine(ctx, "completed", themeBridge.success)
                }

                function drawLine(ctx, key, color) {
                    var s = root.series
                    if (s.length === 0) return
                    ctx.strokeStyle = color
                    ctx.fillStyle = color
                    ctx.lineWidth = 2
                    ctx.lineJoin = "round"
                    ctx.beginPath()
                    for (var i = 0; i < s.length; i++) {
                        var x = root.xAt(i, width)
                        var y = root.yAt(s[i][key], height)
                        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y)
                    }
                    ctx.stroke()
                    for (var j = 0; j < s.length; j++) {
                        ctx.beginPath()
                        ctx.arc(root.xAt(j, width), root.yAt(s[j][key], height), 3, 0, 2 * Math.PI)
                        ctx.fill()
                    }
                }
            }

            Repeater {
                model: root.series

                Text {
                    x: chart.x + root.xAt(index, chart.width) - width / 2
                    y: chart.height + 4
                    width: 56
                    horizontalAlignment: Text.AlignHCenter
                    text: modelData.label
                    font.pixelSize: 10
                    color: themeBridge.textSecondary
                    elide: Text.ElideRight
                    visible: root.hasData && index % root.labelStep === 0
                }
            }
        }
    }
}
