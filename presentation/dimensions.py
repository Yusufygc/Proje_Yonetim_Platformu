"""
UI boyut ve geometri sabitleri — tek doğruluk kaynağı.

Qt QSS layout margin/spacing/fixed-size yönetemez; bu sabitler
Python kodundaki magic number'ların yerine geçer.
Her grup kendi kapsamını temsil eder; anlamsız mikro-soyutlamadan kaçınılır.
"""


class Spacing:
    """setContentsMargins / setSpacing için standart ızgara değerleri."""

    XS = 4
    SM = 6
    MD = 8
    LG = 12
    XL = 16
    XXL = 20
    XXXL = 24
    PAGE = 32   # Sayfa seviyesi dış boşluk


class Size:
    """Sabit widget boyutları."""

    # Sidebar
    SIDEBAR_NAV_BTN_H = 44          # SidebarNavButton yüksekliği
    SIDEBAR_TOGGLE_W = 28           # Collapse/expand toggle butonu genişliği
    SIDEBAR_TOGGLE_H = 28           # Collapse/expand toggle butonu yüksekliği
    SIDEBAR_SEARCH_H = 36           # Sidebar arama butonu yüksekliği
    SIDEBAR_DIVIDER_H = 1           # Yatay ayraç yüksekliği

    # Theme toggle switch
    THEME_SWITCH_W = 44             # ThemeToggleSwitch genişliği
    THEME_SWITCH_H = 24             # ThemeToggleSwitch yüksekliği
    THEME_THUMB = 18                # Thumb boyutu (kare)
    THEME_COLLAPSED_BTN = 36        # Çöktürülmüş sidebar tema butonu

    # Genel buton minimum boyutları
    BTN_SM_W = 60                   # Küçük buton min genişliği (checklist ekle vb.)
    BTN_SM_H = 32                   # Küçük buton min yüksekliği
    BTN_MD_W = 80                   # Orta buton min genişliği
    BTN_MD_H = 36                   # Orta buton min yüksekliği
    BTN_MD_H38 = 38                 # Dialog ana butonları (Cancel, Save)
    STAGE_BTN_H = 24                # Aşama satırı içi "Tamamla/Aktif Et" butonu — kompakt
    STAGE_ROW_H = 36                # Aşama satırı sabit yüksekliği (8 aşamayı yarım ekran yutmadan göstermek için)
    BTN_LG_W = 90                   # Büyük dialog butonu min genişliği
    BTN_LG_H = 38                   # Büyük dialog butonu min yüksekliği
    BTN_NEW_PROJECT_W = 130         # "Yeni Proje" AnimatedButton genişliği
    BTN_NEW_PROJECT_H = 36          # "Yeni Proje" AnimatedButton yüksekliği
    BTN_ICON_SM = 20                # Küçük icon buton (checklist toggle/delete) kare kenarı
    BTN_ICON_MD = 24                # Orta icon buton (+) kare kenarı
    BTN_IDEA_W = 140                # "Yeni Fikir" butonu min genişliği
    BTN_IDEA_H = 40                 # "Yeni Fikir" butonu min yüksekliği

    # Panel / sayfa boyutları
    LEFT_PANEL_W = 280              # Projeler sayfası sol liste paneli genişliği
    PAGE_HEADER_H = 80              # InfoPage header yüksekliği
    TASK_LIST_MAX_H = 220           # TaskListWidget scroll alanı max yüksekliği

    # Form input yükseklikleri
    INPUT_H_SM = 32                 # Küçük input (checklist ekleme)
    INPUT_H_MD = 36                 # Orta input/combo (dialog form)
    INPUT_H_LG = 38                 # Büyük input (dialog ana alan)
    TEXTAREA_H_SM = 70              # Küçük textarea (notlar vb.)
    TEXTAREA_H_MD = 72              # Orta textarea
    TEXTAREA_H_LG = 80              # Büyük textarea (açıklama alanları)

    # İlerleme çubuğu
    PROGRESS_W = 80                 # Proje listesi progress bar genişliği
    PROGRESS_H = 4                  # Proje listesi progress bar yüksekliği

    # ProjectListItem
    LIST_ITEM_MIN_H = 58            # Proje liste öğesi minimum yüksekliği

    # EmptyState illustration
    EMPTY_ILLUSTRATION_W = 160
    EMPTY_ILLUSTRATION_H = 120

    # Toast
    TOAST_H = 48
    TOAST_MIN_W = 300
    TOAST_MAX_W = 500

    # Dialog minimum genişlikler
    DIALOG_TASK_MIN_W = 480
    DIALOG_PROJECT_MIN_W = 620
    DIALOG_IDEA_MIN_W = 500

    # Notlar/kararlar buton satırı minimum yükseklik
    ACTION_BTN_H = 36


class Shadow:
    """apply_shadow() için varsayılan değerler."""

    BLUR = 20           # Bulanıklık yarıçapı (piksel)
    Y_OFFSET = 4        # Dikey kaydırma (piksel)
    ALPHA = 40          # Siyah gölge opaklığı (0–255)

    # Kart/panel hafif gölge
    CARD_BLUR = 15
    CARD_Y = 3
    CARD_ALPHA = 20

    # Dashboard liste gölgesi
    LIST_BLUR = 15
    LIST_Y = 3
    LIST_ALPHA = 15

    # Toast gölgesi
    TOAST_BLUR = 20
    TOAST_Y = 6
    TOAST_ALPHA = 40

    # Gölge rengi (R, G, B, A) — tüm gölgeler siyah tabanlı
    COLOR_R = 0
    COLOR_G = 0
    COLOR_B = 0
