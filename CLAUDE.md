# AI Asistan Geliştirme Yönergeleri (CLAUDE.md)

Bu dosya, **Proje Yönetim ve Takip Platformu** deposunda çalışacak tüm yapay zeka asistanları için bağlayıcı kuralları içerir. Kod yazmadan veya mimari değişiklik önermeden önce bu dosyayı **ve** `Project_docs/RULES.md` dosyasını okumak **ZORUNLUDUR**.

---

## 0. Çalışma Ortamı

- **Conda env:** `C:\Users\ysfygc\anaconda3\envs\projeTakip`
- Tüm kurulum, test ve çalıştırma komutları bu ortamda yapılacak.
- Bağımlılık değişikliklerinde `requirements.txt` veya `pyproject.toml` güncellenecek; ortama elle paket kurulmayacak.

---

## 1. Temel Anayasa: Project_docs/RULES.md

- Geliştirilecek her kod parçası `Project_docs/RULES.md` dosyasındaki standartlara uymak zorundadır.
- **Asla "God Object" yaratma:** Bir dosya 400 satırı, bir sınıf 15 metodu aşıyorsa, mevcut koda ekleme yapmak yerine refactoring öner.
- SOLID prensiplerini ve Single Responsibility kuralını her fonksiyonda gözet.

---

## 2. Mimari ve Teknoloji Yığını

- **Arayüz (UI):** PySide6. `14_PREMIUM_UI_UX_TASARIM_PLANI.md` uyarınca modern, gölgeli (`QGraphicsDropShadowEffect`), gradyanlı ve animasyonlu (200-300 ms) bileşenler kodlanacak.
- **Veritabanı:** Doğrudan SQLite sorguları YASAKTIR. `SQLAlchemy` + `Alembic`. Tüm şema değişiklikleri migration scripti ile yapılacak.
- **Bellek Yönetimi:** Her PySide6 widget'ı oluşturulurken `parent` parametresi atanacak.
- **Katman Sırası:** `UI Widget → Controller/ViewModel → Service → Repository → SQLAlchemy Model`. Katmanlar arası sıçrama yasak; bağımlılıklar `di_container.py` üzerinden enjekte edilecek.

---

## 3. Kod Kalitesi — Senior Standartları

### 3.1 Tip Güvenliği
- Her fonksiyon/metod imzasına Python type hint eklenecek (`-> None`, `-> int | None` vb.).
- Dönüş tipi belirsiz olduğunda `Any` kullanmak yerine açık bir `TypedDict` veya `dataclass` tanımlanacak.
- `mypy` veya `pyright` uyarıları hata sayılacak; `# type: ignore` kullanılmadan önce gerekçe yorum olarak eklenmeli.

### 3.2 Hata Yönetimi
- Bare `except:` veya `except Exception as e: pass` YASAKTIR.
- İş katmanı hataları `exceptions.py` içinde tanımlı özel istisnalar fırlatacak (örn. `ProjectValidationError`, `TaskNotFoundError`).
- UI katmanı bu istisnaları yakalayıp kullanıcıya anlamlı mesaj gösterecek; stack trace kullanıcıya asla gösterilmeyecek.
- Her `try/except` bloğu yalnızca beklenen istisna tipini yakalayacak.

### 3.3 Fonksiyon ve Sınıf Boyutu
- Fonksiyon: max 25 satır, tek sorumluluk.
- Sınıf: max 15 public metod, max 400 satır.
- Bu sınırlara yaklaşıldığında ekleme yapma, böl ve refactor et.

### 3.4 Guard Clause Zorunluluğu
- İçi içe `if/else` (arrow anti-pattern) yerine erken `return`/`raise` kullanılacak.

```python
# YANLIŞ
def process(item):
    if item:
        if item.is_valid():
            ...

# DOĞRU
def process(item):
    if not item:
        raise ValueError("item boş olamaz")
    if not item.is_valid():
        raise ItemValidationError(...)
    ...
```

### 3.5 Immutability ve Side Effect
- Fonksiyonlar mümkün olduğunca saf (pure) olacak; dış state'i yan etki olarak değiştirmeyecek.
- UI bileşenleri iş mantığı değişkeni tutmayacak; state `ViewModel` veya `Controller`'da yaşayacak.

---

## 4. Test Stratejisi

