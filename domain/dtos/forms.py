"""Form DTOs used between presentation controllers and services."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProjectCreateDTO:
    title: str
    values: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Proje basligi bos olamaz.")


@dataclass(slots=True)
class ProjectUpdateDTO:
    values: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IdeaCreateDTO:
    title: str
    values: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Fikir basligi bos olamaz.")


@dataclass(slots=True)
class IdeaUpdateDTO:
    values: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TaskCreateDTO:
    project_id: int
    title: str
    values: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Gorev basligi bos olamaz.")


@dataclass(slots=True)
class TaskUpdateDTO:
    values: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DecisionCreateDTO:
    project_id: int
    title: str
    decision: str
    values: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.decision = self.decision.strip()
        if not self.title:
            raise ValueError("Karar basligi bos olamaz.")
        if not self.decision:
            raise ValueError("Karar metni bos olamaz.")


@dataclass(slots=True)
class DecisionUpdateDTO:
    values: dict[str, Any] = field(default_factory=dict)
