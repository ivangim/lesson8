import os
import uuid
import pytest
from CompanyApi import CompanyApi


@pytest.fixture(scope="session")
def client():
    c = CompanyApi("https://ru.yougile.com")
    token = os.getenv("YOUGILE_API_KEY")
    c.get_token()
    if token:
        c._token = token
    return c


@pytest.fixture
def created_project(client):
    title = f"pytest-project-{uuid.uuid4().hex[:8]}"
    resp = client.request("POST", "/api-v2/projects", json={"title": title})
    assert resp.status_code == 201, resp.text
    project = resp.json()

    if "title" not in project:
        full = client.request(
            "GET", f"/api-v2/projects/{project['id']}"
        )
        assert full.status_code == 200, (
            f"Не удалось получить проект: {full.text}"
        )
        project = full.json()

    try:
        yield project
    finally:
        cleanup_resp = client.request(
            "PUT",
            f"/api-v2/projects/{project['id']}",
            json={"deleted": True},
        )
        if cleanup_resp.status_code not in (200, 204, 404):
            print(f"WARN: не удалось удалить проект {project['id']}: "
                  f"{cleanup_resp.status_code} {cleanup_resp.text}")