- **Birim testi:** Repository ve Service katmanları için `pytest` ile test yazılacak. Kritik iş kuralları kapsanmadan PR açılmayacak.
- **Mock kullanımı:** `unittest.mock` ile yalnızca dış bağımlılıklar (DB, dosya sistemi, ağ) mock'lanacak; iç servisler gerçek implementasyonla test edilecek.
- **Test isimlendirme:** `test_<method>_when_<durum>_should_<beklenen>` formatı.
- **Fixture'lar:** `conftest.py`'de paylaşılan fixture'lar tanımlanacak; her test kendi verisini oluşturacak, birbirine bağımlı testler yasak.
- SQLAlchemy testleri in-memory SQLite (`sqlite:///:memory:`) kullanacak; production DB'ye dokunulmayacak.

---

## 5. Performans Kuralları

- **Lazy loading zorunlu:** Liste/ağaç bileşenlerinde tüm veri aynı anda RAM'e yüklenmeyecek; pagination veya sanal scroll uygulanacak.
- **N+1 sorgu yasağı:** İlişkisel sorgularda `joinedload` veya `selectinload` kullanılacak; döngü içinde `session.query()` çağrısı yasak.
- **UI thread koruması:** Ağır iş (DB sorgusu, dosya okuma) `QThread` veya `QRunnable` ile arka plana alınacak; UI thread bloke edilmeyecek.
- Gereksiz `QWidget.update()` / `repaint()` çağrılarından kaçınılacak; sinyal/slot mekanizması tercih edilecek.

---

## 6. Güvenlik

- SQL injection: string birleştirme veya f-string ile sorgu oluşturmak YASAKTIR. Parametrik sorgu veya SQLAlchemy ORM kullanılacak.
- Kullanıcı girdisi her zaman UI katmanında doğrulanacak, ardından servis katmanında iş kuralı doğrulaması yapılacak.
- Şifre ve hassas veri plain-text olarak loglara yazılmayacak.
- Dosya yollarında `os.path.join` / `pathlib.Path` kullanılacak; string birleştirme ile path oluşturmak yasak.

---

## 7. Loglama Standartları

- `print()` ile loglama YASAKTIR. Python `logging` modülü kullanılacak.
- Log seviyeleri: `DEBUG` (geliştirme), `INFO` (iş akışı), `WARNING` (geri çekilebilir hata), `ERROR` (kritik başarısızlık).
- Log mesajları İngilizce, yapılandırılmış ve aranabilir olacak. Kullanıcı adı, ID gibi bağlam verileri `extra={}` ile eklenecek.

---

## 8. Kod İnceleme (Review) Kontrol Listesi

Kod teslim edilmeden önce şu sorular cevaplanmış olmalı:

1. Fonksiyon 25 satır sınırını aşıyor mu?
2. Bare `except` veya `pass` var mı?
3. Type hint eksik metod var mı?
4. DB sorgusu widget içinde yazılmış mı?
5. N+1 sorgu riski var mı?
6. Test eklendi mi? Kritik yol kapsandı mı?
7. `parent` atanmamış PySide6 nesnesi var mı?
8. Commit mesajı `Project_docs/RULES.md §6` formatına uygun mu?

---

## 9. Refactoring Tetikleyicileri

Aşağıdaki durumlardan **herhangi biri** gerçekleştiğinde yeni özellik eklemek yerine önce refactor:

- Dosya > 400 satır
- Sınıf > 15 metod
- Aynı mantık 3+ yerde tekrar ediyor (DRY ihlali)
- Widget doğrudan DB çağırıyor
- Bir fonksiyon 3'ten fazla argüman alıyor (nesne/dataclass'a topla)
- Test yazmak için aşırı mock gerekiyor (tasarım kokusu)

---

## 10. İletişim ve Commit Kuralları

- Commit mesajları tamamen Türkçe, imla kurallarına uygun (`ç, ğ, ı, ö, ş, ü`).
- Jenerik mesajlar (`güncelleme yapıldı`, `fix`, `düzeltme`) YASAKTIR.
- AI/prompt referansı commit mesajlarında ve kod yorumlarında yer almayacak.
- Yorum satırları neyin yapıldığını değil, **neden** yapıldığını açıklayacak.
- Format: `tip(kapsam): açıklama` — örnek:

```text
feat(task_service): Görev tamamlanma yüzdesi hesaplama servise taşındı

- Widget içindeki hesaplama mantığı TaskService.calculate_completion() metoduna alındı.
- Alt görev ağırlıkları dikkate alınan ağırlıklı ortalama algoritması eklendi.
- TaskRepository.fetch_subtasks() metodu lazy load desteğiyle güncellendi.
```
