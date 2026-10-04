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
                    text: {
                        switch (detailRoot.p.priority) {
                            case "CRITICAL": return i18nBridge.tr("priority_critical", "Kritik");
                            case "HIGH": return i18nBridge.tr("priority_high", "Yüksek");
                            case "LOW": return i18nBridge.tr("priority_low", "Düşük");
                            default: return i18nBridge.tr("priority_medium", "Orta");
                        }
                    }
                    badgeColor: {
                        switch (detailRoot.p.priority) {
                            case "CRITICAL": return themeBridge.danger;
                            case "HIGH": return themeBridge.warning;
                            case "LOW": return themeBridge.textSecondary;
                            default: return themeBridge.accentStart;
                        }
                    }
                    anchors.verticalCenter: parent.verticalCenter
                }

                AppBadge {
                    visible: (detailRoot.p.health || "") !== ""
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
                    visible: (detailRoot.p.project_type || "") !== ""
                    text: {
                        var pt = (detailRoot.p.project_type || "").toUpperCase();
                        switch (pt) {
                            case "SOFTWARE": case "YAZILIM": return i18nBridge.tr("project_type_software", "Yazılım");
                            case "EDUCATION": case "EGITIM": case "EĞİTİM": return i18nBridge.tr("project_type_education", "Eğitim");
                            case "RESEARCH": case "ARASTIRMA": case "ARAŞTIRMA": return i18nBridge.tr("project_type_research", "Araştırma");
                            case "DESIGN": case "TASARIM": return i18nBridge.tr("project_type_design", "Tasarım");
                            case "INTERNAL": case "IC ARAC": case "İÇ ARAÇ": return i18nBridge.tr("project_type_internal", "İç Araç");
                            case "CLIENT": case "MUSTERI": case "MÜŞTERİ İŞİ": return i18nBridge.tr("project_type_client", "Müşteri İşi");
                            case "EXPERIMENTAL": case "DENEYSEL": return i18nBridge.tr("project_type_experimental", "Deneysel");
                            case "WEB": return "Web";
                            case "MOBILE": return "Mobil";
                            case "DESKTOP": return "Masaüstü";
                            case "CLI": return "Komut Satırı";
                            case "OTHER": case "DIGER": case "DİĞER": return i18nBridge.tr("project_type_other", "Diğer");
                            default: return detailRoot.p.project_type || "";
                        }
                    }
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

            // Süreç Aşamaları (Açılır Kapanır Liste / Accordion)
            AppCard {
                id: stagesCard
                width: parent.width - 48
                height: stagesContentColumn.implicitHeight + 32
                clip: true

                property bool stagesExpanded: true

                Column {
                    id: stagesContentColumn
                    anchors.fill: parent
                    spacing: 12

                    // Tıklanabilir Açılır / Kapanır Başlık Satırı
                    Rectangle {
                        width: parent.width
                        height: 32
                        color: "transparent"

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: stagesCard.stagesExpanded = !stagesCard.stagesExpanded
                        }

                        RowLayout {
                            anchors.fill: parent
                            spacing: 8

                            AppIcon {
                                name: stagesCard.stagesExpanded ? "chevron-down" : "chevron-right"
                                size: 16
                                color: themeBridge.accentStart
                                Layout.alignment: Qt.AlignVCenter
                            }

                            Text {
                                text: i18nBridge.tr("section_stages", "SÜREÇ AŞAMALARI")
                                font.pixelSize: 13
                                font.weight: Font.DemiBold
                                color: themeBridge.textPrimary
                                Layout.alignment: Qt.AlignVCenter
                            }

                            // Tamamlanan Aşama Sayacı
                            Text {
                                text: {
                                    var list = projectViewModel.selectedStages || [];
                                    var doneCount = 0;
                                    for (var i = 0; i < list.length; i++) {
                                        if (list[i].status === "DONE" || list[i].status === "COMPLETED") {
                                            doneCount++;
                                        }
                                    }
                                    return "(" + doneCount + "/" + list.length + " " + i18nBridge.tr("status_completed", "Tamamlandı") + ")";
                                }
                                font.pixelSize: 12
                                color: themeBridge.textMuted
                                Layout.alignment: Qt.AlignVCenter
                            }

                            Item { Layout.fillWidth: true }

                            Text {
                                text: stagesCard.stagesExpanded ? i18nBridge.tr("action_collapse", "Daralt") : i18nBridge.tr("action_expand", "Genişlet")
                                font.pixelSize: 11
                                color: themeBridge.accentStart
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }
                    }

                    // Aşamalar Listesi (Açıkken Görünür)
                    Column {
                        id: stagesListColumn
                        width: parent.width
                        spacing: 10
                        visible: stagesCard.stagesExpanded

                        Repeater {
                            model: projectViewModel.selectedStages
                            delegate: RowLayout {
                                width: stagesListColumn.width
                                height: 36
                                spacing: 12

                                Rectangle {
                                    width: 10
                                    height: 10
                                    radius: 5
                                    color: (modelData.status === "DONE" || modelData.status === "COMPLETED") ? themeBridge.success : (
                                        (modelData.status === "ACTIVE" || modelData.status === "IN_PROGRESS") ? themeBridge.accentStart : themeBridge.border
                                    )
                                    Layout.alignment: Qt.AlignVCenter
                                }

                                Text {
                                    text: (index + 1) + ". " + modelData.name
                                    font.pixelSize: 13
                                    font.weight: (modelData.status === "ACTIVE" || modelData.status === "IN_PROGRESS") ? Font.DemiBold : Font.Normal
                                    color: (modelData.status === "DONE" || modelData.status === "COMPLETED") ? themeBridge.textMuted : themeBridge.textPrimary
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                    Layout.alignment: Qt.AlignVCenter
                                }

                                AppBadge {
                                    text: {
                                        var st = modelData.status;
                                        if (st === "DONE" || st === "COMPLETED") return i18nBridge.tr("status_completed", "Tamamlandı");
                                        if (st === "ACTIVE" || st === "IN_PROGRESS") return i18nBridge.tr("status_active", "Aktif");
                                        if (st === "SKIPPED") return i18nBridge.tr("status_skipped", "Atlandı");
                                        return i18nBridge.tr("status_not_started", "Başlamadı");
                                    }
                                    variant: {
                                        var st = modelData.status;
                                        if (st === "DONE" || st === "COMPLETED") return "success";
                                        if (st === "ACTIVE" || st === "IN_PROGRESS") return "info";
                                        return "neutral";
                                    }
                                    size: "sm"
                                    Layout.alignment: Qt.AlignVCenter
                                }

                                AppButton {
                                    visible: modelData.status !== "COMPLETED" && modelData.status !== "DONE"
                                    variant: "secondary"
                                    text: i18nBridge.tr("btn_complete_stage", "Tamamla")
                                    implicitHeight: 28
                                    onClicked: projectViewModel.completeStage(modelData.id)
                                    Layout.alignment: Qt.AlignVCenter
                                }

                                AppButton {
                                    visible: modelData.status === "NOT_STARTED"
                                    variant: "primary"
                                    text: i18nBridge.tr("btn_activate_stage", "Aktif Et")
                                    implicitHeight: 28
                                    onClicked: projectViewModel.activateStage(modelData.id)
                                    Layout.alignment: Qt.AlignVCenter
                                }
                            }
                        }
                    }
                }
            }

            // Sekme Çubuğu (Segmented Tabs)
            Rectangle {
                width: parent.width - 48
                height: 40
                radius: 8
                color: themeBridge.isDark ? themeBridge.surface : "#F1F5F9"
                border.width: 1
                border.color: themeBridge.border

                Row {
                    anchors.centerIn: parent
                    spacing: 4

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
                            id: tabBtn
                            width: Math.max(76, tabText.implicitWidth + 24)
                            height: 32
                            radius: 6
                            color: detailRoot.currentTab === index ?
                                (themeBridge.isDark ? themeBridge.surfaceRaised : "#FFFFFF") :
                                (tabMouse.containsMouse ? (themeBridge.isDark ? themeBridge.surfaceRaised : "#E2E8F0") : "transparent")
                            border.width: detailRoot.currentTab === index ? 1 : 0
                            border.color: themeBridge.isDark ? themeBridge.border : "#CBD5E1"

                            Text {
                                id: tabText
                                anchors.centerIn: parent
                                text: modelData
                                font.pixelSize: 12
                                font.weight: detailRoot.currentTab === index ? Font.DemiBold : Font.Normal
                                color: detailRoot.currentTab === index ? themeBridge.accentStart : themeBridge.textSecondary
                            }

                            MouseArea {
                                id: tabMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: detailRoot.currentTab = index
                            }
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
                            iconName: "plus"
                            text: i18nBridge.tr("action_add_decision", "Karar Ekle")
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
                                            text: {
                                                var st = (modelData.status || "APPROVED").toUpperCase();
                                                switch (st) {
                                                    case "APPROVED": case "ONAYLANDI": return i18nBridge.tr("decision_approved", "Onaylandı");
                                                    case "REJECTED": case "REDDEDILDI": case "REDDEDİLDİ": return i18nBridge.tr("decision_rejected", "Reddedildi");
                                                    case "PROPOSED": case "ONERILDI": case "ÖNERİLDİ": return i18nBridge.tr("decision_proposed", "Önerildi");
                                                    default: return modelData.status;
                                                }
                                            }
                                            variant: (modelData.status === "REJECTED" || modelData.status === "REDDEDILDI") ? "danger" : "success"
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
                            iconName: "plus"
                            text: i18nBridge.tr("action_add_note", "Not Ekle")
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
                            iconName: "plus"
                            text: i18nBridge.tr("action_add_resource", "Kaynak Ekle")
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
                                            text: {
                                                var rt = (modelData.resource_type || "DOCUMENT").toUpperCase();
                                                switch (rt) {
                                                    case "DOCUMENT": return i18nBridge.tr("resource_type_document", "Doküman");
                                                    case "ARTICLE": return i18nBridge.tr("resource_type_article", "Makale");
                                                    case "VIDEO": return i18nBridge.tr("resource_type_video", "Video");
                                                    case "GITHUB": case "REPO": return i18nBridge.tr("resource_type_github", "GitHub / Repo");
                                                    case "DESIGN": return i18nBridge.tr("resource_type_design", "Tasarım");
                                                    case "API": return i18nBridge.tr("resource_type_api", "API Referansı");
                                                    case "TOOL": return i18nBridge.tr("resource_type_tool", "Araç");
                                                    case "OTHER": return i18nBridge.tr("resource_type_other", "Diğer");
                                                    default: return modelData.resource_type;
                                                }
                                            }
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
                            iconName: "plus"
                            text: i18nBridge.tr("action_add_output", "Çıktı Ekle")
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
        title: i18nBridge.tr("dialog_add_output_title", "Yeni Çıktı Ekle")
        modal: true

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
                label: i18nBridge.tr("field_output_title", "Çıktı Başlığı *")
                placeholder: i18nBridge.tr("output_title_placeholder", "Rapor, doküman veya dosya adı")
                Layout.fillWidth: true
            }

            AppTextInput {
                id: outputPathInput
                label: i18nBridge.tr("field_output_path", "Dosya Yolu / URL")
                placeholder: "C:/docs/rapor.pdf veya https://..."
                Layout.fillWidth: true
            }
        }

        footer: RowLayout {
            width: parent.width
            Item { Layout.fillWidth: true }
            AppButton {
                btnVariant: "secondary"
                text: i18nBridge.tr("action_cancel", "İptal")
                onClicked: addOutputDialog.close()
            }
            AppButton {
                btnVariant: "primary"
                text: i18nBridge.tr("action_add", "Ekle")
                onClicked: {
                    if (outputTitleInput.text) {
                        projectViewModel.addOutput(outputTitleInput.text, outputPathInput.text);
                        outputTitleInput.text = "";
                        outputPathInput.text = "";
                        addOutputDialog.close();
                    }
                }
            }
        }
    }

    // Karar Ekleme Dialogu
    Dialog {
        id: addDecisionDialog
        anchors.centerIn: parent
        width: 420
        title: i18nBridge.tr("decision_dialog_new_title", "Yeni Karar Ekle")
        modal: true

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
                label: i18nBridge.tr("decision_dialog_title_label", "Karar Konusu *")
                placeholder: i18nBridge.tr("decision_title_placeholder", "Örn: Mimari Seçim Kararı")
                Layout.fillWidth: true
            }

            AppTextInput {
                id: decisionTextInput
                label: i18nBridge.tr("decision_dialog_decision_label", "Alınan Karar *")
                placeholder: i18nBridge.tr("decision_desc_placeholder", "Detaylı karar açıklaması...")
                isTextArea: true
                Layout.fillWidth: true
            }
        }

        footer: RowLayout {
            width: parent.width
            Item { Layout.fillWidth: true }
            AppButton {
                btnVariant: "secondary"
                text: i18nBridge.tr("action_cancel", "İptal")
                onClicked: addDecisionDialog.close()
            }
            AppButton {
                btnVariant: "primary"
                text: i18nBridge.tr("action_add", "Ekle")
                onClicked: {
                    if (decisionTitleInput.text && decisionTextInput.text) {
                        projectViewModel.createDecision(decisionTitleInput.text, decisionTextInput.text, "APPROVED");
                        decisionTitleInput.text = "";
                        decisionTextInput.text = "";
                        addDecisionDialog.close();
                    }
                }
            }
        }
    }

    // Not Ekleme Dialogu
    Dialog {
        id: addNoteDialog
        anchors.centerIn: parent
        width: 420
        title: i18nBridge.tr("note_dialog_new_title", "Yeni Proje Notu Ekle")
        modal: true

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
                label: i18nBridge.tr("note_dialog_title_label", "Not Başlığı *")
                placeholder: i18nBridge.tr("note_title_placeholder", "Örn: Toplantı Notu")
                Layout.fillWidth: true
            }

            AppTextInput {
                id: noteBodyInput
                label: i18nBridge.tr("note_dialog_body_label", "Not İçeriği")
                placeholder: i18nBridge.tr("note_body_placeholder", "Not içeriği...")
                isTextArea: true
                Layout.fillWidth: true
            }
        }

        footer: RowLayout {
            width: parent.width
            Item { Layout.fillWidth: true }
            AppButton {
                btnVariant: "secondary"
                text: i18nBridge.tr("action_cancel", "İptal")
                onClicked: addNoteDialog.close()
            }
            AppButton {
                btnVariant: "primary"
                text: i18nBridge.tr("action_add", "Ekle")
                onClicked: {
                    if (noteTitleInput.text) {
                        projectViewModel.createNote(noteTitleInput.text, noteBodyInput.text);
                        noteTitleInput.text = "";
                        noteBodyInput.text = "";
                        addNoteDialog.close();
                    }
                }
            }
        }
    }

    // Kaynak Ekleme Dialogu
    Dialog {
        id: addResourceDialog
        anchors.centerIn: parent
        width: 420
        title: i18nBridge.tr("resource_dialog_new_title", "Yeni Kaynak Ekle")
        modal: true

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
                label: i18nBridge.tr("resource_dialog_title_label", "Kaynak Adı *")
                placeholder: i18nBridge.tr("resource_title_placeholder", "Örn: API Dokümantasyonu")
                Layout.fillWidth: true
            }

            AppTextInput {
                id: resourceUrlInput
                label: i18nBridge.tr("resource_dialog_url_label", "Kaynak Bağlantısı (URL / Yol) *")
                placeholder: "https://api.example.com veya dosya yolu"
                Layout.fillWidth: true
            }
        }

        footer: RowLayout {
            width: parent.width
            Item { Layout.fillWidth: true }
            AppButton {
                btnVariant: "secondary"
                text: i18nBridge.tr("action_cancel", "İptal")
                onClicked: addResourceDialog.close()
            }
            AppButton {
                btnVariant: "primary"
                text: i18nBridge.tr("action_add", "Ekle")
                onClicked: {
                    if (resourceTitleInput.text && resourceUrlInput.text) {
                        projectViewModel.createResource(resourceTitleInput.text, resourceUrlInput.text, "DOCUMENT");
                        resourceTitleInput.text = "";
                        resourceUrlInput.text = "";
                        addResourceDialog.close();
                    }
                }
            }
        }
    }
}
