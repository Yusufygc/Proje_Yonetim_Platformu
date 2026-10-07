import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../components"
import "../../../theme"

// Mod seçimi, şekil araçları, geri al/yinele ve temizle.
Flickable {
    id: bar

    // Çizim durumu üst bileşende tutulur; çubuk yalnızca seçim isteği bildirir.
    property string toolMode: "draw"
    property string activeTool: "pen"
    property bool canUndo: false
    property bool canRedo: false

    signal modeSelected(string mode)
    signal toolSelected(string tool)
    signal templateRequested()
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
                    btnVariant: bar.toolMode === "draw" ? "primary" : "ghost"
                    implicitHeight: 24
                    onClicked: {
                        bar.toolMode = "draw"
                        if (bar.activeTool.startsWith("flow_")) bar.activeTool = "pen"
                    }
                }

                AppButton {
                    text: "🔷 " + i18nBridge.tr("tab_tools_flowchart", "Akış Şeması")
                    btnVariant: bar.toolMode === "flowchart" ? "primary" : "ghost"
                    implicitHeight: 24
                    onClicked: {
                        bar.toolMode = "flowchart"
                        bar.activeTool = "flow_process"
                    }
                }
            }
        }

        Rectangle { width: 1; height: 18; color: themeBridge.color("border") }

        // ── Çizim Araçları Grubu ──
        RowLayout {
            visible: bar.toolMode === "draw"
            spacing: Theme.spacing.xs

            AppButton {
                text: "✏️ " + i18nBridge.tr("tool_pen", "Kalem")
                btnVariant: bar.activeTool === "pen" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("pen")
            }

            AppButton {
                text: "➖ " + i18nBridge.tr("tool_line", "Çizgi")
                btnVariant: bar.activeTool === "line" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("line")
            }

            AppButton {
                text: "➔ " + i18nBridge.tr("tool_arrow", "Ok")
                btnVariant: bar.activeTool === "arrow" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("arrow")
            }

            AppButton {
                text: "▭ " + i18nBridge.tr("tool_rect", "Kutu")
                btnVariant: bar.activeTool === "rect" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("rect")
            }

            AppButton {
                text: "▢ " + i18nBridge.tr("tool_round_rect", "Oval")
                btnVariant: bar.activeTool === "round_rect" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("round_rect")
            }

            AppButton {
                text: "◯ " + i18nBridge.tr("tool_circle", "Daire")
                btnVariant: bar.activeTool === "circle" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("circle")
            }

            AppButton {
                text: "⌫ " + i18nBridge.tr("tool_eraser", "Silgi")
                btnVariant: bar.activeTool === "eraser" ? "warning" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("eraser")
            }
        }

        // ── Akış Şeması Blokları Grubu ──
        RowLayout {
            visible: bar.toolMode === "flowchart"
            spacing: Theme.spacing.xs

            AppButton {
                text: "🟢 " + i18nBridge.tr("flow_terminator", "Başla/Bitir")
                btnVariant: bar.activeTool === "flow_start" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("flow_start")
            }

            AppButton {
                text: "🟦 " + i18nBridge.tr("flow_process", "İşlem")
                btnVariant: bar.activeTool === "flow_process" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("flow_process")
            }

            AppButton {
                text: "🔶 " + i18nBridge.tr("flow_decision", "Karar")
                btnVariant: bar.activeTool === "flow_decision" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("flow_decision")
            }

            AppButton {
                text: "▱ " + i18nBridge.tr("flow_io", "Girdi/Çıktı")
                btnVariant: bar.activeTool === "flow_io" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("flow_io")
            }

            AppButton {
                text: "➔ " + i18nBridge.tr("flow_arrow", "Akış Oku")
                btnVariant: bar.activeTool === "arrow" ? "primary" : "secondary"
                implicitHeight: 28
                onClicked: bar.toolSelected("arrow")
            }

            AppButton {
                text: "📋 " + i18nBridge.tr("flow_template", "Hazır Şema")
                btnVariant: "secondary"
                implicitHeight: 28
                onClicked: bar.templateRequested()
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
            enabled: bar.canUndo
            opacity: bar.canUndo ? 1.0 : 0.4
            onClicked: bar.undoRequested()
        }

        AppButton {
            text: "↪"
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
