from app.llm_feedback import generate_feedback


def test_generate_feedback_falls_back_when_llm_disabled(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "false")

    result = generate_feedback(
        learning_objective="Understand machine learning methods.",
        course_content="The course covers classification and regression.",
        detected_verbs=[
            {
                "verb": "understand",
                "lemma": "understand",
                "known": True,
                "type": "VagueVerb",
                "measurable": False,
                "bloom_category": "unclear",
                "bloom_rank": None,
                "replacement_suggestions": [
                    {
                        "verb": "explain",
                        "bloom_category": "comprehension",
                        "bloom_rank": 2,
                    }
                ],
            }
        ],
        issues=[
            {
                "type": "vague verb",
                "message": "The verb or phrase 'understand' is vague or not measurable.",
            }
        ],
        content_support={
            "status": "supported",
            "score": 0.8,
            "objective_terms": ["machine learning", "method"],
            "course_terms": ["classification", "regression"],
            "matched_terms": ["machine learning"],
            "missing_terms": [],
        },
    )

    assert result["llm_used"] is False
    assert result["explanation"] is not None
    assert result["suggested_rewrite"] is None