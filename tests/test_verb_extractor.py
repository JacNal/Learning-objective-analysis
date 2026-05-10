from app.verb_extractor import extract_verbs


def find_by_lemma(results, lemma):
    for item in results:
        if item["lemma"] == lemma:
            return item

    return None


def test_extracts_measurable_verb():
    result = extract_verbs("Implement a simple classification model.")

    verb = find_by_lemma(result, "implement")

    assert verb is not None
    assert verb["known"] is True
    assert verb["type"] == "MeasurableVerb"
    assert verb["measurable"] is True
    assert verb["bloom_category"] == "application"
    assert verb["bloom_rank"] == 3


def test_extracts_inflected_verb_by_lemma():
    result = extract_verbs("Students implemented a simple classification model.")

    verb = find_by_lemma(result, "implement")

    assert verb is not None
    assert verb["known"] is True
    assert verb["measurable"] is True
    assert verb["bloom_category"] == "application"


def test_extracts_vague_verb():
    result = extract_verbs("Students should understand machine learning methods.")

    verb = find_by_lemma(result, "understand")

    assert verb is not None
    assert verb["known"] is True
    assert verb["measurable"] is False
    assert verb["bloom_category"] == "unclear"


def test_extracts_knowledge_of_phrase():
    result = extract_verbs("Students should have knowledge of regression models.")

    phrase = find_by_lemma(result, "knowledge of")

    assert phrase is not None
    assert phrase["known"] is True
    assert phrase["type"] == "VaguePhrase"
    assert phrase["measurable"] is False
    assert phrase["bloom_category"] == "unclear"
    assert phrase["bloom_rank"] is None
    assert len(phrase["replacement_suggestions"]) > 0


def test_extracts_understanding_of_phrase():
    result = extract_verbs(
        "Students should gain an understanding of classification methods."
    )

    verb = find_by_lemma(result, "understanding of")

    assert verb is not None
    assert verb["known"] is True
    assert verb["measurable"] is False
    assert verb["bloom_category"] == "unclear"


def test_extracts_capable_of_phrase_and_measurable_verb():
    result = extract_verbs(
        "Students should be capable of implementing a simple model."
    )

    vague_phrase = find_by_lemma(result, "capable of")
    measurable_verb = find_by_lemma(result, "implement")

    assert vague_phrase is not None
    assert vague_phrase["known"] is True
    assert vague_phrase["measurable"] is False

    assert measurable_verb is not None
    assert measurable_verb["known"] is True
    assert measurable_verb["measurable"] is True
    assert measurable_verb["bloom_category"] == "application"


def test_extracts_unknown_action_verb():
    result = extract_verbs("Students debug machine learning pipelines.")

    verb = find_by_lemma(result, "debug")

    assert verb is not None
    assert verb["known"] is False
    assert verb["measurable"] is None
    assert verb["bloom_category"] == "unknown"