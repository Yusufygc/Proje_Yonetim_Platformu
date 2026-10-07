import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../../components"
import "../../../theme"

// Renk, çizgi kalınlığı, dolgu, görsel ve araç ipucu çubuğu.
Flickable {
    id: bar

    // Seçili renk, kalınlık ve dolgu üst bileşende tutulur; çubuk yalnızca değişiklik ister.
    property string toolMode: "draw"
    property string activeTool: "pen"
    property string currentColor: "#FFFFFF"
    property int currentLineWidth: 3
    property bool fillEnabled: false
    property bool hasBackgroundImage: false

    signal colorSelected(string color)
    signal lineWidthSelected(int width)
    signal fillToggled()
    signal imagePickRequested()
    signal imageClearRequested()

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
                border.color: bar.activeTool !== "eraser" && bar.currentColor === modelData ? Theme.accent(themeBridge.currentTheme) : "#40888888"
                border.width: bar.activeTool !== "eraser" && bar.currentColor === modelData ? 2.5 : 1

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: bar.colorSelected(modelData)
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
                    btnVariant: bar.currentLineWidth === modelData.val ? "primary" : "secondary"
                    implicitWidth: 34
                    implicitHeight: 28
                    onClicked: bar.lineWidthSelected(modelData.val)
                }
            }
        }

        // Dolgu Seçimi
        AppButton {
            text: bar.fillEnabled ? "■ " + i18nBridge.tr("label_fill", "Dolgulu") : "□ " + i18nBridge.tr("label_outline", "İçi Boş")
            btnVariant: bar.fillEnabled ? "primary" : "secondary"
            implicitHeight: 28
            onClicked: bar.fillToggled()
        }

        Rectangle { width: 1; height: 18; color: themeBridge.color("border") }

        // Görsel Ekle / Arka Planı Kaldır
        AppButton {
            text: "🖼️ " + i18nBridge.tr("tool_image", "Görsel")
            btnVariant: "secondary"
            implicitHeight: 28
            onClicked: bar.imagePickRequested()
        }

        AppButton {
            text: "❌"
            btnVariant: "danger"
            implicitWidth: 28
            implicitHeight: 28
            visible: bar.hasBackgroundImage
            onClicked: bar.imageClearRequested()
        }

        Item { Layout.fillWidth: true }

        Text {
            text: bar.helpText()
            font.pixelSize: 11
            color: themeBridge.color("text_muted")
        }
    }
    function helpText() {
        if (bar.toolMode === "flowchart") {
            switch (bar.activeTool) {
                case "flow_start": return i18nBridge.tr("hint_flow_start", "Başla/Bitir bloğu için sürükleyin (Çift tıkla düzenle)")
                case "flow_process": return i18nBridge.tr("hint_flow_process", "İşlem bloğu için sürükleyin (Çift tıkla düzenle)")
                case "flow_decision": return i18nBridge.tr("hint_flow_decision", "Karar/koşul bloğu için sürükleyin (Çift tıkla düzenle)")
                case "flow_io": return i18nBridge.tr("hint_flow_io", "Girdi/çıktı bloğu için sürükleyin (Çift tıkla düzenle)")
                case "arrow": return i18nBridge.tr("hint_flow_arrow", "Blokları bağlamak için akış oku çekin (Çift tıkla etiketle)")
                default: return ""
            }
        }

        switch (bar.activeTool) {
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
}
