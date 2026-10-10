import QtQuick 2.15
import QtQuick.Controls 2.15
import "../components"

Item {
    id: archiveViewRoot
    anchors.fill: parent

    property int pendingDeleteId: 0
    property string pendingDeleteTitle: ""
    property bool confirmModalVisible: false

    Component.onCompleted: {
        archiveViewModel.loadArchivedProjects();
    }

    Column {
        anchors.fill: parent
        padding: 24
        spacing: 20

        // ── Başlık ve Sayaç ─────────────────────────────────────────────────
        Row {
            width: parent.width - 48
            spacing: 16

            Column {
                spacing: 4
                Text {
                    text: i18nBridge.tr("nav_archive", "Arşiv")
                    font.pixelSize: 22
                    font.weight: Font.Bold
                    color: themeBridge.textPrimary
                }
                Text {
                    text: i18nBridge.tr("archive_subtitle", "Arşivlenen projeleri geri yükleyebilir veya kalıcı olarak silebilirsiniz.")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }

            AppBadge {
                text: archiveViewModel.count + " " + i18nBridge.tr("archive_count_suffix", "proje")
                variant: "neutral"
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // ── Boş Durum ───────────────────────────────────────────────────────
        AppCard {
            width: parent.width - 48
            height: 280
            visible: archiveViewModel.count === 0

            Column {
                anchors.centerIn: parent
                spacing: 12

                AppIcon {
                    name: "archive"
                    size: 48
                    color: themeBridge.textMuted
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("archive_empty", "Arşivlenmiş proje yok.")
                    font.pixelSize: 16
                    font.weight: Font.DemiBold
                    color: themeBridge.textPrimary
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: i18nBridge.tr("archive_empty_desc", "Projeler sayfasından projeleri arşivleyebilirsiniz.")
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }
            }
        }

        // ── Arşiv Listesi ───────────────────────────────────────────────────
        ScrollView {
            id: archiveScroll
            width: parent.width - 48
            height: parent.height - 100
            contentWidth: availableWidth
            clip: true
            visible: archiveViewModel.count > 0

            ScrollBar.vertical: AppScrollBar { }

            Column {
                width: archiveScroll.availableWidth - 14
                spacing: 12

                Repeater {
                    model: archiveViewModel.archivedProjects

                    AppCard {
                        width: parent.width
                        height: 76

                        Row {
                            anchors.fill: parent
                            anchors.leftMargin: 16
                            anchors.rightMargin: 16
                            spacing: 16

                            // Sol İkon
                            Rectangle {
                                width: 40
                                height: 40
                                radius: 8
                                color: themeBridge.background
                                anchors.verticalCenter: parent.verticalCenter

                                AppIcon {
                                    name: "archive"
                                    size: 18
                                    color: themeBridge.textMuted
                                    anchors.centerIn: parent
                                }
                            }

                            // Proje Başlığı ve Durum
                            Column {
                                width: parent.width - 240
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 4

                                Row {
                                    spacing: 8

                                    Text {
                                        text: modelData.title
                                        font.pixelSize: 14
                                        font.weight: Font.DemiBold
                                        color: themeBridge.textPrimary
                                        elide: Text.ElideRight
                                        maximumLineCount: 1
                                    }

                                    AppBadge {
                                        text: modelData.statusLabel
                                        variant: "neutral"
                                    }
                                }

                                Text {
                                    text: modelData.shortDescription || i18nBridge.tr("common_no_desc", "Açıklama belirtilmemiş")
                                    font.pixelSize: 12
                                    color: themeBridge.textSecondary
                                    elide: Text.ElideRight
                                    maximumLineCount: 1
                                    width: parent.width
                                }
                            }

                            // Aksiyon Butonları
                            Row {
                                anchors.verticalCenter: parent.verticalCenter
                                spacing: 8

                                AppButton {
                                    text: i18nBridge.tr("action_restore", "Geri Al")
                                    variant: "secondary"
                                    onClicked: archiveViewModel.restoreProject(modelData.id)
                                }

                                AppButton {
                                    text: i18nBridge.tr("action_delete", "Kalıcı Sil")
                                    variant: "danger"
                                    onClicked: {
                                        archiveViewRoot.pendingDeleteId = modelData.id;
                                        archiveViewRoot.pendingDeleteTitle = modelData.title;
                                        archiveViewRoot.confirmModalVisible = true;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ── Silme Onay Modalı ───────────────────────────────────────────────────
    Rectangle {
        id: confirmModal
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.6)
        visible: archiveViewRoot.confirmModalVisible
        z: 999

        MouseArea {
            anchors.fill: parent
            onClicked: archiveViewRoot.confirmModalVisible = false
        }

        AppCard {
            width: 440
            height: 200
            anchors.centerIn: parent

            MouseArea { anchors.fill: parent } // engelle

            Column {
                anchors.fill: parent
                spacing: 16

                Row {
                    spacing: 12
                    AppIcon {
                        name: "trash"
                        size: 24
                        color: themeBridge.danger
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Text {
                        text: i18nBridge.tr("archive_delete_title", "Projeyi Kalıcı Olarak Sil")
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        color: themeBridge.textPrimary
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: i18nBridge.tr(
                        "archive_delete_confirm",
                        "Bu proje ve ilişkili tüm görevler, notlar ve kaynaklar kalıcı olarak silinecektir. Bu işlem geri alınamaz."
                    )
                    font.pixelSize: 13
                    color: themeBridge.textSecondary
                }

                Row {
                    anchors.right: parent.right
                    spacing: 12

                    AppButton {
                        text: i18nBridge.tr("action_cancel", "Vazgeç")
                        variant: "secondary"
                        onClicked: archiveViewRoot.confirmModalVisible = false
                    }

                    AppButton {
                        text: i18nBridge.tr("action_delete_confirm", "Evet, Kalıcı Olarak Sil")
                        variant: "danger"
                        onClicked: {
                            archiveViewModel.deleteProject(archiveViewRoot.pendingDeleteId);
                            archiveViewRoot.confirmModalVisible = false;
                        }
                    }
                }
            }
        }
    }
}
