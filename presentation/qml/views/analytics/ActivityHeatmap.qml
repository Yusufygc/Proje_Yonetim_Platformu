import QtQuick 2.15
import QtQuick.Controls 2.15
import "../../components"

// Son 12 haftanın gün gün tamamlanan görev yoğunluğu (sütun: hafta, satır: pazartesi-pazar).
AppCard {
    id: root
    height: 250

    readonly property var cells: analyticsViewModel.heatmap.cells || []
    readonly property int maxCount: analyticsViewModel.heatmap.max || 0
    readonly property int gap: 4
    readonly property int labelWidth: 30
    readonly property int columns: 12
    // Hücre yüksekliği sabit (kart yüksekliğine sığsın), genişliği kartı doldurur.
    readonly property int cellHeight: 20
    readonly property int cellWidth: Math.max(10, Math.min(56, Math.floor((width - 2 * padding - labelWidth - (columns - 1) * gap) / columns)))

    // 0: boş; 1-4: yoğunluk. Vurgu renginin saydamlığı artarak koyulaşır.
    function levelOf(count) {
        if (count <= 0 || maxCount <= 0) return 0
        return Math.min(4, Math.ceil(count / maxCount * 4))
    }

    function colorOf(count) {
        var level = levelOf(count)
        if (level === 0) return themeBridge.surfaceRaised
        var c = Qt.color(themeBridge.accentStart)
        return Qt.rgba(c.r, c.g, c.b, 0.25 + 0.19 * level)
    }

    Column {
        anchors.fill: parent
        spacing: 12

        Text {
            text: i18nBridge.tr("analytics_panel_heatmap_title", "Aktivite (Son 12 Hafta)")
            font.pixelSize: 14
            font.weight: Font.DemiBold
            color: themeBridge.textPrimary
        }

        Item {
            id: grid
            width: parent.width
            height: 7 * root.cellHeight + 6 * root.gap

            Repeater {
                model: [
                    { row: 0, key: "analytics_wd_mon", fallback: "Pzt" },
                    { row: 2, key: "analytics_wd_wed", fallback: "Çar" },
                    { row: 4, key: "analytics_wd_fri", fallback: "Cum" }
                ]

                Text {
                    x: 0
                    y: modelData.row * (root.cellHeight + root.gap) + (root.cellHeight - height) / 2
                    text: i18nBridge.tr(modelData.key, modelData.fallback)
                    font.pixelSize: 10
                    color: themeBridge.textMuted
                }
            }

            Repeater {
                model: root.cells

                Rectangle {
                    x: root.labelWidth + modelData.col * (root.cellWidth + root.gap)
                    y: modelData.row * (root.cellHeight + root.gap)
                    width: root.cellWidth
                    height: root.cellHeight
                    radius: 3
                    color: root.colorOf(modelData.count)
                    visible: !modelData.future

                    MouseArea {
                        id: cellMouse
                        anchors.fill: parent
                        hoverEnabled: true
                    }

                    ToolTip.visible: cellMouse.containsMouse
                    ToolTip.delay: 150
                    ToolTip.text: modelData.label + ": " + modelData.count + " " + i18nBridge.tr("analytics_tasks_unit", "görev")
                }
            }
        }

        Row {
            spacing: 4
            anchors.right: parent.right

            Text {
                text: i18nBridge.tr("analytics_heatmap_less", "Az")
                font.pixelSize: 10
                color: themeBridge.textMuted
                anchors.verticalCenter: parent.verticalCenter
            }

            Repeater {
                model: 5

                Rectangle {
                    width: 12
                    height: 12
                    radius: 3
                    color: root.colorOf(index === 0 ? 0 : index * Math.max(root.maxCount, 4) / 4)
                }
            }

            Text {
                text: i18nBridge.tr("analytics_heatmap_more", "Çok")
                font.pixelSize: 10
                color: themeBridge.textMuted
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}
