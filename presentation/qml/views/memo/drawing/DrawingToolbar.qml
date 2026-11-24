import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../components"
import "../../../theme"

// Şekil araçları, geri al/yinele ve temizle.
Flickable {
    id: bar

    // Çizim durumu üst bileşende tutulur; çubuk yalnızca seçim isteği bildirir.
    property string activeTool: "pen"
    property bool canUndo: false
    property bool canRedo: false

    signal toolSelected(string tool)
    signal undoRequested()
    signal redoRequested()
    signal clearRequested()

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

        // ── Çizim Araçları Grubu ──
        RowLayout {
            spacing: Theme.spacing.xs

            AppButton {
                iconName: "pencil"
                text: i18nBridge.tr("tool_pen", "Kalem")
                btnVariant: bar.activeTool === "pen" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("pen")
            }

            AppButton {
                iconName: "minus"
                text: i18nBridge.tr("tool_line", "Çizgi")
                btnVariant: bar.activeTool === "line" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("line")
            }

            AppButton {
                iconName: "arrow-right"
                text: i18nBridge.tr("tool_arrow", "Ok")
                btnVariant: bar.activeTool === "arrow" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("arrow")
            }

            AppButton {
                iconName: "square"
                text: i18nBridge.tr("tool_rect", "Kutu")
                btnVariant: bar.activeTool === "rect" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("rect")
            }

            AppButton {
                iconName: "square-round"
                text: i18nBridge.tr("tool_round_rect", "Oval")
                btnVariant: bar.activeTool === "round_rect" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("round_rect")
            }

            AppButton {
                iconName: "circle"
                text: i18nBridge.tr("tool_circle", "Daire")
                btnVariant: bar.activeTool === "circle" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("circle")
            }

            AppButton {
                iconName: "eraser"
                text: i18nBridge.tr("tool_eraser", "Silgi")
                btnVariant: bar.activeTool === "eraser" ? "warning" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("eraser")
            }
        }

        Item { Layout.fillWidth: true }

        Rectangle { width: 1; height: 18; color: themeBridge.border }

        // Geri Al / İleri Al
        AppButton {
            iconName: "undo"
            btnVariant: "secondary"
            implicitWidth: 32
            implicitHeight: 28
            enabled: bar.canUndo
            opacity: bar.canUndo ? 1.0 : 0.4
            onClicked: bar.undoRequested()
        }

        AppButton {
            iconName: "redo"
            btnVariant: "secondary"
            implicitWidth: 32
            implicitHeight: 28
            enabled: bar.canRedo
            opacity: bar.canRedo ? 1.0 : 0.4
            onClicked: bar.redoRequested()
        }

        // Temizle Butonu
        AppButton {
            text: i18nBridge.tr("action_clear", "Temizle")
            btnVariant: "secondary"
            implicitHeight: 28
            onClicked: bar.clearRequested()
        }
    }
}
