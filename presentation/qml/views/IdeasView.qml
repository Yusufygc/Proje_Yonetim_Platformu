import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../dialogs"
import "../theme"
import "ideas"

Item {
    id: ideasViewRoot
    anchors.fill: parent

    property string currentStatusFilter: "ALL"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.xl
        spacing: Theme.spacing.lg

        // Üst Araç Çubuğu
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.md

            // Başlık
            RowLayout {
                spacing: Theme.spacing.sm
                AppIcon {
                    name: "ideas"
                    size: 24
                    color: Theme.accent(themeBridge.currentTheme)
                }

                Text {
                    text: i18nBridge.tr("ideas_title", "Fikir Havuzu")
                    font.pixelSize: Theme.typography.sizeH2
                    font.weight: Theme.typography.weightBold
                    color: themeBridge.color("text_primary")
                }
            }

            Item { Layout.fillWidth: true }

            // Arama Kutusu
            AppTextInput {
                id: searchInput
                placeholder: i18nBridge.tr("ideas_search_placeholder", "Fikirlerde ara...")
                Layout.preferredWidth: 260
                onTextChanged: {
                    if (ideaViewModel) ideaViewModel.setSearchQuery(text)
                }
            }

            // "+ Yeni Fikir" Butonu
            AppButton {
                text: i18nBridge.tr("ideas_add_btn", "+ Yeni Fikir")
                iconName: "plus"
                btnVariant: "primary"
                onClicked: {
                    if (ideaViewModel) ideaViewModel.openCreateDialog()
                }
            }
        }

        // Filtre Hapları (Filter Pills)
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            Repeater {
                model: [
                    { "text": i18nBridge.tr("filter_all", "Tümü"), "value": "ALL" },
                    { "text": i18nBridge.tr("idea_status_raw", "Ham Fikir"), "value": "RAW" },
                    { "text": i18nBridge.tr("idea_status_reviewing", "İnceleniyor"), "value": "REVIEWING" },
                    { "text": i18nBridge.tr("idea_status_validating", "Doğrulanıyor"), "value": "VALIDATING" },
                    { "text": i18nBridge.tr("idea_status_converted", "Projeye Dönüştürüldü"), "value": "CONVERTED" },
                    { "text": i18nBridge.tr("idea_status_deferred", "Ertelendi"), "value": "DEFERRED" }
                ]

                Rectangle {
                    id: pill
                    implicitWidth: pillText.implicitWidth + 24
                    implicitHeight: 32
                    radius: 16

                    property bool isActive: ideasViewRoot.currentStatusFilter === modelData.value

                    color: isActive ? Theme.accent(themeBridge.currentTheme) : themeBridge.color("surface")
                    border.color: isActive ? Theme.accent(themeBridge.currentTheme) : themeBridge.color("border")
                    border.width: 1

                    Behavior on color { ColorAnimation { duration: Theme.animation.fast } }

                    Text {
                        id: pillText
                        anchors.centerIn: parent
                        text: modelData.text
                        font.pixelSize: Theme.typography.sizeSmall
                        font.weight: pill.isActive ? Theme.typography.weightSemiBold : Theme.typography.weightNormal
                        color: pill.isActive ? "#FFFFFF" : themeBridge.color("text_secondary")
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            ideasViewRoot.currentStatusFilter = modelData.value
                            if (ideaViewModel) ideaViewModel.setStatusFilter(modelData.value)
                        }
                    }
                }
            }
        }

        // Ana İçerik Bölünmüş Görünüm (SplitView)
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

            // Sol Panel: Fikir Listesi
            AppCard {
                SplitView.preferredWidth: 380
                SplitView.minimumWidth: 300
                SplitView.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacing.md
                    spacing: Theme.spacing.sm

                    ListView {
                        id: ideaListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: ideaViewModel ? ideaViewModel.ideaModel : null
                        spacing: Theme.spacing.sm

                        delegate: IdeaCard {}

                        // Boş Durum
                        Item {
                            anchors.centerIn: parent
                            width: 260
                            height: 180
                            visible: ideaListView.count === 0

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: Theme.spacing.md

                                AppIcon {
                                    name: "ideas"
                                    size: 40
                                    color: themeBridge.color("text_muted")
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                Text {
                                    text: i18nBridge.tr("ideas_empty", "Henüz fikir yok")
                                    font.pixelSize: Theme.typography.sizeH3
                                    font.weight: Theme.typography.weightSemiBold
                                    color: themeBridge.color("text_primary")
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                AppButton {
                                    text: i18nBridge.tr("ideas_add_btn", "+ Yeni Fikir")
                                    btnVariant: "primary"
                                    Layout.alignment: Qt.AlignHCenter
                                    onClicked: {
                                        if (ideaViewModel) ideaViewModel.openCreateDialog()
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Sağ Panel: Fikir Detay Paneli
            IdeaDetailPanel {
                SplitView.fillWidth: true
                SplitView.fillHeight: true
            }
        }
    }

    // Modal Fikir Dialogu
    IdeaDialog {
        id: ideaDialog
    }
}
