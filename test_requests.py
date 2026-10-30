import uuid
import pytest
from CompanyApi import CompanyApi


@pytest.fixture(scope="session")
def client():
    c = CompanyApi("https://ru.yougile.com")
    c.get_token()
    return c


@pytest.fixture
def created_project(client):
    title = f"pytest-project-{uuid.uuid4().hex[:8]}"
    resp = client.request("POST", "/api-v2/projects", json={"title": title})
    assert resp.status_code == 201, resp.text
    project = resp.json()
    if "title" not in project:
        full = client.request("GET", f"/api-v2/projects/{project['id']}")
        if full.status_code == 200:
            project = full.json()
    try:
        yield project
    finally:
        r = client.request("DELETE", f"/api-v2/projects/{project['id']}")
        if r.status_code not in (200, 204, 404):
            print(f"WARN: не удалось удалить проект {project['id']}: {r.status_code} {r.text}")


def test_create_project_positive(created_project):
    assert "id" in created_project
    #assert created_project["title"] == "pytest-project"
def test_debug_create(client):
    resp = client.request("POST", "/api-v2/projects", json={"title": "debug-project"})
    print(resp.status_code, resp.json())


def test_create_project_empty_title_negative(client):
    """Негативный: пустой title должен вернуть 400."""
    resp = client.request("POST", "/api-v2/projects", json={"title": ""})
    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert "error" in body


def test_get_project_positive(client, created_project):
    resp = client.request("GET", f"/api-v2/projects/{created_project['id']}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == created_project["id"]


def test_get_nonexistent_project_negative(client):
    resp = client.request("GET", "/api-v2/projects/00000000-0000-0000-0000-000000000000")
    assert resp.status_code in (404, 400), resp.text


def test_update_project_positive(client, created_project):
    new_title = f"pytest-project-updated-{uuid.uuid4().hex[:8]}"
    resp = client.request(
        "PUT",
        f"/api-v2/projects/{created_project['id']}",
        json={"title": new_title},
    )
    assert resp.status_code == 200, resp.text
    check = client.request("GET", f"/api-v2/projects/{created_project['id']}")
    assert check.json()["title"] == new_title

    def test_get_token_invalid_company_id_negative():
        client = CompanyApi()
        with pytest.raises(RuntimeError, match="400"):
            client.get_token(company_id="not-a-uuid")