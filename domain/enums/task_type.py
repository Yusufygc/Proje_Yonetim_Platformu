"""Görev tipi enum'u."""
import enum


class TaskType(str, enum.Enum):
    GROUP = "GROUP"
    TASK = "TASK"
    BUG = "BUG"
    IMPROVEMENT = "IMPROVEMENT"
    RESEARCH = "RESEARCH"
    DOCUMENTATION = "DOCUMENTATION"
    DESIGN = "DESIGN"
    TEST = "TEST"
    REVIEW = "REVIEW"
