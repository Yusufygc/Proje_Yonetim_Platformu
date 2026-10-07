import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../../components"

// Tüm görevlerin durum dağılımı halkası; ortada toplam görev sayısı.
AppCard {
    id: root
    height: 250

    readonly property var statuses: analyticsViewModel.statusDistribution
    readonly property int total: {
        var t = 0
        for (var i = 0; i < statuses.length; i++) t += statuses[i].value
        return t
    }

    onStatusesChanged: ring.requestPaint()

    Connections {
        target: themeBridge
        function onThemeChanged() { ring.requestPaint() }
    }

    Column {
        anchors.fill: parent
        spacing: 12

        Text {
            text: i18nBridge.tr("analytics_panel_status_title", "Görev Durumları")
            font.pixelSize: 14
            font.weight: Font.DemiBold
            color: themeBridge.textPrimary
        }

        Row {
            width: parent.width
            height: parent.height - 30
            spacing: 18

            Item {
                width: 150
                height: 150
                anchors.verticalCenter: parent.verticalCenter

                Canvas {
                    id: ring
                    anchors.fill: parent

                    onPaint: {
                        var ctx = getContext("2d")
                        ctx.clearRect(0, 0, width, height)
                        var cx = width / 2
                        var cy = height / 2
                        var radius = width / 2 - 12
                        ctx.lineWidth = 20
                        ctx.lineCap = "butt"
                        // Boş halka izi: veri yokken de şekil görünsün.
                        ctx.strokeStyle = themeBridge.border
                        ctx.beginPath()
                        ctx.arc(cx, cy, radius, 0, 2 * Math.PI)
                        ctx.stroke()
                        if (root.total === 0) return

                        var visibleCount = 0
                        for (var k = 0; k < root.statuses.length; k++) if (root.statuses[k].value > 0) visibleCount++
                        var gap = visibleCount > 1 ? 0.03 : 0
                        var angle = -Math.PI / 2
                        for (var i = 0; i < root.statuses.length; i++) {
                            var item = root.statuses[i]
                            if (item.value === 0) continue
                            var sweep = item.value / root.total * 2 * Math.PI
                            ctx.strokeStyle = item.color
                            ctx.beginPath()
                            ctx.arc(cx, cy, radius, angle + gap / 2, angle + sweep - gap / 2)
                            ctx.stroke()
                            angle += sweep
                        }
                    }
                }

                Column {
                    anchors.centerIn: parent
                    spacing: 0

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: root.total.toString()
                        font.pixelSize: 26
                        font.weight: Font.Bold
                        color: themeBridge.textPrimary
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: i18nBridge.tr("analytics_status_total", "Toplam")
                        font.pixelSize: 11
                        color: themeBridge.textMuted
                    }
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6
                width: parent.width - 150 - 18

                Repeater {
                    model: root.statuses

                    Row {
                        width: parent.width
                        spacing: 8
                        opacity: modelData.value > 0 ? 1.0 : 0.45

                        Rectangle {
                            width: 10
                            height: 10
                            radius: 5
                            color: modelData.color
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: modelData.label
                            width: parent.width - 18 - countText.width - 8
                            font.pixelSize: 12
                            color: themeBridge.textPrimary
                            elide: Text.ElideRight
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            id: countText
                            text: modelData.value.toString()
                            font.pixelSize: 12
                            font.weight: Font.DemiBold
                            color: themeBridge.textSecondary
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }
            }
        }
    }
}
