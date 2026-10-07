import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../../components"
import "../../../theme"

// Özet sekmesi.
Column {
    id: root

    property var project: ({})

    spacing: 10

    Text {
        text: (root.project.problem_statement || "") !== "" ?
            "Problem: " + root.project.problem_statement :
            "Hedef Kitle: " + (root.project.target_audience || "Genel")
        font.pixelSize: 13
        color: themeBridge.textSecondary
    }

    Text {
        text: "Başlangıç: " + (root.project.start_date || "--") + "  |  Hedef: " + (root.project.target_date || "--")
        font.pixelSize: 12
        color: themeBridge.textMuted
    }
}
