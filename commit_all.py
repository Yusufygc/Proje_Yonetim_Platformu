import os
import subprocess

commits = {
    # Modified
    ".pre-commit-config.yaml": "chore(config): pre-commit konfigürasyonu güncellendi\n\nProje geneli kod standartlarını sağlamak amacıyla pre-commit ayarlarında iyileştirmeler yapıldı.",
    "controllers/dashboard_controller.py": "feat(controllers): dashboard controller iş mantığı güncellendi\n\nAna panel için gerekli veri akışları ve controller seviyesindeki işleyici metotlar genişletildi.",
    "controllers/decision_controller.py": "feat(controllers): karar yönetimi controller güncellendi\n\nKararların işlenmesi ve UI tarafına aktarılması sürecindeki kontroller iyileştirildi.",
    "controllers/idea_controller.py": "feat(controllers): fikir yönetimi controller iyileştirildi\n\nFikirlerin eklenmesi ve güncellenmesine dair backend haberleşme metotları güncellendi.",
    "controllers/project_controller.py": "feat(controllers): proje controller metodları güncellendi\n\nProje oluşturma, silme ve güncelleme aşamalarındaki veri bağlama işlemleri düzenlendi.",
    "controllers/task_controller.py": "feat(controllers): görev yönetimi controller güncellendi\n\nGörevlerin (tasks) takibi ve durum değişikliklerini yöneten controller fonksiyonları genişletildi.",
    "core/exceptions/base_exception.py": "refactor(core): temel hata (exception) yönetimi güncellendi\n\nUygulama genelinde fırlatılan özel hataların temel (base) sınıfı iyileştirildi.",
    "core/exceptions/task_exceptions.py": "refactor(core): görev hataları (exceptions) güncellendi\n\nGörev işlemleri sırasında ortaya çıkabilecek hata durumları için spesifik tipler belirlendi.",
    "core/logger.py": "refactor(core): merkezi loglama mekanizması iyileştirildi\n\nSistem kayıtlarının daha standart ve okunabilir formatta yazılabilmesi için logger güncellendi.",
    "core/managers/log_manager.py": "refactor(core): log yöneticisi güncellendi\n\nLog yönetimi servis bazlı bir yapıya kavuşturularak izlenebilirlik artırıldı.",
    "core/workers/worker.py": "refactor(core): arka plan işçi (worker) sınıfı iyileştirildi\n\nArka planda asenkron olarak çalıştırılan işlemlerin (threads) yönetimi ve hata yakalama kapasitesi artırıldı.",
    "di_container.py": "refactor(di): bağımlılık enjeksiyon (DI) konteyneri güncellendi\n\nYeni servislerin ve repository sınıflarının proje genelinde kullanılabilmesi için tanımlamalar yapıldı.",
    "domain/enums/decision_status.py": "feat(domain): karar durumları (enums) güncellendi\n\nKarar takip süreci için kullanılabilecek yeni durum tanımlamaları (enum) eklendi.",
    "domain/enums/idea_status.py": "feat(domain): fikir durumları güncellendi\n\nFikirlerin değerlendirme aşamalarını belirten enumerator tipleri genişletildi.",
    "domain/enums/stage_status.py": "feat(domain): aşama durumları güncellendi\n\nProje aşamalarının (stages) durum takibini kolaylaştıran tanımlamalar yapıldı.",
    "domain/enums/task_type.py": "feat(domain): görev türleri eklendi/güncellendi\n\nGörevlerin kategorizasyonunu sağlayan tip tanımlamaları zenginleştirildi.",
    "domain/models/__init__.py": "refactor(domain): model modülü başlatıcısı güncellendi\n\nUygulamadaki tüm veri modellerinin dışa aktarımını sağlayan init dosyası düzenlendi.",
    "domain/models/checklist_item.py": "feat(domain): checklist elemanı modeli güncellendi\n\nAlt görevleri temsil eden checklist elemanlarına ait veri alanları genişletildi.",
    "domain/models/decision_record.py": "feat(domain): karar kaydı modeli iyileştirildi\n\nKararların neden-sonuç ilişkisini tutabilmek için karar modeli alanları eklendi.",
    "domain/models/idea.py": "feat(domain): fikir modeli alanları güncellendi\n\nFikir detaylarının daha kapsamlı tutulması için yeni veri özellikleri modele dahil edildi.",
    "domain/models/note.py": "feat(domain): not modeli güncellendi\n\nProjelerle ve görevlerle ilişkili notların veritabanı modeli iyileştirildi.",
    "domain/models/project.py": "feat(domain): proje modeli alanları genişletildi\n\nProjelerin sağlık durumu, GitHub URL'i, hedeflenen çıktılar gibi metadatalarını barındıran alanlar eklendi.",
    "domain/models/project_stage.py": "feat(domain): proje aşaması modeli güncellendi\n\nProje takvimindeki her bir dönüm noktasını temsil eden aşama modeli güncellendi.",
    "domain/models/resource.py": "feat(domain): kaynak (resource) modeli güncellendi\n\nProje materyalleri ve dış bağlantıları temsil eden kaynak modeli iyileştirildi.",
    "domain/models/task.py": "feat(domain): görev (task) modeli iyileştirildi\n\nGörev eforu, zorluğu ve bağlantılı olduğu kısımları ifade eden veri alanları eklendi.",
    "infrastructure/database/db_manager.py": "refactor(db): veritabanı yöneticisi bağlantı ayarları güncellendi\n\nVeritabanı bağlantı yönetimi, oturum açma (session) işlemleri ve bağlantı havuzu iyileştirildi.",
    "infrastructure/repositories/decision_repository.py": "feat(repo): karar veritabanı erişim katmanı güncellendi\n\nKararların SQLite üzerinde saklanması ve çekilmesi işlemleri için CRUD metotları yazıldı.",
    "infrastructure/repositories/idea_repository.py": "feat(repo): fikir repository veritabanı işlemleri iyileştirildi\n\nFikirlerin sorgulanması, filtreli getirilmesi ve saklanmasını üstlenen katman güncellendi.",
    "infrastructure/repositories/note_repository.py": "feat(repo): not repository metotları güncellendi\n\nUygulamadaki metin notlarının kalıcı hafızada (DB) barındırılmasını sağlayan fonksiyonlar genişletildi.",
    "infrastructure/repositories/project_repository.py": "feat(repo): proje repository işlemleri iyileştirildi\n\nProjelerin kaydedilmesi, silinmesi ve ilişkili verilerinin birleşik getirilmesi (join) optimize edildi.",
    "infrastructure/repositories/resource_repository.py": "feat(repo): kaynak repository işlemleri güncellendi\n\nDış bağlantıların ve proje kaynaklarının veritabanı entegrasyonu tamamlandı.",
    "infrastructure/repositories/task_repository.py": "feat(repo): görev repository metodları genişletildi\n\nGörev sorguları, görev ekleme ve güncelleme gibi kalıcı hafıza işlemleri geliştirildi.",
    "main.py": "refactor(main): uygulama ana giriş noktası güncellendi\n\nUygulamanın başlangıç rutinleri, pencere yükleme işlemleri ve DI yapısının tetiklenmesi iyileştirildi.",
    "presentation/dialogs/task_dialog.py": "style(ui): görev ekleme diyaloğu güncellendi\n\nGörev detaylarının girildiği pencerenin arayüz elemanları, hizalamaları ve görünümleri düzenlendi.",
    "presentation/pages/dashboard_page.py": "style(ui): ana panel (dashboard) görünümü iyileştirildi\n\nGenel istatistikleri ve özetleri barındıran kontrol paneli sayfası görsel olarak zenginleştirildi.",
    "presentation/pages/ideas_page.py": "style(ui): fikirler sayfası görünümü güncellendi\n\nFikir listesinin görünümü ve tablo/kart tasarımları yeni tema standartlarına uyarlandı.",
    "presentation/pages/tasks_page.py": "style(ui): görevler sayfası görünümü iyileştirildi\n\nGörevlerin listelenmesi, filtrelenmesi ve kullanıcıya gösterimi sırasındaki arayüz detayları iyileştirildi.",
    "presentation/shell/main_window.py": "style(ui): ana pencere iskeleti güncellendi\n\nUygulamanın temel taşıyıcı penceresi (shell), sayfa geçişleri ve genel layout anlamında güncellendi.",
    "presentation/shell/sidebar.py": "style(ui): yan menü (sidebar) tasarımı iyileştirildi\n\nNavigasyon barındaki ikonlar, aktif seçim görünümleri ve dark/light mode uyumlulukları düzeltildi.",
    "presentation/widgets/decision_list_widget.py": "style(ui): karar listesi bileşeni güncellendi\n\nKararların alt alta gösterildiği custom liste widget'ı görsel standartlara uyduruldu.",
    "presentation/widgets/project_detail_panel.py": "style(ui): proje detay paneli görünümü iyileştirildi\n\nSeçilen projenin içeriğini yansıtan sağ panelin veri okunaklılığı ve eleman yerleşimi güncellendi.",
    "presentation/widgets/project_list_item.py": "style(ui): proje listesi elemanı stili güncellendi\n\nYan menüdeki proje kartlarının seçilme durumları, hover efektleri ve şeffaflık (transparent) ayarları düzeltildi.",
    "presentation/widgets/stage_timeline_widget.py": "style(ui): aşama zaman çizelgesi bileşeni güncellendi\n\nProjelerin aşamalarını görselleştiren zaman tüneli arayüzü iyileştirildi.",
    "presentation/widgets/toast.py": "style(ui): bildirim (toast) bileşeni iyileştirildi\n\nEkranın köşesinde çıkan hata, başarı ve bilgi bildirimlerinin renkleri ve tasarımları düzeltildi.",
    "pyproject.toml": "chore(deps): proje bağımlılıkları ve konfigürasyonları güncellendi\n\nProjede kullanılan kütüphane versiyonları (PySide6, SQLAlchemy vb.) ve pytest, ruff ayarları kaydedildi.",
    "resources/locales/strings.tr.json": "chore(i18n): türkçe dil dosyası güncellendi\n\nUygulama arayüzünde kullanılan metinlerin dil çevirileri ve isimlendirmeleri eklendi.",
    "services/dashboard_service.py": "feat(services): dashboard iş mantığı güncellendi\n\nKontrol panelinde gösterilecek verilerin analiz edilip hesaplanmasını sağlayan servis fonksiyonları eklendi.",
    "services/decision_service.py": "feat(services): karar iş mantığı iyileştirildi\n\nKararların backend seviyesindeki kuralları ve validasyon süreçleri servise entegre edildi.",
    "services/export_service.py": "feat(services): dışa aktarma servisi güncellendi\n\nProje verilerini veya tablolarını farklı formatlarda dışa aktarma (export) altyapısı genişletildi.",
    "services/idea_service.py": "feat(services): fikir servisi işlemleri güncellendi\n\nFikirlerin puanlanması ve filtrelenmesiyle ilgili iş (business) kuralları uygulandı.",
    "services/project_service.py": "feat(services): proje servisi mantığı iyileştirildi\n\nProjeye bağlı diğer alt öğelerin (aşama, görev vb.) proje ile birlikte yönetilmesini sağlayan kurallar düzenlendi.",
    "services/resource_service.py": "feat(services): kaynak yönetimi servisi güncellendi\n\nProjelere eklenen kaynakların doğrulanması ve yönetimi işlemleri sağlandı.",
    "services/search_service.py": "feat(services): arama servisi metodları güncellendi\n\nUygulama geneli metin aramalarını koordine eden servis altyapısı iyileştirildi.",
    "services/stage_service.py": "feat(services): proje aşaması servisi iyileştirildi\n\nAşamalar arası geçiş ve aktivasyon gibi iş mantıkları servis katmanında ele alındı.",
    "services/task_service.py": "feat(services): görev servisi işlemleri güncellendi\n\nGörev tamamlama, efor yönetimi ve görevler arası ilişkiler servis tabanlı hale getirildi.",
    "uv.lock": "chore(deps): uv kilit dosyası güncellendi\n\nBağımlılıkların versiyon kilitlerini içeren uv paketi kilit dosyası yenilendi.",
    
    # Untracked files / Directories
    "alembic.ini": "chore(db): alembic konfigürasyon dosyası eklendi\n\nVeritabanı göç (migration) işlemlerini yöneten alembic aracının konfigürasyon dosyası oluşturuldu.",
    "core/managers/backup_manager.py": "feat(core): yedekleme yöneticisi eklendi\n\nKullanıcı verilerinin güvenliğini sağlamak amacıyla periyodik veya manuel yedekleme işlemleri yapan modül eklendi.",
    "core/managers/secret_manager.py": "feat(core): gizli bilgi yöneticisi eklendi\n\nUygulama sırlarını (secrets) veya hassas anahtarları güvenli şekilde yönetecek olan mekanizma eklendi.",
    "domain/dtos/forms.py": "feat(domain): form veri transfer nesneleri (DTOs) eklendi\n\nArayüz formlarından servislere aktarılacak yapısal veri paketleri eklendi.",
    "domain/enums/project_health.py": "feat(domain): proje sağlık durumu tanımlamaları eklendi\n\nProjenin (Yolunda, Riskli vb.) sağlık durumlarını belirten yeni bir Enum yapısı tanımlandı.",
    "domain/models/activity_log.py": "feat(domain): etkinlik günlüğü (activity log) modeli eklendi\n\nKullanıcı hareketlerini (audit) izlemek için gerekli veritabanı veri yapısı oluşturuldu.",
    "domain/models/attachment.py": "feat(domain): eklenti (attachment) modeli eklendi\n\nProjelere eklenebilecek dosya veya belgeleri modelleyen yapı eklendi.",
    "domain/models/project_idea.py": "feat(domain): proje fikri ilişkisel modeli eklendi\n\nFikirlerin projeye dönüşümünü takip etmek veya projelerle fikirleri ilişkilendirmek için veri yapısı oluşturuldu.",
    "domain/models/project_tag.py": "feat(domain): proje etiketi modeli eklendi\n\nProjeleri etiketlerle organize etmeyi sağlayan veri yapısı eklendi.",
    "domain/models/setting.py": "feat(domain): ayar (setting) modeli eklendi\n\nKullanıcı ve sistem tercihlerinin veritabanında tutulması için anahtar-değer modeli tanımlandı.",
    "domain/models/workflow_stage.py": "feat(domain): iş akışı aşaması modeli eklendi\n\nÖzel iş akışları tanımlayabilmek için gereken aşama (workflow_stage) modeli geliştirildi.",
    "infrastructure/database/alembic_runner.py": "feat(db): alembic çalıştırıcı mekanizması eklendi\n\nKod içerisinden Alembic migration komutlarını doğrudan tetikleyebilecek olan arayüz eklendi.",
    "infrastructure/database/migration_runner.py": "feat(db): veritabanı göç (migration) çalıştırıcısı eklendi\n\nProgram başlarken veya ihtiyaç anında veritabanı şema güncellemelerini çalıştıran modül oluşturuldu.",
    "infrastructure/migrations/": "chore(db): veritabanı göç dosyaları eklendi\n\nAlembic tarafından oluşturulan ilk migration dosyaları ve veritabanı şema versiyonları projeye dahil edildi.",
    "infrastructure/repositories/activity_log_repository.py": "feat(repo): etkinlik günlüğü veritabanı erişimi eklendi\n\nKullanıcı aktivitelerinin veritabanına eklenmesi ve sorgulanması için repository yazıldı.",
    "infrastructure/repositories/attachment_repository.py": "feat(repo): eklenti repository işlemleri eklendi\n\nDosya ve eklentilerin DB tarafındaki CRUD işlemleri için sınıf eklendi.",
    "infrastructure/repositories/project_idea_repository.py": "feat(repo): proje fikir repository eklendi\n\nProje ve fikir ilişkilerinin yönetileceği veritabanı katmanı tanımlandı.",
    "infrastructure/repositories/project_tag_repository.py": "feat(repo): proje etiket repository eklendi\n\nEtiket yönetimi (tagging) veritabanı işlemleri oluşturuldu.",
    "infrastructure/repositories/workflow_stage_repository.py": "feat(repo): iş akışı aşaması repository eklendi\n\nİş akışı modelinin kalıcı depolama seviyesindeki işlemleri için repository tamamlandı.",
    "installer/": "chore(installer): kurulum sihirbazı dosyaları eklendi\n\nUygulamanın Inno Setup gibi paketleyiciler veya kurulum sihirbazları için gereken konfigürasyon dosyaları eklendi.",
    "presentation/widgets/empty_state.py": "feat(ui): boş durum (empty state) bileşeni eklendi\n\nVeri olmadığında gösterilecek görsel ağırlıklı ve kullanıcı dostu arayüz bileşeni (EmptyState) kodlandı.",
    "quality.py": "chore(tooling): kalite kontrol aracı eklendi\n\nKod kalitesini (linting, test) otomatik olarak test eden ve raporlayan script eklendi.",
    "resources/illustrations/": "chore(assets): illüstrasyon dosyaları eklendi\n\nArayüzde boş durumlarda veya özel ekranlarda gösterilecek görsel asset'ler sisteme dahil edildi.",
    "scripts/": "chore(scripts): yardımcı betikler eklendi\n\nGeliştirme süreçlerini otomatize etmek için terminal scriptleri projeye yerleştirildi.",
    "tests/test_mvp_core.py": "test(core): MVP çekirdek testleri eklendi\n\nUygulamanın minimum geçerli ürün sınırları içindeki kritik fonksiyonları için birim testleri (unit tests) yazıldı.",
    "tests/test_quality_systems.py": "test(qa): kalite sistemleri testleri eklendi\n\nKalite servislerinin doğru çalıştığını teyit eden kapsamlı test senaryoları eklendi.",
    "tests/test_ui_smoke.py": "test(ui): arayüz duman (smoke) testleri eklendi\n\nArayüzün hatasız ayağa kalktığından ve temel bileşenlerin render edildiğinden emin olmak için testler yazıldı."
}

def run_git_commit(filepath, message):
    try:
        # Add the file
        subprocess.run(["git", "add", filepath], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Commit the file
        subprocess.run(["git", "commit", "-m", message], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Committed: {filepath}")
    except subprocess.CalledProcessError:
        print(f"Skipped or error on: {filepath} (Might be already committed or deleted)")

# Git status --porcelain
result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

for line in result.stdout.splitlines():
    if not line.strip():
        continue
    status = line[:2]
    filepath = line[3:].strip()
    
    # Handle renames / quotes in git porcelain
    if filepath.startswith('"') and filepath.endswith('"'):
        filepath = filepath[1:-1]
    
    # Match the file with our dictionary
    msg = None
    for key in commits:
        if filepath.startswith(key):
            msg = commits[key]
            break
            
    if not msg:
        msg = f"chore(sync): {filepath} güncellendi\n\nUygulama güncellemesi."
        
    run_git_commit(filepath, msg)

print("All files processed.")
