import QtQuick
import QtQuick.Layouts
import "../../theme"

RowLayout {
    spacing: Theme.spacing.md

    Rectangle {
        Layout.fillWidth: true
        height: 38
        radius: Theme.radius.small
        color: themeBridge.surface
        border.color: themeBridge.border

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Theme.spacing.md
            anchors.rightMargin: Theme.spacing.md
            spacing: Theme.spacing.lg

            RowLayout {
                spacing: Theme.spacing.xs
                Text {
                    text: i18nBridge.tr("stat_total_tasks", "Toplam:")
                    font.pixelSize: Theme.typography.sizeSmall
                    color: themeBridge.textSecondary
                }
                Text {
                    text: taskViewModel ? taskViewModel.totalTasks.toString() : "0"
                    font.pixelSize: Theme.typography.sizeSmall
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.textPrimary
                }
            }

            RowLayout {
                spacing: Theme.spacing.xs
                Text {
                    text: i18nBridge.tr("stat_completed_tasks", "Tamamlanan:")
                    font.pixelSize: Theme.typography.sizeSmall
                    color: themeBridge.textSecondary
                }
                Text {
                    text: taskViewModel ? taskViewModel.completedTasks.toString() : "0"
                    font.pixelSize: Theme.typography.sizeSmall
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.success
                }
            }

            RowLayout {
                spacing: Theme.spacing.xs
                Text {
                    text: i18nBridge.tr("stat_in_progress_tasks", "Devam Eden:")
                    font.pixelSize: Theme.typography.sizeSmall
                    color: themeBridge.textSecondary
                }
                Text {
                    text: taskViewModel ? taskViewModel.inProgressTasks.toString() : "0"
                    font.pixelSize: Theme.typography.sizeSmall
                    font.weight: Theme.typography.weightBold
                    color: Theme.accent(themeBridge.currentTheme)
                }
            }

            RowLayout {
                spacing: Theme.spacing.xs
                Text {
                    text: i18nBridge.tr("stat_blocked_tasks", "Engellenen:")
                    font.pixelSize: Theme.typography.sizeSmall
                    color: themeBridge.textSecondary
                }
                Text {
                    text: taskViewModel ? taskViewModel.blockedTasks.toString() : "0"
                    font.pixelSize: Theme.typography.sizeSmall
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.danger
                }
            }
        }
    }
}
