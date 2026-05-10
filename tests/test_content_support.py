from app.content_support import extract_keywords, estimate_content_support


def test_extract_keywords_gets_noun_concepts():
    result = extract_keywords(
        "Implement a classification model and evaluate model performance."
    )

    assert "classification" in result
    assert "model" in result
    assert "performance" in result


def test_content_support_supported():
    result = estimate_content_support(
        learning_objective="Implement a classification model.",
        course_content=(
            "The course covers supervised learning, classification, regression, and model evaluation."
        ),
    )

    assert result["status"] == "supported"
    assert result["score"] >= 0.66
    assert "classification" in result["matched_terms"]


def test_content_support_partially_supported():
    result = estimate_content_support(
        learning_objective="Implement a classification model and evaluate neural networks.",
        course_content=(
            "The course covers classification, regression, and model evaluation."
        ),
    )

    assert result["status"] in {"partially supported", "supported"}
    assert "neural network" in result["missing_terms"] or "network" in result["missing_terms"]


def test_content_support_unsupported():
    result = estimate_content_support(
        learning_objective="Analyze bitcoin growth and gambling patterns.",
        course_content=(
            "The course covers regression, classification, and model evaluation."
        ),
    )

    assert result["status"] == "unsupported"
    assert result["score"] < 0.33