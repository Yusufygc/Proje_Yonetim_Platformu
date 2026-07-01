from domain.models.note import Note
from infrastructure.repositories.base_repository import ProjectScopedRepository


class NoteRepository(ProjectScopedRepository[Note]):
    """Proje Notları (Note) için veri erişim katmanı."""

    model = Note

    def _project_order(self) -> tuple:
        return (Note.sort_order, Note.id)

    def reorder(self, ordered_ids: list[int]) -> None:
        self._apply_order(ordered_ids, "sort_order")
