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
        "learning_objective": "Students should understand machine learning methods.",
        "course_content": "The course covers regression, classification, and model evaluation.",
    }

    response = client.post("/api/v1/analyse", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["learning_objective"] == payload["learning_objective"]
    assert data["detected_verbs"][0]["lemma"] == "understand"
    assert data["detected_verbs"][0]["known"] is True
    assert data["detected_verbs"][0]["measurable"] is False
    assert data["detected_verbs"][0]["bloom_category"] == "unclear"

    assert data["issues"][0]["type"] == "vague verb"
    assert data["content_match"]["status"] == "not implemented"
    assert data["suggested_rewrite"] is None


def test_analyse_rejects_missing_course_content():
    payload = {
        "learning_objective": "Students should understand machine learning methods."
    }

    response = client.post("/api/v1/analyse", json=payload)

    assert response.status_code == 422