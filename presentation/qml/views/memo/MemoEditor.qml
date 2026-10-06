import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../components"
import "../../theme"

AppCard {
    id: root

    property var memo: memoViewModel ? memoViewModel.selectedMemo : ({})
    property bool hasMemo: memo && memo.id !== undefined && memo.id !== 0
    property int currentTab: 0

    Connections {
        target: memoViewModel
        function onSelectedMemoChanged() {
            if (memoViewModel && root.hasMemo) {
                titleInput.text = root.memo.title || ""
                bodyInput.text = root.memo.body || ""
                drawingCanvas.loadDrawingJson(root.memo.drawingData || "")
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.lg
        spacing: Theme.spacing.md

        // Not Seçili Değilse Boş Durum
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: !root.hasMemo

            ColumnLayout {
                anchors.centerIn: parent
                spacing: Theme.spacing.md

                AppIcon {
                    name: "note-sticky"
                    size: 48
                    color: themeBridge.color("text_muted")
                    Layout.alignment: Qt.AlignHCenter
                }

                Text {
                    text: i18nBridge.tr("memo_select_prompt", "Düzenlemek için bir not seçin veya yeni oluşturun")
                    font.pixelSize: Theme.typography.sizeH3
                    color: themeBridge.color("text_secondary")
                    Layout.alignment: Qt.AlignHCenter
                }

                AppButton {
                    text: i18nBridge.tr("memo_new_btn", "Yeni Not Ekle")
                    btnVariant: "primary"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: {
                        if (memoViewModel) memoViewModel.createMemo()
                    }
                }
            }
        }

        // Not Düzenleyici
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.md
            visible: root.hasMemo

            // Başlık Satırı & Sekmeler & Eylemler
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.md

                // Başlık Girişi
                AppTextInput {
                    id: titleInput
                    placeholder: i18nBridge.tr("memo_title_placeholder", "Not Başlığı...")
                    Layout.fillWidth: true
                    showVoiceInput: true
                }

                // Sekme Butonları (Düzenle / Önizleme / Çizim)
                RowLayout {
                    spacing: 4

                    AppButton {
                        text: i18nBridge.tr("tab_edit_note", "Düzenle")
                        iconName: "pencil"
                        btnVariant: root.currentTab === 0 ? "primary" : "secondary"
                        onClicked: root.currentTab = 0
                    }

                    AppButton {
                        text: i18nBridge.tr("tab_preview_note", "Önizleme")
                        iconName: "eye"
                        btnVariant: root.currentTab === 1 ? "primary" : "secondary"
                        onClicked: root.currentTab = 1
                    }

                    AppButton {
                        text: i18nBridge.tr("tab_drawing_note", "Çizim")
                        iconName: "pen-tool"
                        btnVariant: root.currentTab === 2 ? "primary" : "secondary"
                        onClicked: root.currentTab = 2
                    }
                }

                Rectangle { width: 1; height: 24; color: themeBridge.color("border") }

                // Kaydet Butonu
                AppButton {
                    text: i18nBridge.tr("action_save", "Kaydet")
                    iconName: "check"
                    btnVariant: "primary"
                    onClicked: root.saveCurrentMemo()
                }

                // Sil Butonu
                AppButton {
                    iconName: "trash-2"
                    btnVariant: "danger"
                    implicitWidth: 34
                    onClicked: {
                        if (memoViewModel && root.hasMemo) {
                            memoViewModel.deleteMemo(root.memo.id)
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: themeBridge.color("border")
            }

            // Sekme 0: Markdown Düzenleyici
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.spacing.xs
                visible: root.currentTab === 0

                // Biçimlendirme Araç Çubuğu
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.xs

                    AppButton {
                        text: "H"
                        btnVariant: "secondary"
                        implicitWidth: 28
                        implicitHeight: 28
                        onClicked: insertFormatting("### ", "")
                    }

                    AppButton {
                        text: "B"
                        btnVariant: "secondary"
                        implicitWidth: 28
                        implicitHeight: 28
                        onClicked: insertFormatting("**", "**")
                    }

                    AppButton {
                        text: "I"
                        btnVariant: "secondary"
                        implicitWidth: 28
                        implicitHeight: 28
                        onClicked: insertFormatting("*", "*")
                    }

                    AppButton {
                        text: "•"
                        btnVariant: "secondary"
                        implicitWidth: 28
                        implicitHeight: 28
                        onClicked: insertFormatting("\n- ", "")
                    }

                    AppButton {
                        text: "1."
                        btnVariant: "secondary"
                        implicitWidth: 28
                        implicitHeight: 28
                        onClicked: insertFormatting("\n1. ", "")
                    }

                    AppButton {
                        text: "</>"
                        btnVariant: "secondary"
                        implicitWidth: 32
                        implicitHeight: 28
                        onClicked: insertFormatting("`", "`")
                    }

                    VoiceInputButton {
                        target: bodyInput
                        width: 28
                        height: 28
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: root.memo.updatedAt ? (i18nBridge.tr("label_last_modified", "Son Değişiklik:") + " " + root.memo.updatedAt) : ""
                        font.pixelSize: Theme.typography.sizeSmall
                        color: themeBridge.color("text_muted")
                    }
                }

                ScrollView {
                    id: editScroll
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true

                    ScrollBar.vertical: AppScrollBar { }

                    TextArea {
                        id: bodyInput
                        placeholderText: i18nBridge.tr("memo_markdown_placeholder", "Notlarınızı Markdown formatında buraya yazın (örn: # Başlık, **kalın**, - liste)...")
                        color: themeBridge.color("text_primary")
                        font.pixelSize: Theme.typography.sizeBody
                        font.family: Theme.typography.fontFamily
                        textFormat: TextEdit.PlainText
                        wrapMode: TextEdit.Wrap
                        selectByMouse: true
                        rightPadding: 16
                        background: Rectangle {
                            color: "transparent"
                        }
                    }
                }
            }

            // Sekme 1: Markdown Önizleme
            ScrollView {
                id: previewScroll
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                visible: root.currentTab === 1

                ScrollBar.vertical: AppScrollBar { }

                Text {
                    id: markdownPreview
                    width: previewScroll.availableWidth - 16
                    text: bodyInput.text.trim().length > 0 ? bodyInput.text : ("*" + i18nBridge.tr("memo_empty_preview", "Önizlenecek içerik bulunmuyor...") + "*")
                    textFormat: Text.MarkdownText
                    font.pixelSize: Theme.typography.sizeBody
                    font.family: Theme.typography.fontFamily
                    color: themeBridge.color("text_primary")
                    wrapMode: Text.Wrap
                    lineHeight: 1.4
                }
            }

            // Sekme 2: Çizim Tuvali
            DrawingCanvas {
                id: drawingCanvas
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: root.currentTab === 2
            }
        }
    }

    function insertFormatting(prefix, suffix) {
        var start = bodyInput.selectionStart
        var end = bodyInput.selectionEnd
        var txt = bodyInput.text
        if (start !== end) {
            var selected = txt.substring(start, end)
            bodyInput.text = txt.substring(0, start) + prefix + selected + suffix + txt.substring(end)
            bodyInput.select(start + prefix.length, start + prefix.length + selected.length)
        } else {
            var pos = bodyInput.cursorPosition
            bodyInput.insert(pos, prefix + suffix)
            bodyInput.cursorPosition = pos + prefix.length
        }
        bodyInput.forceActiveFocus()
    }

    function saveCurrentMemo() {
        if (memoViewModel && root.hasMemo) {
            var drawingJson = drawingCanvas.getDrawingJson()
            memoViewModel.saveMemo(root.memo.id, titleInput.text, bodyInput.text, drawingJson)
        }
    }
}
