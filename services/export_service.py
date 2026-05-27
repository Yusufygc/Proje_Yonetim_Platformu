"""
Export Service - Uygulama verilerinin yedeklenmesi ve dışa aktarılması.
"""
import json
import logging
import shutil
from pathlib import Path
from typing import Any

from sqlalchemy import select

import config
from domain.models.decision_record import DecisionRecord
from domain.models.idea import Idea
from domain.models.note import Note
from domain.models.project import Project
from domain.models.resource import Resource
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ExportService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def backup_database(self, target_path: str) -> None:
        """Mevcut SQLite veritabanını hedef dizine/dosyaya kopyalar."""
        source = config.DATABASE_PATH
        if not source.exists():
            raise FileNotFoundError("Veritabanı dosyası bulunamadı.")
            
        target = Path(target_path)
        shutil.copy2(source, target)
        logger.info("Veritabanı yedeklendi: %s", target)

    def export_to_json(self, target_path: str) -> None:
        """Tüm proje verilerini (ve alt ilişkileri) JSON formatında dışa aktarır."""
        export_data: dict[str, Any] = {"projects": [], "ideas": []}

        with self._db.session() as sess:
            # Fikirler
            for idea in sess.scalars(select(Idea)):
                export_data["ideas"].append({
                    "id": idea.id,
                    "title": idea.title,
                    "description": idea.description,
                    "created_at": idea.created_at.isoformat() if idea.created_at else None
                })

            # Projeler ve alt nesneleri
            for proj in sess.scalars(select(Project)):
                proj_data = {
                    "id": proj.id,
                    "title": proj.title,
                    "description": proj.short_description,
                    "status": proj.status,
                    "tasks": [],
                    "decisions": [],
                    "notes": [],
                    "resources": []
                }
                
                # Görevler
                tasks = sess.scalars(select(Task).where(Task.project_id == proj.id))
                for t in tasks:
                    proj_data["tasks"].append({
                        "id": t.id,
                        "title": t.title,
                        "status": t.status
                    })
                    
                # Kararlar
                decisions = sess.scalars(select(DecisionRecord).where(DecisionRecord.project_id == proj.id))
                for d in decisions:
                    proj_data["decisions"].append({
                        "id": d.id,
                        "title": d.title,
                        "status": d.status
                    })

                # Notlar
                notes = sess.scalars(select(Note).where(Note.project_id == proj.id))
                for n in notes:
                    proj_data["notes"].append({
                        "id": n.id,
                        "title": n.title
                    })

                # Kaynaklar
                resources = sess.scalars(select(Resource).where(Resource.project_id == proj.id))
                for r in resources:
                    proj_data["resources"].append({
                        "id": r.id,
                        "title": r.title,
                        "url": r.url
                    })

                export_data["projects"].append(proj_data)

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)
            
        logger.info("JSON dışa aktarımı tamamlandı: %s", target_path)
