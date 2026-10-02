import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../components"

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
    ScrollView {
        id: detailScroll
        anchors.fill: parent
        visible: detailRoot.hasProject
        contentWidth: availableWidth
        clip: true

        Column {
            width: parent.width
            padding: 24
            spacing: 16

            // Üst Başlık ve Eylemler Satırı
            Row {
                width: parent.width - 48
                spacing: 16

                Text {
                    width: parent.width - actionsRow.width - 16
                    text: detailRoot.p.title || ""
                    font.pixelSize: 20
                    font.weight: Font.Bold
                    color: themeBridge.textPrimary
                    wrapMode: Text.Wrap
                    anchors.verticalCenter: parent.verticalCenter
                }

                Row {
                    id: actionsRow
                    spacing: 8
                    anchors.verticalCenter: parent.verticalCenter

                    AppButton {
                        variant: "primary"
                        text: i18nBridge.tr("action_edit", "Düzenle")
                        iconName: "pencil"
                        onClicked: projectViewModel.openEditDialog(detailRoot.p.id)
                    }

                    AppButton {
                        variant: "secondary"
                        text: detailRoot.p.is_archived ? i18nBridge.tr("action_restore", "Geri Yükle") : i18nBridge.tr("action_archive", "Arşivle")
                        iconName: "archive"
                        onClicked: {
                            if (detailRoot.p.is_archived) {
                                projectViewModel.restoreProject(detailRoot.p.id);
                            } else {
                                projectViewModel.archiveProject(detailRoot.p.id);
                            }
                        }
                    }

                    AppButton {
                        variant: "danger"
                        text: i18nBridge.tr("action_delete", "Sil")
                        iconName: "trash"
                        onClicked: projectViewModel.deleteProject(detailRoot.p.id)
                    }
                }
            }

            // Rozetler Satırı
            Row {
                width: parent.width - 48
                spacing: 10

                StatusIndicator {
                    status: detailRoot.p.status || "PLANNED"
                    anchors.verticalCenter: parent.verticalCenter
                }

                AppBadge {
                    text: detailRoot.p.priority || "MEDIUM"
                    badgeColor: themeBridge.accentStart
                    anchors.verticalCenter: parent.verticalCenter
                }

                AppBadge {
                    visible: detailRoot.p.health !== ""
                    text: {
                        switch (detailRoot.p.health) {
                            case "GOOD": return i18nBridge.tr("health_good", "Yolunda");
                            case "AT_RISK": return i18nBridge.tr("health_at_risk", "Riskli");
                            case "BLOCKED": return i18nBridge.tr("health_blocked", "Tıkandı");
                            default: return i18nBridge.tr("health_unknown", "Belirsiz");
                        }
                    }
                    badgeColor: detailRoot.p.health === "GOOD" ? themeBridge.success : (
                        detailRoot.p.health === "AT_RISK" ? themeBridge.warning : themeBridge.danger
                    )
                    anchors.verticalCenter: parent.verticalCenter
                }

                AppBadge {
                    visible: detailRoot.p.project_type !== ""
                    text: detailRoot.p.project_type || ""
                    badgeColor: themeBridge.textSecondary
                    anchors.verticalCenter: parent.verticalCenter
                }

                Item { width: 1; height: 1; Layout.fillWidth: true }

                AppProgressBar {
                    value: detailRoot.p.progress || 0
                    showLabel: true
                    barHeight: 6
                    implicitWidth: 100
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            // Açıklama
            AppCard {
                width: parent.width - 48
                height: Math.max(70, descText.implicitHeight + 32)
                visible: (detailRoot.p.description || "") !== ""

                Column {
                    anchors.fill: parent
                    spacing: 4

                    Text {
                        text: i18nBridge.tr("section_description", "AÇIKLAMA")
                        font.pixelSize: 11
                        font.weight: Font.DemiBold
                        color: themeBridge.textMuted
                    }

                    Text {
                        id: descText
                        text: detailRoot.p.description || ""
                        font.pixelSize: 13
                        color: themeBridge.textSecondary
                        wrapMode: Text.Wrap
                        width: parent.width
                    }
                }
            }

            // Bağlantılar (GitHub / Klasör)
            Row {
                width: parent.width - 48
                spacing: 12
                visible: (detailRoot.p.github_repo || "") !== "" || (detailRoot.p.local_path || "") !== ""

                AppButton {
                    visible: (detailRoot.p.github_repo || "") !== ""
                    variant: "secondary"
                    text: "GitHub Deposu"
                    iconName: "external-link"
                    onClicked: projectViewModel.openUrlOrPath(detailRoot.p.github_repo)
                }

                AppButton {
                    visible: (detailRoot.p.local_path || "") !== ""
                    variant: "secondary"
                    text: "Yerel Klasör"
                    iconName: "folder"
                    onClicked: projectViewModel.openUrlOrPath(detailRoot.p.local_path)
                }
            }

            // Süreç Aşamaları (Timeline)
            AppCard {
                width: parent.width - 48
                height: stagesColumn.implicitHeight + 32

                Column {
                    id: stagesColumn
                    anchors.fill: parent
                    spacing: 12

                    Text {
                        text: i18nBridge.tr("section_stages", "SÜREÇ AŞAMALARI")
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        color: themeBridge.textPrimary
                    }

                    // Aşamalar Listesi
                    Repeater {
                        model: projectViewModel.selectedStages
                        delegate: Row {
                            width: stagesColumn.width
                            height: 32
                            spacing: 10

                            Rectangle {
                                width: 10
                                height: 10
                                radius: 5
                                color: modelData.status === "COMPLETED" ? themeBridge.success : (
                                    modelData.status === "IN_PROGRESS" ? themeBridge.accentStart : themeBridge.border
                                )
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: (index + 1) + ". " + modelData.name
                                font.pixelSize: 13
                                font.weight: modelData.status === "IN_PROGRESS" ? Font.Bold : Font.Normal
                                color: modelData.status === "COMPLETED" ? themeBridge.textMuted : themeBridge.textPrimary
                                anchors.verticalCenter: parent.verticalCenter
                                width: parent.width - 160
                                elide: Text.ElideRight
                            }

                            Item { width: 1; height: 1; Layout.fillWidth: true }

                            AppButton {
                                visible: modelData.status !== "COMPLETED"
                                variant: "ghost"
                                text: i18nBridge.tr("btn_complete_stage", "Tamamla")
                                implicitHeight: 26
                                onClicked: projectViewModel.completeStage(modelData.id)
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            AppButton {
                                visible: modelData.status === "NOT_STARTED"
                                variant: "ghost"
                                text: i18nBridge.tr("btn_activate_stage", "Aktif Et")
                                implicitHeight: 26
                                onClicked: projectViewModel.activateStage(modelData.id)
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }
            }

            // Sekme Çubuğu (Navbar Tabs)
            Row {
                width: parent.width - 48
                spacing: 8

                Repeater {
                    model: [
                        i18nBridge.tr("tab_summary", "Özet"),
                        i18nBridge.tr("tab_tasks", "Görevler"),
                        i18nBridge.tr("tab_decisions", "Kararlar"),
                        i18nBridge.tr("tab_notes", "Notlar"),
                        i18nBridge.tr("tab_resources", "Kaynaklar"),
                        i18nBridge.tr("tab_outputs", "Çıktılar")
                    ]

                    Rectangle {
                        width: Math.max(70, tabText.implicitWidth + 20)
                        height: 32
                        radius: 6
                        color: detailRoot.currentTab === index ? themeBridge.surfaceRaised : "transparent"
                        border.width: detailRoot.currentTab === index ? 1 : 0
                        border.color: themeBridge.accentStart

                        Text {
                            id: tabText
                            anchors.centerIn: parent
                            text: modelData
                            font.pixelSize: 12
                            font.weight: detailRoot.currentTab === index ? Font.DemiBold : Font.Normal
                            color: detailRoot.currentTab === index ? themeBridge.textPrimary : themeBridge.textSecondary
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: detailRoot.currentTab = index
                        }
                    }
                }
            }

            // Sekme İçerikleri
            AppCard {
                width: parent.width - 48
                height: 180

                // Tab 0: Özet
                Column {
                    anchors.fill: parent
                    spacing: 10
                    visible: detailRoot.currentTab === 0

                    Text {
                        text: (detailRoot.p.problem_statement || "") !== "" ?
                            "Problem: " + detailRoot.p.problem_statement :
                            "Hedef Kitle: " + (detailRoot.p.target_audience || "Genel")
                        font.pixelSize: 13
                        color: themeBridge.textSecondary
                    }

                    Text {
                        text: "Başlangıç: " + (detailRoot.p.start_date || "--") + "  |  Hedef: " + (detailRoot.p.target_date || "--")
                        font.pixelSize: 12
                        color: themeBridge.textMuted
                    }
                }

                // Tab 1: Görevler
                Column {
                    anchors.fill: parent
                    spacing: 12
                    visible: detailRoot.currentTab === 1

                    Text {
                        text: "Proje Görevleri WBS modülünden yönetilmektedir."
                        font.pixelSize: 13
                        color: themeBridge.textSecondary
                    }

                    AppButton {
                        variant: "secondary"
                        text: "Görevler Sayfasına Git"
                        iconName: "square-check"
                        onClicked: navBridge.navigateTo("tasks")
                    }
                }

                // Tab 2: Kararlar
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8
                    visible: detailRoot.currentTab === 2

                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: i18nBridge.tr("tab_decisions", "Proje Kararları:")
                            font.pixelSize: 13
                            color: themeBridge.color("text_secondary")
                            Layout.fillWidth: true
                        }

                        AppButton {
                            btnVariant: "primary"
                            text: "+ " + i18nBridge.tr("action_add_decision", "Karar Ekle")
                            implicitHeight: 28
                            onClicked: addDecisionDialog.open()
                        }
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        ColumnLayout {
                            width: parent.width - 12
                            spacing: 6

                            Repeater {
                                model: projectViewModel.selectedDecisions
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 36
                                    radius: 6
                                    color: themeBridge.color("surface_alt")
                                    border.color: themeBridge.color("border")

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 6
                                        spacing: 8

                                        AppBadge {
                                            text: modelData.status || "APPROVED"
                                            variant: modelData.status === "REJECTED" ? "danger" : "success"
                                            size: "sm"
                                        }

                                        Text {
                                            text: modelData.title
                                            font.pixelSize: 12
                                            font.weight: Font.DemiBold
                                            color: themeBridge.color("text_primary")
                                        }

                                        Text {
                                            text: "— " + modelData.decision
                                            font.pixelSize: 12
                                            color: themeBridge.color("text_secondary")
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }

                                        AppButton {
                                            iconName: "trash-2"
                                            btnVariant: "secondary"
                                            implicitWidth: 22
                                            implicitHeight: 22
                                            onClicked: projectViewModel.deleteDecision(modelData.id)
                                        }
                                    }
                                }
                            }

                            Text {
                                visible: !projectViewModel.selectedDecisions || projectViewModel.selectedDecisions.length === 0
                                text: i18nBridge.tr("no_decisions", "Henüz kayıtlı karar yok.")
                                font.pixelSize: 12
                                color: themeBridge.color("text_muted")
                            }
                        }
                    }
                }

                // Tab 3: Notlar
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8
                    visible: detailRoot.currentTab === 3

                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: i18nBridge.tr("tab_notes", "Proje Notları:")
                            font.pixelSize: 13
                            color: themeBridge.color("text_secondary")
                            Layout.fillWidth: true
                        }

                        AppButton {
                            btnVariant: "primary"
                            text: "+ " + i18nBridge.tr("action_add_note", "Not Ekle")
                            implicitHeight: 28
                            onClicked: addNoteDialog.open()
                        }
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        ColumnLayout {
                            width: parent.width - 12
                            spacing: 6

                            Repeater {
                                model: projectViewModel.selectedNotes
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 36
                                    radius: 6
                                    color: themeBridge.color("surface_alt")
                                    border.color: themeBridge.color("border")

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 6
                                        spacing: 8

                                        Text {
                                            text: modelData.title
                                            font.pixelSize: 12
                                            font.weight: Font.DemiBold
                                            color: themeBridge.color("text_primary")
                                        }

                                        Text {
                                            text: "— " + modelData.body
                                            font.pixelSize: 12
                                            color: themeBridge.color("text_secondary")
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }

                                        AppButton {
                                            iconName: "trash-2"
                                            btnVariant: "secondary"
                                            implicitWidth: 22
                                            implicitHeight: 22
                                            onClicked: projectViewModel.deleteNote(modelData.id)
                                        }
                                    }
                                }
                            }

                            Text {
                                visible: !projectViewModel.selectedNotes || projectViewModel.selectedNotes.length === 0
                                text: i18nBridge.tr("no_notes", "Henüz kayıtlı proje notu yok.")
                                font.pixelSize: 12
                                color: themeBridge.color("text_muted")
                            }
                        }
                    }
                }

                // Tab 4: Kaynaklar
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8
                    visible: detailRoot.currentTab === 4

                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: i18nBridge.tr("tab_resources", "Proje Kaynakları:")
                            font.pixelSize: 13
                            color: themeBridge.color("text_secondary")
                            Layout.fillWidth: true
                        }

                        AppButton {
                            btnVariant: "primary"
                            text: "+ " + i18nBridge.tr("action_add_resource", "Kaynak Ekle")
                            implicitHeight: 28
                            onClicked: addResourceDialog.open()
                        }
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        ColumnLayout {
                            width: parent.width - 12
                            spacing: 6

                            Repeater {
                                model: projectViewModel.selectedResources
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 36
                                    radius: 6
                                    color: themeBridge.color("surface_alt")
                                    border.color: themeBridge.color("border")

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 6
                                        spacing: 8

                                        AppBadge {
                                            text: modelData.resource_type || "DOCUMENT"
                                            variant: "neutral"
                                            size: "sm"
                                        }

                                        Text {
                                            text: modelData.title
                                            font.pixelSize: 12
                                            font.weight: Font.DemiBold
                                            color: themeBridge.color("text_primary")
                                        }

                                        Text {
                                            text: "(" + modelData.url + ")"
                                            font.pixelSize: 11
                                            color: Theme.accent(themeBridge.currentTheme)
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }

                                        AppButton {
                                            iconName: "external-link"
                                            btnVariant: "secondary"
                                            implicitWidth: 22
                                            implicitHeight: 22
                                            onClicked: projectViewModel.openUrlOrPath(modelData.url)
                                        }

                                        AppButton {
                                            iconName: "trash-2"
                                            btnVariant: "secondary"
                                            implicitWidth: 22
                                            implicitHeight: 22
                                            onClicked: projectViewModel.deleteResource(modelData.id)
                                        }
                                    }
                                }
                            }

                            Text {
                                visible: !projectViewModel.selectedResources || projectViewModel.selectedResources.length === 0
                                text: i18nBridge.tr("no_resources", "Henüz kayıtlı kaynak yok.")
                                font.pixelSize: 12
                                color: themeBridge.color("text_muted")
                            }
                        }
                    }
                }

                // Tab 5: Çıktılar
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8
                    visible: detailRoot.currentTab === 5

                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: i18nBridge.tr("tab_outputs", "Proje Çıktıları ve Ekleri:")
                            font.pixelSize: 13
                            color: themeBridge.color("text_secondary")
                            Layout.fillWidth: true
                        }

                        AppButton {
                            btnVariant: "primary"
                            text: "+ " + i18nBridge.tr("action_add_output", "Çıktı Ekle")
                            implicitHeight: 28
                            onClicked: addOutputDialog.open()
                        }
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        ColumnLayout {
                            width: parent.width - 12
                            spacing: 6

                            Repeater {
                                model: projectViewModel.selectedOutputs
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    implicitHeight: 36
                                    radius: 6
                                    color: themeBridge.color("surface_alt")
                                    border.color: themeBridge.color("border")

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 6
                                        spacing: 8

                                        Text {
                                            text: "📎 " + modelData.title
                                            font.pixelSize: 12
                                            font.weight: Font.DemiBold
                                            color: themeBridge.color("text_primary")
                                        }

                                        Text {
                                            text: "(" + modelData.file_path + ")"
                                            font.pixelSize: 11
                                            color: themeBridge.color("text_muted")
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }

                                        AppButton {
                                            iconName: "external-link"
                                            btnVariant: "secondary"
                                            implicitWidth: 22
                                            implicitHeight: 22
                                            onClicked: projectViewModel.openUrlOrPath(modelData.file_path)
                                        }
                                    }
                                }
                            }

                            Text {
                                visible: !projectViewModel.selectedOutputs || projectViewModel.selectedOutputs.length === 0
                                text: i18nBridge.tr("no_outputs", "Henüz kayıtlı çıktı yok.")
                                font.pixelSize: 12
                                color: themeBridge.color("text_muted")
                            }
                        }
                    }
                }
            }
        }
    }

    // Çıktı Ekleme Dialogu
    Dialog {
        id: addOutputDialog
        anchors.centerIn: parent
        width: 380
        title: "Yeni Çıktı Ekle"
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel

        background: Rectangle {
            radius: 12
            color: themeBridge.color("surface")
            border.width: 1
            border.color: themeBridge.color("border")
        }

        ColumnLayout {
            width: parent.width
            spacing: 12

            AppTextInput {
                id: outputTitleInput
                label: "Çıktı Başlığı"
                placeholder: "Rapor, doküman veya dosya adı"
                Layout.fillWidth: true
            }

            AppTextInput {
                id: outputPathInput
                label: "Dosya Yolu / URL"
                placeholder: "C:/docs/rapor.pdf veya https://..."
                Layout.fillWidth: true
            }
        }

        onAccepted: {
            if (outputTitleInput.text) {
                projectViewModel.addOutput(outputTitleInput.text, outputPathInput.text);
                outputTitleInput.text = "";
                outputPathInput.text = "";
            }
        }
    }

    // Karar Ekleme Dialogu
    Dialog {
        id: addDecisionDialog
        anchors.centerIn: parent
        width: 420
        title: "Yeni Karar Ekle"
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel

        background: Rectangle {
            radius: 12
            color: themeBridge.color("surface")
            border.width: 1
            border.color: themeBridge.color("border")
        }

        ColumnLayout {
            width: parent.width
            spacing: 12

            AppTextInput {
                id: decisionTitleInput
                label: "Karar Konusu *"
                placeholder: "Örn: Mimari Seçim Kararı"
                Layout.fillWidth: true
            }

            AppTextInput {
                id: decisionTextInput
                label: "Alınan Karar *"
                placeholder: "Detaylı karar açıklaması..."
                isTextArea: true
                Layout.fillWidth: true
            }
        }

        onAccepted: {
            if (decisionTitleInput.text && decisionTextInput.text) {
                projectViewModel.createDecision(decisionTitleInput.text, decisionTextInput.text, "APPROVED");
                decisionTitleInput.text = "";
                decisionTextInput.text = "";
            }
        }
    }

    // Not Ekleme Dialogu
    Dialog {
        id: addNoteDialog
        anchors.centerIn: parent
        width: 420
        title: "Yeni Proje Notu Ekle"
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel

        background: Rectangle {
            radius: 12
            color: themeBridge.color("surface")
            border.width: 1
            border.color: themeBridge.color("border")
        }

        ColumnLayout {
            width: parent.width
            spacing: 12

            AppTextInput {
                id: noteTitleInput
                label: "Not Başlığı *"
                placeholder: "Örn: Toplantı Notu"
                Layout.fillWidth: true
            }

            AppTextInput {
                id: noteBodyInput
                label: "Not İçeriği"
                placeholder: "Not içeriği..."
                isTextArea: true
                Layout.fillWidth: true
            }
        }

        onAccepted: {
            if (noteTitleInput.text) {
                projectViewModel.createNote(noteTitleInput.text, noteBodyInput.text);
                noteTitleInput.text = "";
                noteBodyInput.text = "";
            }
        }
    }

    // Kaynak Ekleme Dialogu
    Dialog {
        id: addResourceDialog
        anchors.centerIn: parent
        width: 420
        title: "Yeni Kaynak Ekle"
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel

        background: Rectangle {
            radius: 12
            color: themeBridge.color("surface")
            border.width: 1
            border.color: themeBridge.color("border")
        }

        ColumnLayout {
            width: parent.width
            spacing: 12

            AppTextInput {
                id: resourceTitleInput
                label: "Kaynak Adı *"
                placeholder: "Örn: API Dokümantasyonu"
                Layout.fillWidth: true
            }

            AppTextInput {
                id: resourceUrlInput
                label: "Kaynak Bağlantısı (URL / Yol) *"
                placeholder: "https://api.example.com veya dosya yolu"
                Layout.fillWidth: true
            }
        }

        onAccepted: {
            if (resourceTitleInput.text && resourceUrlInput.text) {
                projectViewModel.createResource(resourceTitleInput.text, resourceUrlInput.text, "DOCUMENT");
                resourceTitleInput.text = "";
                resourceUrlInput.text = "";
            }
        }
    }
}
