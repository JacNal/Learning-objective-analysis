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
    assert data["content_support"]["status"] in {
        "supported",
        "partially_supported",
        "unsupported",
    }
    assert "matched_terms" in data["content_support"]
    assert "missing_terms" in data["content_support"]
    assert "objective_terms" in data["content_support"]
    assert "course_terms" in data["content_support"]
    assert "llm_used" in data
    assert "explanation" in data
    assert "suggested_rewrite" in data


def test_analyse_rejects_missing_course_content():
    payload = {
        "learning_objective": "Students should understand machine learning methods."
    }

    response = client.post("/api/v1/analyse", json=payload)

    assert response.status_code == 422


def test_verb_lookup_known_measurable_verb():
    response = client.get("/api/v1/verbs/implement")

    assert response.status_code == 200

    data = response.json()

    assert data["verb"] == "implement"
    assert data["known"] is True
    assert data["type"] == "MeasurableVerb"
    assert data["measurable"] is True
    assert data["bloom_category"] == "application"
    assert data["bloom_rank"] == 3
    assert data["replacement_suggestions"] == []


def test_verb_lookup_vague_verb_has_replacement_suggestions():
    response = client.get("/api/v1/verbs/understand")

    assert response.status_code == 200

    data = response.json()

    assert data["verb"] == "understand"
    assert data["known"] is True
    assert data["type"] == "VagueVerb"
    assert data["measurable"] is False
    assert data["bloom_category"] == "unclear"
    assert data["bloom_rank"] is None

    replacement_verbs = {
        suggestion["verb"]
        for suggestion in data["replacement_suggestions"]
    }

    assert "explain" in replacement_verbs
    assert "describe" in replacement_verbs
    assert "compare" in replacement_verbs


def test_verb_lookup_unknown_verb():
    response = client.get("/api/v1/verbs/debug")

    assert response.status_code == 200

    data = response.json()

    assert data["verb"] == "debug"
    assert data["known"] is False
    assert data["type"] == "unknown"
    assert data["measurable"] is None
    assert data["bloom_category"] == "unknown"
    assert data["bloom_rank"] is None
    assert data["replacement_suggestions"] == []