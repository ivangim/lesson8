import uuid


def test_create_project_positive(client):
    resp = client.request(
        "POST",
        "/api-v2/projects",
        json={"title": "pytest-project-test"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "id" in body
    client.request(
        "PUT",
        f"/api-v2/projects/{body['id']}",
        json={"deleted": True},
    )

def test_create_project_empty_title_negative(client):
    resp = client.request("POST", "/api-v2/projects", json={"title": ""})
    assert resp.status_code == 400, resp.text
    body = resp.json()
    assert "error" in body

def test_get_project_positive(client, created_project):
    resp = client.request(
        "GET",
        f"/api-v2/projects/{created_project['id']}",
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == created_project["id"]

def test_get_nonexistent_project_negative(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.request("GET", f"/api-v2/projects/{fake_id}")
    assert resp.status_code == 404, resp.text

    body = resp.json()
    assert "error" in body, f"В ответе нет поля error: {body}"

    error_text = body["error"].lower()
    assert "not found" in error_text or "не найден" in error_text, (
        f"Неожиданный текст ошибки: {body['error']}"
    )


def test_update_project_positive(client, created_project):
    new_title = f"pytest-project-updated-{uuid.uuid4().hex[:8]}"
    resp = client.request(
        "PUT",
        f"/api-v2/projects/{created_project['id']}",
        json={"title": new_title},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "id" in body, f"В ответе нет поля id: {body}"
    assert body["id"] == created_project["id"]

    check = client.request(
        "GET",
        f"/api-v2/projects/{created_project['id']}",
    )
    assert check.status_code == 200, check.text
    assert check.json()["title"] == new_title


def test_update_nonexistent_project_negative(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.request(
        "PUT",
        f"/api-v2/projects/{fake_id}",
        json={"title": "whatever"},
    )
    assert resp.status_code == 404, resp.text

    body = resp.json()
    assert "error" in body, f"В ответе нет поля error: {body}"

    error_text = body["error"].lower()
    assert "not found" in error_text or "не найден" in error_text, (
        f"Неожиданный текст ошибки: {body['error']}"
    )
