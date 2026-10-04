import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../components"
import "../../theme"

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

        ScrollBar.vertical: AppScrollBar {
            id: detailScrollBar
        }

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
                color: themeBridge.surfaceAlt
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
                                themeBridge.surfaceRaised :
                                (tabMouse.containsMouse ? (themeBridge.isDark ? themeBridge.surfaceRaised : themeBridge.border) : "transparent")
                            border.width: detailRoot.currentTab === index ? 1 : 0
                            border.color: themeBridge.border

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
                height: detailRoot.currentTab === 1 ? 420 : (detailRoot.currentTab === 0 ? 120 : 280)

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
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8
                    visible: detailRoot.currentTab === 1

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: i18nBridge.tr("tab_tasks_title", "Proje Görevleri:")
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                            color: themeBridge.color("text_secondary")
                        }

                        Text {
                            text: "(" + (projectViewModel.selectedTasks ? projectViewModel.selectedTasks.length : 0) + ")"
                            font.pixelSize: 12
                            color: themeBridge.color("text_muted")
                        }

                        Item { Layout.fillWidth: true }

                        AppButton {
                            btnVariant: "secondary"
                            iconName: "external-link"
                            text: i18nBridge.tr("tab_tasks_wbs_page", "WBS Sayfasında Aç")
                            implicitHeight: 28
                            onClicked: navBridge.navigateTo("tasks")
                        }
                    }

                    // Hızlı Görev Ekleme Satırı
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        AppTextInput {
                            id: quickTaskInput
                            placeholder: i18nBridge.tr("placeholder_new_task", "Yeni görev başlığı yazın...")
                            Layout.fillWidth: true
                            inputHeight: 32
                            onAccepted: {
                                if (quickTaskInput.text.trim()) {
                                    projectViewModel.addTask(quickTaskInput.text.trim());
                                    quickTaskInput.text = "";
                                }
                            }
                        }

                        AppButton {
                            btnVariant: "primary"
                            iconName: "plus"
                            text: i18nBridge.tr("action_add", "Ekle")
                            implicitHeight: 32
                            onClicked: {
                                if (quickTaskInput.text.trim()) {
                                    projectViewModel.addTask(quickTaskInput.text.trim());
                                    quickTaskInput.text = "";
                                }
                            }
                        }
                    }

                    ListView {
                        id: projectTasksList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        spacing: 6
                        model: projectViewModel.selectedTasks

                        delegate: Rectangle {
                            width: projectTasksList.width - 4
                            height: 38
                            radius: 6
                            color: themeBridge.surfaceAlt
                            border.color: themeBridge.border
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: (modelData.parent_id > 0 ? 24 : 10)
                                anchors.rightMargin: 10
                                spacing: 8

                                // Durum Checkbox'ı
                                Rectangle {
                                    width: 18
                                    height: 18
                                    radius: 4
                                    color: modelData.is_done ? themeBridge.color("success") : "transparent"
                                    border.color: modelData.is_done ? themeBridge.color("success") : themeBridge.color("border")
                                    border.width: 1.5

                                    AppIcon {
                                        anchors.centerIn: parent
                                        name: "check"
                                        size: 12
                                        color: "#FFFFFF"
                                        visible: modelData.is_done
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: projectViewModel.toggleTaskStatus(modelData.id)
                                    }
                                }

                                // Alt görev oku
                                Text {
                                    visible: modelData.parent_id > 0
                                    text: "↳"
                                    font.pixelSize: 12
                                    color: themeBridge.color("text_muted")
                                }

                                // Görev Başlığı
                                Text {
                                    text: modelData.title
                                    font.pixelSize: 12
                                    font.strikeout: modelData.is_done
                                    font.weight: Font.Medium
                                    color: modelData.is_done ? themeBridge.color("text_muted") : themeBridge.color("text_primary")
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                // Öncelik Rozeti
                                AppBadge {
                                    visible: !!modelData.priority
                                    text: {
                                        var p = (modelData.priority || "MEDIUM").toUpperCase();
                                        switch (p) {
                                            case "URGENT": return i18nBridge.tr("priority_urgent", "Acil");
                                            case "HIGH": return i18nBridge.tr("priority_high", "Yüksek");
                                            case "MEDIUM": return i18nBridge.tr("priority_medium", "Orta");
                                            case "LOW": return i18nBridge.tr("priority_low", "Düşük");
                                            default: return p;
                                        }
                                    }
                                    variant: {
                                        var p = (modelData.priority || "MEDIUM").toUpperCase();
                                        if (p === "URGENT" || p === "HIGH") return "danger";
                                        if (p === "MEDIUM") return "warning";
                                        return "neutral";
                                    }
                                    size: "sm"
                                }

                                // Durum Rozeti
                                AppBadge {
                                    text: {
                                        var st = (modelData.status || "TODO").toUpperCase();
                                        switch (st) {
                                            case "DONE": return i18nBridge.tr("status_done", "Tamamlandı");
                                            case "IN_PROGRESS": return i18nBridge.tr("status_in_progress", "Sürüyor");
                                            case "BLOCKED": return i18nBridge.tr("status_blocked", "Engellendi");
                                            case "REVIEW": return i18nBridge.tr("status_review", "İncelemede");
                                            default: return i18nBridge.tr("status_todo", "Yapılacak");
                                        }
                                    }
                                    variant: modelData.is_done ? "success" : (modelData.status === "IN_PROGRESS" ? "info" : "secondary")
                                    size: "sm"
                                }

                                // Vade Tarihi
                                Text {
                                    visible: !!modelData.due_date
                                    text: modelData.due_date || ""
                                    font.pixelSize: 11
                                    color: themeBridge.color("text_muted")
                                }

                                // Silme Butonu
                                AppButton {
                                    iconName: "trash-2"
                                    btnVariant: "secondary"
                                    implicitWidth: 22
                                    implicitHeight: 22
                                    onClicked: projectViewModel.deleteTask(modelData.id)
                                }
                            }
                        }

                        // Boş Durum
                        Text {
                            anchors.centerIn: parent
                            visible: !projectViewModel.selectedTasks || projectViewModel.selectedTasks.length === 0
                            text: i18nBridge.tr("no_tasks", "Bu projede henüz kayıtlı görev yok.")
                            font.pixelSize: 12
                            color: themeBridge.color("text_muted")
                        }
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

    // ========================================================
    // MODAL DİYALOGLAR (Özel Modern Kart Modalları)
    // ========================================================

    // Çıktı Ekleme Dialogu
    Rectangle {
        id: addOutputDialog
        objectName: "addOutputDialog"
        parent: detailRoot.parent ? detailRoot.parent : detailRoot
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.65)
        visible: false
        z: 9999

        function open() {
            outputTitleInput.text = "";
            outputPathInput.text = "";
            visible = true;
        }

        function close() {
            visible = false;
        }

        MouseArea {
            anchors.fill: parent
            onClicked: { /* modal dışı tıklamayı engeller */ }
        }

        Shortcut {
            sequence: "Escape"
            enabled: addOutputDialog.visible
            onActivated: addOutputDialog.close()
        }

        AppCard {
            id: outputCard
            width: Math.min(480, parent.width - 48)
            height: Math.min(outputCol.implicitHeight + outputCard.padding * 2, parent.height - 48)
            anchors.centerIn: parent
            padding: Theme.spacing.xl

            ColumnLayout {
                id: outputCol
                width: parent.width
                spacing: Theme.spacing.md

                // Başlık Çubuğu
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    AppIcon {
                        name: "copy"
                        size: 20
                        color: Theme.accent(themeBridge.currentTheme)
                    }

                    Text {
                        text: i18nBridge.tr("dialog_add_output_title", "Yeni Çıktı Ekle")
                        font.pixelSize: Theme.typography.sizeH3
                        font.weight: Theme.typography.weightBold
                        color: themeBridge.color("text_primary")
                        Layout.fillWidth: true
                    }

                    AppButton {
                        iconName: "x"
                        btnVariant: "secondary"
                        implicitWidth: 32
                        implicitHeight: 32
                        onClicked: addOutputDialog.close()
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
                }

                AppTextInput {
                    id: outputTitleInput
                    label: i18nBridge.tr("field_output_title", "Çıktı Başlığı *")
                    placeholder: i18nBridge.tr("output_title_placeholder", "Rapor, doküman veya dosya adı")
                    Layout.fillWidth: true
                    showVoiceInput: true
                }

                AppTextInput {
                    id: outputPathInput
                    label: i18nBridge.tr("field_output_path", "Dosya Yolu / URL")
                    placeholder: i18nBridge.tr("output_path_placeholder", "C:/docs/rapor.pdf veya https://...")
                    Layout.fillWidth: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
                }

                // Alt Butonlar
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    Item { Layout.fillWidth: true }

                    AppButton {
                        btnVariant: "secondary"
                        text: i18nBridge.tr("btn_cancel", "İptal")
                        onClicked: addOutputDialog.close()
                    }

                    AppButton {
                        btnVariant: "primary"
                        text: i18nBridge.tr("action_add", "Ekle")
                        onClicked: {
                            if (outputTitleInput.text.trim()) {
                                projectViewModel.addOutput(outputTitleInput.text.trim(), outputPathInput.text.trim());
                                addOutputDialog.close();
                            }
                        }
                    }
                }
            }
        }
    }

    // Karar Ekleme Dialogu
    Rectangle {
        id: addDecisionDialog
        objectName: "addDecisionDialog"
        parent: detailRoot.parent ? detailRoot.parent : detailRoot
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.65)
        visible: false
        z: 9999

        function open() {
            decisionTitleInput.text = "";
            decisionTextInput.text = "";
            decisionStatusCombo.selectedValue = "APPROVED";
            visible = true;
        }

        function close() {
            visible = false;
        }

        MouseArea {
            anchors.fill: parent
            onClicked: { /* modal dışı tıklamayı engeller */ }
        }

        Shortcut {
            sequence: "Escape"
            enabled: addDecisionDialog.visible
            onActivated: addDecisionDialog.close()
        }

        AppCard {
            id: decisionCard
            width: Math.min(500, parent.width - 48)
            height: Math.min(decisionCol.implicitHeight + decisionCard.padding * 2, parent.height - 48)
            anchors.centerIn: parent
            padding: Theme.spacing.xl

            ColumnLayout {
                id: decisionCol
                width: parent.width
                spacing: Theme.spacing.md

                // Başlık Çubuğu
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    AppIcon {
                        name: "check_square"
                        size: 20
                        color: Theme.accent(themeBridge.currentTheme)
                    }

                    Text {
                        text: i18nBridge.tr("decision_dialog_new_title", "Yeni Karar Ekle")
                        font.pixelSize: Theme.typography.sizeH3
                        font.weight: Theme.typography.weightBold
                        color: themeBridge.color("text_primary")
                        Layout.fillWidth: true
                    }

                    AppButton {
                        iconName: "x"
                        btnVariant: "secondary"
                        implicitWidth: 32
                        implicitHeight: 32
                        onClicked: addDecisionDialog.close()
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
                }

                AppTextInput {
                    id: decisionTitleInput
                    label: i18nBridge.tr("decision_dialog_title_label", "Karar Konusu *")
                    placeholder: i18nBridge.tr("decision_title_placeholder", "Örn: Mimari Seçim Kararı")
                    Layout.fillWidth: true
                    showVoiceInput: true
                }

                AppTextInput {
                    id: decisionTextInput
                    label: i18nBridge.tr("decision_dialog_decision_label", "Alınan Karar *")
                    placeholder: i18nBridge.tr("decision_desc_placeholder", "Detaylı karar açıklaması...")
                    isTextArea: true
                    inputHeight: 80
                    Layout.fillWidth: true
                    showVoiceInput: true
                }

                AppComboBox {
                    id: decisionStatusCombo
                    label: i18nBridge.tr("field_status", "Durum")
                    Layout.fillWidth: true
                    model: [
                        { "text": i18nBridge.tr("decision_approved", "Onaylandı"), "value": "APPROVED" },
                        { "text": i18nBridge.tr("decision_proposed", "Önerildi"), "value": "PROPOSED" },
                        { "text": i18nBridge.tr("decision_rejected", "Reddedildi"), "value": "REJECTED" }
                    ]
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
                }

                // Alt Butonlar
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    Item { Layout.fillWidth: true }

                    AppButton {
                        btnVariant: "secondary"
                        text: i18nBridge.tr("btn_cancel", "İptal")
                        onClicked: addDecisionDialog.close()
                    }

                    AppButton {
                        btnVariant: "primary"
                        text: i18nBridge.tr("action_add", "Ekle")
                        onClicked: {
                            if (decisionTitleInput.text.trim()) {
                                var st = decisionStatusCombo.selectedValue || "APPROVED";
                                projectViewModel.createDecision(decisionTitleInput.text.trim(), decisionTextInput.text.trim(), st);
                                addDecisionDialog.close();
                            }
                        }
                    }
                }
            }
        }
    }

    // Not Ekleme Dialogu
    Rectangle {
        id: addNoteDialog
        objectName: "addNoteDialog"
        parent: detailRoot.parent ? detailRoot.parent : detailRoot
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.65)
        visible: false
        z: 9999

        function open() {
            noteTitleInput.text = "";
            noteBodyInput.text = "";
            visible = true;
        }

        function close() {
            visible = false;
        }

        MouseArea {
            anchors.fill: parent
            onClicked: { /* modal dışı tıklamayı engeller */ }
        }

        Shortcut {
            sequence: "Escape"
            enabled: addNoteDialog.visible
            onActivated: addNoteDialog.close()
        }

        AppCard {
            id: noteCard
            width: Math.min(500, parent.width - 48)
            height: Math.min(noteCol.implicitHeight + noteCard.padding * 2, parent.height - 48)
            anchors.centerIn: parent
            padding: Theme.spacing.xl

            ColumnLayout {
                id: noteCol
                width: parent.width
                spacing: Theme.spacing.md

                // Başlık Çubuğu
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    AppIcon {
                        name: "note-sticky"
                        size: 20
                        color: Theme.accent(themeBridge.currentTheme)
                    }

                    Text {
                        text: i18nBridge.tr("note_dialog_new_title", "Yeni Proje Notu Ekle")
                        font.pixelSize: Theme.typography.sizeH3
                        font.weight: Theme.typography.weightBold
                        color: themeBridge.color("text_primary")
                        Layout.fillWidth: true
                    }

                    AppButton {
                        iconName: "x"
                        btnVariant: "secondary"
                        implicitWidth: 32
                        implicitHeight: 32
                        onClicked: addNoteDialog.close()
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
                }

                AppTextInput {
                    id: noteTitleInput
                    label: i18nBridge.tr("note_dialog_title_label", "Not Başlığı *")
                    placeholder: i18nBridge.tr("note_title_placeholder", "Örn: Toplantı Notu")
                    Layout.fillWidth: true
                    showVoiceInput: true
                }

                AppTextInput {
                    id: noteBodyInput
                    label: i18nBridge.tr("note_dialog_body_label", "Not İçeriği")
                    placeholder: i18nBridge.tr("note_body_placeholder", "Not içeriği...")
                    isTextArea: true
                    inputHeight: 100
                    Layout.fillWidth: true
                    showVoiceInput: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
                }

                // Alt Butonlar
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    Item { Layout.fillWidth: true }

                    AppButton {
                        btnVariant: "secondary"
                        text: i18nBridge.tr("btn_cancel", "İptal")
                        onClicked: addNoteDialog.close()
                    }

                    AppButton {
                        btnVariant: "primary"
                        text: i18nBridge.tr("action_add", "Ekle")
                        onClicked: {
                            if (noteTitleInput.text.trim()) {
                                projectViewModel.createNote(noteTitleInput.text.trim(), noteBodyInput.text.trim());
                                addNoteDialog.close();
                            }
                        }
                    }
                }
            }
        }
    }

    // Kaynak Ekleme Dialogu
    Rectangle {
        id: addResourceDialog
        objectName: "addResourceDialog"
        parent: detailRoot.parent ? detailRoot.parent : detailRoot
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.65)
        visible: false
        z: 9999

        function open() {
            resourceTitleInput.text = "";
            resourceUrlInput.text = "";
            resourceTypeCombo.selectedValue = "DOCUMENT";
            visible = true;
        }

        function close() {
            visible = false;
        }

        MouseArea {
            anchors.fill: parent
            onClicked: { /* modal dışı tıklamayı engeller */ }
        }

        Shortcut {
            sequence: "Escape"
            enabled: addResourceDialog.visible
            onActivated: addResourceDialog.close()
        }

        AppCard {
            id: resourceCard
            width: Math.min(500, parent.width - 48)
            height: Math.min(resourceCol.implicitHeight + resourceCard.padding * 2, parent.height - 48)
            anchors.centerIn: parent
            padding: Theme.spacing.xl

            ColumnLayout {
                id: resourceCol
                width: parent.width
                spacing: Theme.spacing.md

                // Başlık Çubuğu
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    AppIcon {
                        name: "external-link"
                        size: 20
                        color: Theme.accent(themeBridge.currentTheme)
                    }

                    Text {
                        text: i18nBridge.tr("resource_dialog_new_title", "Yeni Kaynak Ekle")
                        font.pixelSize: Theme.typography.sizeH3
                        font.weight: Theme.typography.weightBold
                        color: themeBridge.color("text_primary")
                        Layout.fillWidth: true
                    }

                    AppButton {
                        iconName: "x"
                        btnVariant: "secondary"
                        implicitWidth: 32
                        implicitHeight: 32
                        onClicked: addResourceDialog.close()
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
                }

                AppTextInput {
                    id: resourceTitleInput
                    label: i18nBridge.tr("resource_dialog_title_label", "Kaynak Adı *")
                    placeholder: i18nBridge.tr("resource_title_placeholder", "Örn: API Dokümantasyonu")
                    Layout.fillWidth: true
                    showVoiceInput: true
                }

                AppTextInput {
                    id: resourceUrlInput
                    label: i18nBridge.tr("resource_dialog_url_label", "Kaynak Bağlantısı (URL / Yol) *")
                    placeholder: i18nBridge.tr("resource_url_placeholder", "https://api.example.com veya dosya yolu")
                    Layout.fillWidth: true
                }

                AppComboBox {
                    id: resourceTypeCombo
                    label: i18nBridge.tr("field_resource_type", "Kaynak Türü")
                    Layout.fillWidth: true
                    model: [
                        { "text": i18nBridge.tr("resource_type_document", "Doküman"), "value": "DOCUMENT" },
                        { "text": i18nBridge.tr("resource_type_article", "Makale"), "value": "ARTICLE" },
                        { "text": i18nBridge.tr("resource_type_video", "Video"), "value": "VIDEO" },
                        { "text": i18nBridge.tr("resource_type_repo", "GitHub / Repo"), "value": "REPO" },
                        { "text": i18nBridge.tr("resource_type_design", "Tasarım"), "value": "DESIGN" },
                        { "text": i18nBridge.tr("resource_type_api", "API Referansı"), "value": "API" },
                        { "text": i18nBridge.tr("resource_type_tool", "Araç"), "value": "TOOL" },
                        { "text": i18nBridge.tr("resource_type_other", "Diğer"), "value": "OTHER" }
                    ]
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: themeBridge.color("border")
                }

                // Alt Butonlar
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    Item { Layout.fillWidth: true }

                    AppButton {
                        btnVariant: "secondary"
                        text: i18nBridge.tr("btn_cancel", "İptal")
                        onClicked: addResourceDialog.close()
                    }

                    AppButton {
                        btnVariant: "primary"
                        text: i18nBridge.tr("action_add", "Ekle")
                        onClicked: {
                            if (resourceTitleInput.text.trim() && resourceUrlInput.text.trim()) {
                                var rType = resourceTypeCombo.selectedValue || "DOCUMENT";
                                projectViewModel.createResource(resourceTitleInput.text.trim(), resourceUrlInput.text.trim(), rType);
                                addResourceDialog.close();
                            }
                        }
                    }
                }
            }
        }
    }
}
