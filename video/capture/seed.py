"""Videoda görünen sabit örnek veri.

Tarihler üretim gününe göre geriye verilir; aksi halde analitik grafikleri düz görünür.
"""
from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

HISTORY_WEEKS = 12
FEATURED_PROJECT = "Mobil Bankacılık Arayüzü"
FEATURED_IDEA = "Harcama kategorisi tahmini"

# (başlık, durum, öncelik, açıklama) — listede ilk sırada görünecek olan en üstte.
PROJECTS = [
    (FEATURED_PROJECT, "ACTIVE", "HIGH", "Müşteri uygulamasının yeni ekran tasarımı ve geliştirmesi."),
    ("Stok Takip Sistemi", "ACTIVE", "CRITICAL", "Depo sayım ve stok hareketleri."),
    ("Kurumsal Web Sitesi", "ON_HOLD", "MEDIUM", "Tanıtım sitesinin yenilenmesi."),
    ("Raporlama Servisi", "BLOCKED", "HIGH", "Haftalık raporların otomatik üretimi."),
    ("Ekip İçi Wiki", "COMPLETED", "LOW", "Ekip bilgi tabanı."),
    ("Müşteri Destek Paneli", "PLANNED", "MEDIUM", "Destek taleplerinin tek ekrandan takibi."),
]

# (başlık, durum, öncelik, tip, alt görevler)
TASKS: list[tuple[str, str, str, str, list[tuple[str, str, str, str]]]] = [
    ("Analiz ve tasarım", "TODO", "MEDIUM", "GROUP", [
        ("Tasarım sistemi bileşenleri", "DONE", "MEDIUM", "DESIGN"),
        ("Kullanıcı görüşmeleri", "DONE", "MEDIUM", "RESEARCH"),
    ]),
    ("Geliştirme", "TODO", "MEDIUM", "GROUP", [
        ("Hesap özeti ekranı", "IN_PROGRESS", "HIGH", "TASK"),
        ("Para transferi formu doğrulaması", "IN_PROGRESS", "CRITICAL", "BUG"),
        ("Bildirim izin akışı", "BLOCKED", "HIGH", "TASK"),
        ("Biyometrik giriş", "DONE", "HIGH", "TASK"),
    ]),
    ("Yayın hazırlığı", "TODO", "MEDIUM", "GROUP", [
        ("Beta kullanıcı testleri", "TODO", "HIGH", "TEST"),
        ("Mağaza açıklaması ve görselleri", "TODO", "LOW", "DOCUMENTATION"),
    ]),
]
CHECKLIST_TASK = "Hesap özeti ekranı"
CHECKLIST = [("Bakiye kartı", True), ("Son işlemler listesi", True),
             ("Boş durum ekranı", False), ("Hata mesajları", False)]

# (başlık, öncelik, durum, problem, çözüm)
IDEAS = [
    ("Tablet görünümü", "MEDIUM", "DEFERRED", "Saha ekibi tablet kullanıyor.", "Geniş ekran yerleşimi."),
    ("Sürüm notu üretici", "MEDIUM", "RAW", "Sürüm notları unutuluyor.", "Tamamlanan işlerden taslak çıkar."),
    ("Koyu temalı rapor çıktısı", "LOW", "RAW", "Sunumlarda açık sayfalar göz yoruyor.", "Koyu rapor şablonu."),
    ("Çevrimdışı sayım modu", "CRITICAL", "VALIDATING", "Depoda bağlantı sık kopuyor.", "Yerelde sayım, sonra eşitleme."),
    (FEATURED_IDEA, "HIGH", "REVIEWING", "Kullanıcılar harcamalarını elle etiketliyor.", "İşlem açıklamasından kategori öner."),
]

# Geçmiş yalnızca durumu buna uyan projelere yazılır; diğerlerinde ilerleme %0 kalır.
HISTORY_PROJECTS = ("Stok Takip Sistemi", "Raporlama Servisi", "Ekip İçi Wiki")
# Proje başına açık iş sayısı: tamamlanmış projede sıfır.
OPEN_WORK = {"Stok Takip Sistemi": 14, "Raporlama Servisi": 22,
             "Kurumsal Web Sitesi": 4, "Müşteri Destek Paneli": 3}
