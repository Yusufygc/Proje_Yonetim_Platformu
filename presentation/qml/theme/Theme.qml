import QtQuick 2.15

QtObject {
    id: themeRoot

    // Renkler — themeBridge üzerinden reaktif
    readonly property color background: themeBridge.background
    readonly property color surface: themeBridge.surface
    readonly property color surfaceRaised: themeBridge.surfaceRaised
    readonly property color textPrimary: themeBridge.textPrimary
    readonly property color textSecondary: themeBridge.textSecondary
    readonly property color textMuted: themeBridge.textMuted
    readonly property color accentStart: themeBridge.accentStart
    readonly property color accentEnd: themeBridge.accentEnd
    readonly property color border: themeBridge.border
    readonly property color sidebarBg: themeBridge.sidebarBg
    readonly property color sidebarActive: themeBridge.sidebarActive
    readonly property color sidebarText: themeBridge.sidebarText
    readonly property color sidebarTextActive: themeBridge.sidebarTextActive
    readonly property color sidebarHoverBg: themeBridge.sidebarHoverBg
    readonly property color sidebarActiveBg: themeBridge.sidebarActiveBg
    readonly property color success: themeBridge.success
    readonly property color warning: themeBridge.warning
    readonly property color danger: themeBridge.danger
    readonly property color iconOnAccent: themeBridge.iconOnAccent
    readonly property bool isDark: themeBridge.isDark

    // Spacing
    readonly property int spacingXS: 4
    readonly property int spacingSM: 6
    readonly property int spacingMD: 8
    readonly property int spacingLG: 12
    readonly property int spacingXL: 16
    readonly property int spacingXXL: 20
    readonly property int spacingXXXL: 24
    readonly property int spacingPage: 32

    // Radius
    readonly property int radiusSM: 4
    readonly property int radiusMD: 8
    readonly property int radiusLG: 12
    readonly property int radiusXL: 16
    readonly property int radiusPill: 999

    // Font Sizes
    readonly property int fontSizeCaption: 11
    readonly property int fontSizeBodySmall: 12
    readonly property int fontSizeBody: 13
    readonly property int fontSizeSubtitle: 15
    readonly property int fontSizeTitleSmall: 18
    readonly property int fontSizeTitleLarge: 24

    // Animasyon Süreleri
    readonly property int animFast: 150
    readonly property int animNormal: 250
    readonly property int animSlow: 350
}
