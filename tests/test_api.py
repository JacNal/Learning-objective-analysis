from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "learning-objective-analysis"
    assert data["version"] == app.version


def test_analyse_accepts_valid_request():
    payload = {
        "learning_objective": "Understand machine learning methods.",
        "course_content": "The course covers regression, classification, and model evaluation.",
    }

    response = client.post("/api/v1/analyse", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["learning_objective"] == payload["learning_objective"]
    assert "detected_verbs" in data
    assert "issues" in data
    assert "content_match" in data
    assert "suggested_rewrite" in data

    assert isinstance(data["detected_verbs"], list)
    assert isinstance(data["issues"], list)
    assert isinstance(data["content_match"], dict)


def test_analyse_rejects_missing_course_content():
    payload = {
        "learning_objective": "Understand machine learning methods."
    }

    response = client.post("/api/v1/analyse", json=payload)

    assert response.status_code == 422