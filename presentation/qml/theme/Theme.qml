pragma Singleton
import QtQuick 2.15

QtObject {
    id: themeRoot

    function accent(themeName) {
        return themeBridge.accentStart;
    }

    function accentAlpha(themeName, alpha) {
        var c = Qt.color(themeBridge.accentStart);
        return Qt.rgba(c.r, c.g, c.b, alpha !== undefined ? alpha : 0.2);
    }

    readonly property var spacing: ({
        xs: 4,
        sm: 8,
        md: 12,
        lg: 16,
        xl: 20,
        xxl: 24,
        xxxl: 32
    })

    readonly property var radius: ({
        small: 4,
        medium: 8,
        large: 12,
        xl: 16,
        full: 999
    })

    readonly property var typography: ({
        sizeSmall: 11,
        sizeBody: 13,
        sizeH3: 15,
        sizeH2: 18,
        sizeH1: 22,
        weightNormal: Font.Normal,
        weightMedium: Font.Medium,
        weightSemiBold: Font.DemiBold,
        weightBold: Font.Bold,
        fontFamily: "Segoe UI, -apple-system, sans-serif"
    })

    readonly property var animation: ({
        fast: 120,
        normal: 200,
        slow: 350
    })

    // Renkler — themeBridge üzerinden reaktif
    readonly property color background: themeBridge.background
    readonly property color surface: themeBridge.surface
    readonly property color surfaceRaised: themeBridge.surfaceRaised
    readonly property color surfaceAlt: themeBridge.surfaceAlt
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
    readonly property color hoverOverlay: themeBridge.hoverOverlay
    readonly property bool isDark: themeBridge.isDark
}
