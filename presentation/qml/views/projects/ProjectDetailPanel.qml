import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../components"
import "../../theme"
import "detail"

Item {
    id: detailRoot

    readonly property var p: projectViewModel.selectedProject
    readonly property bool hasProject: projectViewModel.selectedProjectId !== 0 && p && p.title !== undefined
    property int currentTab: 0

    // Boş Durum (Proje Seçilmemişken)
    Column {
        anchors.centerIn: parent
        spacing: 12
        visible: !detailRoot.hasProject

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "◈"
            font.pixelSize: 36
            color: themeBridge.textMuted
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: i18nBridge.tr("detail_empty_message", "Bir proje seçin veya yeni proje oluşturun")
            font.pixelSize: 14
            color: themeBridge.textMuted
            horizontalAlignment: Text.AlignHCenter
        }
    }

    // Proje Detay İçeriği
    // Proje Detay İçeriği
    ScrollView {
        id: detailScroll
        anchors.fill: parent
        visible: detailRoot.hasProject
        contentWidth: availableWidth
        clip: true

        ScrollBar.vertical: AppScrollBar {
            id: detailScrollBar
        }

        Column {
            width: parent.width
            padding: 24
            spacing: 16

            ProjectHeader {
                width: parent.width - 48
                project: detailRoot.p
            }

            ProjectStagesCard {
                width: parent.width - 48
            }

            ProjectTabBar {
                width: parent.width - 48
                currentTab: detailRoot.currentTab
                onTabSelected: function(index) { detailRoot.currentTab = index }
            }

            // Sekme İçerikleri
            AppCard {
                width: parent.width - 48
                height: detailRoot.currentTab === 0 ? 120 : 420

                ProjectSummaryTab {
                    anchors.fill: parent
                    visible: detailRoot.currentTab === 0
                    project: detailRoot.p
                }

                ProjectTasksTab {
                    anchors.fill: parent
                    visible: detailRoot.currentTab === 1
                }

                ProjectDecisionsTab {
                    anchors.fill: parent
                    visible: detailRoot.currentTab === 2
                    onAddRequested: decisionDialog.open()
                    onEditRequested: function(item) { decisionDialog.open(item) }
                }

                ProjectNotesTab {
                    anchors.fill: parent
                    visible: detailRoot.currentTab === 3
                    onAddRequested: noteDialog.open()
                    onEditRequested: function(item) { noteDialog.open(item) }
                }

                ProjectResourcesTab {
                    anchors.fill: parent
                    visible: detailRoot.currentTab === 4
                    onAddRequested: resourceDialog.open()
                    onEditRequested: function(item) { resourceDialog.open(item) }
                }

                ProjectOutputsTab {
                    anchors.fill: parent
                    visible: detailRoot.currentTab === 5
                    onAddRequested: outputDialog.open()
                }

                ProjectActivityTab {
                    anchors.fill: parent
                    visible: detailRoot.currentTab === 6
                }
            }
        }
    }

    // Modal diyaloglar tüm ekranı kaplamak için panelin üst öğesine bağlanır.
    ProjectOutputDialog { id: outputDialog; host: detailRoot.parent ? detailRoot.parent : detailRoot }
    ProjectDecisionDialog { id: decisionDialog; host: detailRoot.parent ? detailRoot.parent : detailRoot }
    ProjectNoteDialog { id: noteDialog; host: detailRoot.parent ? detailRoot.parent : detailRoot }
    ProjectResourceDialog { id: resourceDialog; host: detailRoot.parent ? detailRoot.parent : detailRoot }
}
