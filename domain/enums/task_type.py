"""Görev tipi enum'u."""
import enum


class TaskType(str, enum.Enum):
    GROUP = "GROUP"
    TASK = "TASK"
    BUG = "BUG"
    RESEARCH = "RESEARCH"
    DESIGN = "DESIGN"
    REVIEW = "REVIEW"
