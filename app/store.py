from datetime import datetime, timezone
from uuid import UUID
from app.models import Task, TaskCreate, TaskUpdate


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[UUID, Task] = {}

    def list(self) -> list[Task]:
        return list(self._tasks.values())

    def get(self, task_id: UUID) -> Task | None:
        return self._tasks.get(task_id)

    def create(self, data: TaskCreate) -> Task:
        task = Task(**data.model_dump())
        self._tasks[task.id] = task
        return task

    def update(self, task_id: UUID, data: TaskUpdate) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        patch = data.model_dump(exclude_unset=True)
        updated = task.model_copy(update={**patch, "updated_at": datetime.now(timezone.utc)})
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: UUID) -> bool:
        return self._tasks.pop(task_id, None) is not None

    def clear(self) -> None:
        self._tasks.clear()


store = TaskStore()
