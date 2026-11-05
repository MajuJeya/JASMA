import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def _reset_store():
    store.clear()
    yield
    store.clear()


client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert False, "deliberate CI red-test demo"
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readyz():
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_create_and_list_task():
    r = client.post("/tasks", json={"title": "write cv"})
    assert r.status_code == 201
    task = r.json()
    assert task["title"] == "write cv"
    assert task["status"] == "todo"

    r = client.get("/tasks")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_task_404():
    r = client.get("/tasks/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_update_task_status():
    created = client.post("/tasks", json={"title": "ship it"}).json()
    r = client.put(f"/tasks/{created['id']}", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"


def test_update_task_404():
    r = client.put("/tasks/00000000-0000-0000-0000-000000000000", json={"status": "done"})
    assert r.status_code == 404


def test_delete_task():
    created = client.post("/tasks", json={"title": "throwaway"}).json()
    r = client.delete(f"/tasks/{created['id']}")
    assert r.status_code == 204
    r = client.get(f"/tasks/{created['id']}")
    assert r.status_code == 404


def test_delete_task_404():
    r = client.delete("/tasks/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_create_task_validates_title():
    r = client.post("/tasks", json={"title": ""})
    assert r.status_code == 422
