import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

Rectangle {
    id: root

    width: ListView.view ? (ListView.view.width - 14) : 280
    height: 100
    radius: Theme.radius.medium

    property bool isSelected: memoViewModel ? memoViewModel.selectedMemoId === model.memoId : false
    property bool isHovered: cardMouseArea.containsMouse

    // Pastel Yapışkan Not Renkleri
    readonly property var pastelLight: ["#FEF9C3", "#DCFCE7", "#E0F2FE", "#FCE7F3", "#EDE9FE"]
    readonly property var pastelDark: ["#332E14", "#12301E", "#0E2838", "#331826", "#231840"]

    color: {
        var idx = Math.abs(model.memoId || 0) % 5
        var palette = themeBridge.isDark ? pastelDark : pastelLight
        return palette[idx]
    }

    border.color: isSelected ? Theme.accent(themeBridge.currentTheme) : (isHovered ? themeBridge.color("border") : "transparent")
    border.width: isSelected ? 2 : 1

    Behavior on border.color { ColorAnimation { duration: Theme.animation.fast } }

    MouseArea {
        id: cardMouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: {
            if (memoViewModel) memoViewModel.selectMemo(model.memoId)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.xs

        // Başlık ve Eylemler
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            Text {
                text: model.title || i18nBridge.tr("untitled_note", "İsimsiz Not")
                font.pixelSize: Theme.typography.sizeBody
                font.weight: Theme.typography.weightSemiBold
                color: themeBridge.color("text_primary")
                Layout.fillWidth: true
                elide: Text.ElideRight
            }

            AppIcon {
                name: "pen-tool"
                size: 14
                color: Theme.accent(themeBridge.currentTheme)
                visible: model.drawingData && model.drawingData.length > 5
            }

            AppButton {
                iconName: "trash-2"
                btnVariant: "secondary"
                implicitWidth: 22
                implicitHeight: 22
                opacity: isHovered || isSelected ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: Theme.animation.fast } }
                onClicked: {
                    if (memoViewModel) memoViewModel.deleteMemo(model.memoId)
                }
            }
        }

        // Metin Özeti
        Text {
            text: model.body || i18nBridge.tr("memo_empty_body", "Boş not...")
            font.pixelSize: Theme.typography.sizeSmall
            color: themeBridge.color("text_secondary")
            Layout.fillWidth: true
            elide: Text.ElideRight
            maximumLineCount: 2
        }

        Item { Layout.fillHeight: true }

        // Tarih
        Text {
            text: model.updatedAt || ""
            font.pixelSize: 11
            color: themeBridge.color("text_muted")
            Layout.fillWidth: true
        }
    }
}
