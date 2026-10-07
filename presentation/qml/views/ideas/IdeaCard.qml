import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

Rectangle {
    id: root

    width: ListView.view ? (ListView.view.width - 14) : 340
    height: 96
    radius: Theme.radius.medium

    property bool isSelected: ideaViewModel ? ideaViewModel.selectedIdeaId === model.ideaId : false
    property bool isHovered: cardMouseArea.containsMouse

    color: {
        if (isSelected) return Theme.accentAlpha(themeBridge.currentTheme, 0.15)
        if (isHovered) return themeBridge.surfaceAlt
        return themeBridge.surface
    }

    border.color: isSelected ? Theme.accent(themeBridge.currentTheme) : themeBridge.border
    border.width: isSelected ? 1.5 : 1

    Behavior on color { ColorAnimation { duration: Theme.animation.fast } }

    MouseArea {
        id: cardMouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: {
            if (ideaViewModel) ideaViewModel.selectIdea(model.ideaId)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.xs

        // Üst Satır: Öncelik Rozeti + Durum Rozeti + Sil Butonu
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            AppBadge {
                text: {
                    if (model.priority === "CRITICAL") return i18nBridge.tr("priority_critical", "Kritik")
                    if (model.priority === "HIGH") return i18nBridge.tr("priority_high", "Yüksek")
                    if (model.priority === "LOW") return i18nBridge.tr("priority_low", "Düşük")
                    return i18nBridge.tr("priority_medium", "Orta")
                }
                variant: {
                    if (model.priority === "CRITICAL") return "danger"
                    if (model.priority === "HIGH") return "warning"
                    if (model.priority === "LOW") return "neutral"
                    return "info"
                }
                size: "sm"
            }

            StatusIndicator {
                status: model.status
            }

            Item { Layout.fillWidth: true }

            AppButton {
                iconName: "trash-2"
                btnVariant: "secondary"
                implicitWidth: 24
                implicitHeight: 24
                opacity: isHovered || isSelected ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: Theme.animation.fast } }
                onClicked: {
                    if (ideaViewModel) ideaViewModel.deleteIdea(model.ideaId)
                }
            }
        }

        // Fikir Başlığı
        Text {
            text: model.title
            font.pixelSize: Theme.typography.sizeBody
            font.weight: Theme.typography.weightSemiBold
            font.strikeout: model.status === "CONVERTED"
            color: model.status === "CONVERTED" ? themeBridge.textMuted : themeBridge.textPrimary
            Layout.fillWidth: true
            elide: Text.ElideRight
        }

        // Problem veya Hedef Kullanıcı Özeti
        Text {
            text: model.targetUser ? (i18nBridge.tr("label_target_user", "Hedef:") + " " + model.targetUser) : (model.problem || "")
            font.pixelSize: Theme.typography.sizeSmall
            color: themeBridge.textSecondary
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
    }
}
