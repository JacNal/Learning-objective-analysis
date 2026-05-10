from functools import lru_cache

import spacy


@lru_cache
def get_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError as exc:
        raise RuntimeError(
            "spaCy model 'en_core_web_sm' is not installed. "
            "Run: python -m spacy download en_core_web_sm"
        ) from exc


def normalize_term(term: str) -> str:
    return " ".join(term.lower().strip().split())


def extract_keywords(text: str) -> list[str]:
    nlp = get_nlp()
    doc = nlp(text)

    terms = set()

    for chunk in doc.noun_chunks:
        cleaned_tokens = [
            token.lemma_.lower()
            for token in chunk
            if not token.is_stop
            and not token.is_punct
            and token.pos_ in {"NOUN", "PROPN", "ADJ"}
        ]

        if cleaned_tokens:
            terms.add(normalize_term(" ".join(cleaned_tokens)))

    for token in doc:
        if token.is_stop or token.is_punct:
            continue

        if token.pos_ in {"NOUN", "PROPN", "ADJ"}:
            terms.add(normalize_term(token.lemma_))

    return sorted(term for term in terms if len(term) > 1)


def term_is_supported(objective_term: str, course_terms: set[str]) -> bool:
    if objective_term in course_terms:
        return True

    objective_parts = set(objective_term.split())

    for course_term in course_terms:
        course_parts = set(course_term.split())
        if objective_parts & course_parts:
            return True

    return False


def estimate_content_support(
    learning_objective: str,
    course_content: str,
) -> dict:
    objective_terms = extract_keywords(learning_objective)
    course_terms = extract_keywords(course_content)

    course_term_set = set(course_terms)

    matched_terms = []
    missing_terms = []

    for term in objective_terms:
        if term_is_supported(term, course_term_set):
            matched_terms.append(term)
        else:
            missing_terms.append(term)

    if not objective_terms:
        score = 0.0
    else:
        score = len(matched_terms) / len(objective_terms)

    if score >= 0.5:
        status = "supported"
    elif score >= 0.25:
        status = "partially supported"
    else:
        status = "unsupported"

    return {
        "status": status,
        "score": round(score, 2),
        "objective_terms": objective_terms,
        "course_terms": course_terms,
        "matched_terms": matched_terms,
        "missing_terms": missing_terms,
    }