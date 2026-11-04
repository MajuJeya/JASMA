import logging
from uuid import UUID
from fastapi import FastAPI, HTTPException, status
from app.logging_config import configure_logging
from app.models import Task, TaskCreate, TaskUpdate
from app.store import store

configure_logging()
log = logging.getLogger("jasma")

app = FastAPI(title="JASMA Task API", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    return store.list()


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    task = store.create(payload)
    log.info("task.created", extra={"task_id": str(task.id)})
    return task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: UUID) -> Task:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: UUID, payload: TaskUpdate) -> Task:
    task = store.update(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    log.info("task.updated", extra={"task_id": str(task_id)})
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID) -> None:
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="task not found")
    log.info("task.deleted", extra={"task_id": str(task_id)})
