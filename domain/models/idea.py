from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums.idea_priority import IdeaPriority
from domain.enums.idea_status import IdeaStatus
from infrastructure.database.base_model import Base, TimestampMixin


class Idea(Base, TimestampMixin):
    """Fikir Havuzu için ORM Modeli"""

    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    problem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_user: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expected_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=IdeaStatus.RAW.value
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=IdeaPriority.MEDIUM.value
    )
    
    # Zorluk seviyesi, efor tahmini ve güven seviyesi (Örn: 1-10 arası, ICE/RICE skoru için)
    difficulty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    effort: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Eğer bu fikir bir projeye dönüştüyse o projenin ID'sini tutar
    converted_project_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )

    project_links: Mapped[list["ProjectIdea"]] = relationship(
        "ProjectIdea", back_populates="idea", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Idea id={self.id} title='{self.title}' status={self.status}>"
