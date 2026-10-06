import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../theme"
import "memo"

Item {
    id: memoViewRoot
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.xl
        spacing: Theme.spacing.lg

        // Üst Araç Çubuğu
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.md

            RowLayout {
                spacing: Theme.spacing.sm
                AppIcon {
                    name: "note-sticky"
                    size: 24
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: i18nBridge.tr("memo_title", "Notlarım")
                    font.pixelSize: Theme.typography.sizeH2
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.color("text_primary")
                }
            }

            Item { Layout.fillWidth: true }

            // Arama Kutusu
            AppTextInput {
                id: searchInput
                placeholder: i18nBridge.tr("memo_search_placeholder", "Notlarda ara...")
                Layout.preferredWidth: 260
                onTextChanged: {
                    if (memoViewModel) memoViewModel.setSearchQuery(text)
                }
            }

            // "+ Yeni Not Ekle" Butonu
            AppButton {
                text: i18nBridge.tr("memo_new_btn", "Yeni Not")
                iconName: "plus"
                btnVariant: "primary"
                onClicked: {
                    if (memoViewModel) memoViewModel.createMemo()
                }
            }
        }

        // Ana İçerik: Bölünmüş Görünüm (SplitView)
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal

            handle: Rectangle {
                implicitWidth: 8
                color: "transparent"
                Rectangle {
                    anchors.centerIn: parent
                    width: 2
                    height: parent.height
                    radius: 1
                    color: SplitHandle.hovered || SplitHandle.pressed ? Theme.accent(themeBridge.currentTheme) : themeBridge.color("border")
                }
            }

            // Sol Panel: Yapışkan Notlar Listesi
            AppCard {
                SplitView.preferredWidth: 340
                SplitView.minimumWidth: 260
                SplitView.fillHeight: true
                padding: 10

                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.spacing.sm

                    ListView {
                        id: memoListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: memoViewModel ? memoViewModel.memoModel : null
                        spacing: Theme.spacing.sm
                        boundsBehavior: Flickable.StopAtBounds

                        ScrollBar.vertical: AppScrollBar {
                            id: memoScrollBar
                        }

                        delegate: MemoCard {}

                        // Boş Durum
                        Item {
                            anchors.centerIn: parent
                            width: 260
                            height: 180
                            visible: memoListView.count === 0

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: Theme.spacing.md

                                AppIcon {
                                    name: "note-sticky"
                                    size: 40
                                    color: themeBridge.color("text_muted")
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                Text {
                                    text: i18nBridge.tr("memo_empty_title", "Henüz not yok")
                                    font.pixelSize: Theme.typography.sizeH3
                                    font.weight: Theme.typography.weightSemiBold
                                    color: themeBridge.color("text_primary")
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                AppButton {
                                    text: i18nBridge.tr("memo_new_btn", "+ Yeni Not")
                                    btnVariant: "primary"
                                    Layout.alignment: Qt.AlignHCenter
                                    onClicked: {
                                        if (memoViewModel) memoViewModel.createMemo()
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Sağ Panel: Zengin Metin ve Çizim Editörü
            MemoEditor {
                SplitView.fillWidth: true
                SplitView.fillHeight: true
            }
        }
    }
}
