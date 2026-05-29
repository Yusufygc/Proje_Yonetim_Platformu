"""
Uygulama kullanım rehberini içeren bilgilendirme sayfası.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from core.managers.theme_manager import ThemeManager


class InfoPage(QWidget):
    """Uygulamanın nasıl kullanılacağını anlatan statik bilgilendirme sayfası."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget(parent=self)
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 32, 0)
        
        title = QLabel("Bilgilendirme ve Kullanım Rehberi", parent=header)
        title.setProperty("cssClass", "title-large")
        header_layout.addWidget(title)
        
        layout.addWidget(header)

        # Divider
        divider = QFrame(parent=self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setProperty("cssClass", "divider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # Main Content Area directly using QTextBrowser (it has built-in scroll)
        browser = QTextBrowser(parent=self)
        browser.setObjectName("info_browser")
        browser.setOpenExternalLinks(True)
        browser.setFrameShape(QFrame.Shape.NoFrame)
        
        theme = ThemeManager.instance()
        accent = theme.color("accent_start")
        text = theme.color("text_primary")
        muted = theme.color("text_secondary")
        border = theme.color("border")
        surface_raised = theme.color("surface_raised")

        # HTML Content
        html_content = f"""
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: {accent}; font-size: 32px; margin-bottom: 12px; margin-top: 10px;">Proje Takip Platformu</h1>
            <p style="font-size: 16px; color: {text}; line-height: 1.8;">
                Bu platform, yazılım projelerinizi, yaratıcı fikirlerinizi ve günlük görevlerinizi tek bir merkezden, 
                modern ve hızlı bir arayüzle yönetebilmeniz için geliştirildi. Aşağıda platformun tüm özelliklerini nasıl 
                tam kapasiteyle kullanabileceğinize dair detaylı bilgileri bulabilirsiniz.
            </p>

            <hr style="border: none; border-top: 1px solid {border}; margin: 32px 0;">

            <h2 style="color: {accent}; margin-top: 24px; font-size: 22px;">🏠 Ana Panel (Dashboard)</h2>
            <p style="font-size: 15px; line-height: 1.6; color: {text};">
                Uygulamaya ilk girdiğinizde sizi karşılayan kontrol merkezidir. Platformdaki genel durumunuzu özetler ve sizi yönlendirir.
            </p>
            <ul style="font-size: 15px; color: {text}; line-height: 1.8;">
                <li><b>Durum Özeti:</b> Toplam proje sayınızı, bekleyen ve tamamlanan görevlerinizi anlık olarak, istatistiksel kartlar halinde görebilirsiniz.</li>
                <li><b>Aktif Projeler:</b> Üzerinde çalıştığınız (aktif durumdaki) projelere tek tıkla ulaşmanızı sağlayan hızlı erişim listesi.</li>
                <li><b>Yaklaşan Görevler:</b> Yapılacaklar listenizdeki en acil veya üzerinde çalışılan görevlerinizi gösterir.</li>
            </ul>

            <h2 style="color: {accent}; margin-top: 40px; font-size: 22px;">📁 Projeler Modülü</h2>
            <p style="font-size: 15px; line-height: 1.6; color: {text};">
                Tüm çalışmalarınızı yapılandırıp takip edebileceğiniz, platformun kalbi niteliğindeki ana modüldür.
            </p>
            <ul style="font-size: 15px; color: {text}; line-height: 1.8;">
                <li><b>Kapsamlı Proje Oluşturma:</b> Yan menüden "Projeler"e tıklayıp <b>+ Yeni Proje</b> butonuyla detaylı form doldurabilirsiniz. Projeye başlık, açıklama, GitHub linki, demo URL, etiketler ve son teslim tarihi (hedef tarih) verebilirsiniz.</li>
                <li><b>Süreç Aşamaları (Timeline):</b> Her projenin "Planlandı", "Geliştirme", "Test", "Tamamlandı" gibi aşamaları vardır. Ekrandaki aşama kartları (Kanban vari) ile projenin tam olarak hangi adımda olduğunu görsel olarak görebilirsiniz.</li>
                <li><b>Kararlar ve Notlar:</b> Proje detay sayfasındaki ilgili butonlara tıklayarak proje toplantılarında aldığınız <i>Kararları</i> ve tuttuğunuz <i>Notları</i> kaydedebilirsiniz.</li>
                <li><b>Kaynaklar (Linkler):</b> Projeye ait GitHub repo, Figma tasarım dosyası, Trello veya dokümantasyon (Notion vb.) linklerini "Kaynaklar" diyaloğu aracılığıyla ekleyerek tek tıkla harici sitelere ulaşabilirsiniz.</li>
            </ul>

            <h2 style="color: {accent}; margin-top: 40px; font-size: 22px;">💡 Fikirler Modülü</h2>
            <p style="font-size: 15px; line-height: 1.6; color: {text};">
                Aklınıza aniden gelen ama henüz büyük bir projeye dönüşmeye hazır olmayan düşüncelerinizi, unutmadan kaydedeceğiniz kuluçka merkezidir.
            </p>
            <ul style="font-size: 15px; color: {text}; line-height: 1.8;">
                <li><b>Fikir Havuzu:</b> Fikirlerinizi başlık, içerik, etiket ve önem derecesiyle sisteme ekleyin. İsterseniz fikirlerinizi filtreleyip arayabilirsiniz.</li>
                <li><b>Projeye Dönüştürme:</b> Zamanı gelen ve olgunlaşan bir fikri detay sayfasındaki "Projeye Dönüştür" butonuna tıklayarak saniyeler içinde tüm verileriyle (başlık, açıklama vb.) "Proje Formuna" aktarabilirsiniz. Böylece fikirden icraata geçiş pürüzsüz olur.</li>
            </ul>

            <h2 style="color: {accent}; margin-top: 40px; font-size: 22px;">☑️ Görevler (TODO) Modülü</h2>
            <p style="font-size: 15px; line-height: 1.6; color: {text};">
                Büyük projeleri küçük, eyleme dökülebilir parçalara bölmek için tasarlanmış görev yönetim aracıdır.
            </p>
            <ul style="font-size: 15px; color: {text}; line-height: 1.8;">
                <li><b>Kanban Yapısı:</b> "Yapılacak" (To Do), "Devam Eden" (In Progress) ve "Tamamlanan" (Done) listeleri arasında görevlerinizi yönetebilirsiniz.</li>
                <li><b>Proje Bağlantısı:</b> Her bir görevi sistemdeki belirli bir projenin altına bağlayabilirsiniz. Böylece hangi görevin hangi projeye ait olduğu hiçbir zaman karışmaz.</li>
            </ul>

            <h2 style="color: {accent}; margin-top: 40px; font-size: 22px;">⚙️ Ayarlar ve Kişiselleştirme</h2>
            <p style="font-size: 15px; line-height: 1.6; color: {text};">
                Uygulama deneyimini zevkinize göre özelleştirin.
            </p>
            <ul style="font-size: 15px; color: {text}; line-height: 1.8;">
                <li><b>Karanlık ve Aydınlık Tema (Dark Mode):</b> Sol menünün alt tarafındaki ☀️ / 🌙 ikonuna tıklayarak (veya Ayarlar sayfasından) gözünüzü yormayan premium karanlık (dark) temaya veya ferah aydınlık (light) temaya anında geçiş yapabilirsiniz.</li>
                <li><b>Profil Bilgileri:</b> Adınızı, unvanınızı ve uygulamanın veri dosyalarını (veritabanı) nereye kaydedeceğini (Çalışma Dizini) Ayarlar modülünden güncelleyebilirsiniz.</li>
            </ul>

            <hr style="border: none; border-top: 1px solid {border}; margin: 40px 0;">

            <h2 style="color: {accent}; margin-top: 24px; font-size: 22px;">🚀 Hayat Kurtaran Kısayollar</h2>
            <p style="font-size: 15px; line-height: 1.6; color: {muted};">
                Farenizi (mouse) olabildiğince az kullanarak uygulamada hızla gezinmek için aşağıdaki klavye kısayollarını kullanabilirsiniz:
            </p>
            <div style="background-color: {surface_raised}; padding: 16px 24px; border-radius: 8px; margin-top: 16px;">
                <ul style="font-size: 16px; color: {text}; line-height: 2.2; margin: 0; padding-left: 20px;">
                    <li><b style="color: {accent};">Ctrl + F</b> veya <b style="color: {accent};">Ctrl + K</b> : Tüm uygulama verilerinde arama yapabileceğiniz <b>Hızlı Arama</b> (Search) kutusunu açar.</li>
                    <li><b style="color: {accent};">Ctrl + N</b> : Nerede olursanız olun anında <b>Yeni Proje</b> oluşturma formunu ekrana getirir.</li>
                </ul>
            </div>
            
            <p style="margin-top: 40px; font-size: 13px; color: {muted}; text-align: center;">
                Proje Takip Platformu v0.1.0 • Verimli çalışmalar dileriz!
            </p>
        </div>
        """
        
        browser.setHtml(html_content)
        layout.addWidget(browser)