WORK_SUBJECTS = ("Sayım ekranı", "Rapor şablonu", "Arama filtresi", "Bildirim metni",
                 "Yetki kontrolü", "Dışa aktarma", "Form doğrulaması", "Hata günlüğü")
WORK_ACTIONS = ("tasarımı", "geliştirmesi", "testi", "incelemesi", "düzeltmesi")

MEMO_TITLE = "Sürüm planı"
MEMO_BODY = "# Sürüm planı\n\n- Beta daveti gönder\n- Geri bildirimleri topla\n- **Cuma** yayın kararı\n"


def seed_database(services: Any, db: Any, today: date) -> None:
    """Boş veritabanını örnek içerikle doldurur."""
    projects = _seed_projects(services)
    _seed_featured_tasks(services, projects[FEATURED_PROJECT])
    _seed_history(services, db, [projects[title] for title in HISTORY_PROJECTS], today)
    _seed_open_work(services, projects)
    # Fikirler oluşturulma sırasıyla listelenir; öne çıkan en üstte olsun diye tersten yazılır.
    for title, priority, status, problem, solution in reversed(IDEAS):
        services.idea.create_idea(
            title, priority=priority, status=status, problem=problem, solution=solution
        )
    services.memo.create(MEMO_TITLE, MEMO_BODY)


def _seed_projects(services: Any) -> dict[str, int]:
    ids: dict[str, int] = {}
    for title, status, priority, description in PROJECTS:
        project = services.project.create_project(
            title, status=status, priority=priority, short_description=description
        )
        ids[title] = project.id
    return ids


def _seed_featured_tasks(services: Any, project_id: int) -> None:
    # Yeni görev listenin başına eklenir; ekrandaki sıra için tersten oluşturulur.
    for title, status, priority, kind, children in reversed(TASKS):
        parent = services.task.create_task(
            project_id, title, status=status, priority=priority, task_type=kind
        )
        for child_title, child_status, child_priority, child_kind in reversed(children):
            child = services.task.create_task(
                project_id, child_title, parent_task_id=parent.id, status=child_status,
                priority=child_priority, task_type=child_kind,
            )
            if child_title == CHECKLIST_TASK:
                _seed_checklist(services, child.id)


def _seed_checklist(services: Any, task_id: int) -> None:
    for index, (text, done) in enumerate(CHECKLIST):
        item = services.task.add_checklist_item(task_id, text, index)
        if done:
            services.task.toggle_checklist_item(item.id)


def _work_title(index: int) -> str:
    return f"{WORK_SUBJECTS[index % len(WORK_SUBJECTS)]} {WORK_ACTIONS[index % len(WORK_ACTIONS)]}"


def _seed_open_work(services: Any, projects: dict[str, int]) -> None:
    for title, count in OPEN_WORK.items():
        for index in range(count):
            services.task.create_task(projects[title], _work_title(index * 3 + 1))


def _seed_history(services: Any, db: Any, project_ids: list[int], today: date) -> None:
    """Son 12 haftaya yayılmış, giderek artan tamamlanmış iş geçmişi."""
    from domain.models.task import Task

    rng = random.Random(7)
    stamps: dict[int, tuple[datetime, datetime]] = {}
    for week in range(HISTORY_WEEKS):
        for number in range(3 + week // 2 + rng.randint(0, 2)):
            days_ago = (HISTORY_WEEKS - 1 - week) * 7 + rng.randint(0, 6)
            done_at = datetime.combine(today - timedelta(days=days_ago), time(12), timezone.utc)
            task = services.task.create_task(
                rng.choice(project_ids), _work_title(week * 7 + number), status="DONE"
            )
            stamps[task.id] = (done_at - timedelta(days=rng.randint(1, 9)), done_at)
    with db.session() as session:
        for task_id, (created_at, completed_at) in stamps.items():
            row = session.get(Task, task_id)
            row.created_at, row.completed_at = created_at, completed_at
