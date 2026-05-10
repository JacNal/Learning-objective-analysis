from app.kg import lookup_verb


def test_lookup_measurable_verb_with_bloom_level():
    result = lookup_verb("implement")

    assert result["known"] is True
    assert result["type"] == "MeasurableVerb"
    assert result["measurable"] is True
    assert result["bloom_category"] == "application"
    assert result["bloom_rank"] == 3
    assert result["replacement_suggestions"] == []


def test_lookup_vague_verb_with_replacement_suggestions():
    result = lookup_verb("understand")

    assert result["known"] is True
    assert result["type"] == "VagueVerb"
    assert result["measurable"] is False
    assert result["bloom_category"] == "unclear"
    assert result["bloom_rank"] is None

    replacement_verbs = {
        suggestion["verb"]
        for suggestion in result["replacement_suggestions"]
    }

    assert "explain" in replacement_verbs
    assert "describe" in replacement_verbs
    assert "compare" in replacement_verbs


def test_lookup_vague_phrase_with_replacement_suggestions():
    result = lookup_verb("knowledge of")

    assert result["known"] is True
    assert result["type"] == "VaguePhrase"
    assert result["measurable"] is False

    replacement_verbs = {
        suggestion["verb"]
        for suggestion in result["replacement_suggestions"]
    }

    assert "define" in replacement_verbs
    assert "identify" in replacement_verbs
    assert "explain" in replacement_verbs


def test_lookup_unknown_verb():
    result = lookup_verb("debug")

    assert result["known"] is False
    assert result["type"] == "unknown"
    assert result["measurable"] is None
    assert result["bloom_category"] == "unknown"
    assert result["bloom_rank"] is None
    assert result["replacement_suggestions"] == []