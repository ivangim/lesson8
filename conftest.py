import pytest
from CompanyApi import CompanyApi


@pytest.fixture(scope="session")
def client():
    c = CompanyApi("https://ru.yougile.com")
    c.get_token()
    return c


@pytest.fixture
def created_project(client):
    """Создаёт проект, отдаёт объект, удаляет после теста."""
    resp = client.request("POST", "/api-v2/projects", json={"title": "pytest-project"})
    assert resp.status_code == 201, resp.text
    project = resp.json()
    yield project
    client.request("DELETE", f"/api-v2/projects/{project['id']}")