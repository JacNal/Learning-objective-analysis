from functools import lru_cache

import spacy
from spacy.matcher import Matcher

#Word list is based on Utica's list of Bloom's Taxonomy Action verbs which can be found on page 2 in the link below. Multi word phrases have been removed.
# https://www.utica.edu/academic/Assessment/new/Blooms%20Taxonomy%20-%20Best.pdf
MEASURABLE_VERBS = {
    "arrange": "knowledge",
    "define": "knowledge",
    "describe": "knowledge",
    "duplicate": "knowledge",
    "identify": "knowledge",
    "label": "knowledge",
    "list": "knowledge",
    "match": "knowledge",
    "memorize": "knowledge",
    "name": "knowledge",
    "order": "knowledge",
    "outline": "knowledge",
    "recognize": "knowledge",
    "relate": "knowledge",
    "recall": "knowledge",
    "repeat": "knowledge",
    "reproduce": "knowledge",
    "select": "knowledge",
    "state": "knowledge",

    "classify": "comprehension",
    "convert": "comprehension",
    "defend": "comprehension",
    "describe": "comprehension",
    "discuss": "comprehension",
    "distinguish": "comprehension",
    "estimate": "comprehension",
    "explain": "comprehension",
    "express": "comprehension",
    "extend": "comprehension",
    "generalize": "comprehension",
    "identify": "comprehension",
    "indicate": "comprehension",
    "infer": "comprehension",
    "locate": "comprehension",
    "paraphrase": "comprehension",
    "predict": "comprehension",
    "recognize": "comprehension",
    "rewrite": "comprehension",
    "review": "comprehension",
    "select": "comprehension",
    "summarize": "comprehension",
    "translate": "comprehension",

    
    "apply": "application",
    "change": "application",
    "choose": "application",
    "compute": "application",
    "demonstrate": "application",
    "discover": "application",
    "dramatize": "application",
    "employ": "application",
    "illustrate": "application",
    "interpret": "application",
    "manipulate": "application",
    "modify": "application",
    "operate": "application",
    "practice": "application",
    "predict": "application",
    "prepare": "application",
    "produce": "application",
    "relate": "application",
    "schedule": "application",
    "show": "application",
    "sketch": "application",
    "solve": "application",
    "use": "application",
    "write": "application",
    "implement": "application",

    "analyze": "analysis",
    "appraise": "analysis",
    "calculate": "analysis",
    "categorize": "analysis",
    "compare": "analysis",
    "contrast": "analysis",
    "criticize": "analysis",
    "diagram": "analysis",
    "differentiate": "analysis",
    "discriminate": "analysis",
    "distinguish": "analysis",
    "examine": "analysis",
    "experiment": "analysis",
    "identify": "analysis",
    "illustrate": "analysis",
    "infer": "analysis",
    "model": "analysis",
    "outline": "analysis",
    "question": "analysis",
    "relate": "analysis",
    "select": "analysis",
    "separate": "analysis",
    "subdivide": "analysis",
    "test": "analysis",
    
    "arrange": "synthesis",
    "assemble": "synthesis",
    "categorize": "synthesis",
    "collect": "synthesis",
    "combine": "synthesis",
    "comply": "synthesis",
    "compose": "synthesis",
    "construct": "synthesis",
    "create": "synthesis",
    "design": "synthesis",
    "develop": "synthesis",
    "devise": "synthesis",
    "explain": "synthesis",
    "formulate": "synthesis",
    "generate": "synthesis",
    "plan": "synthesis",
    "prepare": "synthesis",
    "rearrange": "synthesis",
    "reconstruct": "synthesis",
    "relate": "synthesis",
    "reorganize": "synthesis",
    "revise": "synthesis",
    "rewrite": "synthesis",
    "summarize": "synthesis",
    "synthesize": "synthesis",
    "tell": "synthesis",
    "write": "synthesis",
    
    "appraise": "evaluation",
    "argue": "evaluation",
    "assess": "evaluation",
    "attach": "evaluation",
    "choose": "evaluation",
    "compare": "evaluation",
    "conclude": "evaluation",
    "contrast": "evaluation",
    "defend": "evaluation",
    "describe": "evaluation",
    "discriminate": "evaluation",
    "estimate": "evaluation",
    "evaluation": "evaluation",
    "explain": "evaluation",
    "judge": "evaluation",
    "justify": "evaluation",
    "interpret": "evaluation",
    "relate": "evaluation",
    "predict": "evaluation",
    "rate": "evaluation",
    "select": "evaluation",
    "summarize": "evaluation",
    "support": "evaluation",
    "value": "evaluation",
    
}


VAGUE_VERBS = {
    "understand",
    "know",
    "learn",
    "appreciate",
    "believe",
    "hear",
    "realize",
    "capacity",
    "comprehend",
    "see",
    "know",
    "conceptualize",
    "listen",
    "perceive",
    "feel",
}


AUXILIARY_LEMMAS_TO_IGNORE = {
    "be",
    "have",
    "do",
    "will",
    "shall",
    "may",
    "might",
    "can",
    "could",
    "should",
    "would",
    "must",
}


@lru_cache
def get_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError as exc:
        raise RuntimeError(
            "spaCy model 'en_core_web_sm' is not downloaded. "
            "Run: python -m spacy download en_core_web_sm"
        ) from exc


@lru_cache
def get_vague_phrase_matcher():
    nlp = get_nlp()
    matcher = Matcher(nlp.vocab)

    vague_phrase_patterns = {
        "APPRECIATION_FOR": (
            "appreciation for",
            [{"LOWER": "appreciation"}, {"LOWER": "for"}],
        ),
        "ACQUAINTED_WITH": (
            "acquainted with",
            [{"LOWER": "acquainted"}, {"LOWER": "with"}],
        ),
        "ADJUSTED_TO": (
            "adjusted to",
            [{"LOWER": "adjusted"}, {"LOWER": "to"}],
        ),
        "AWARENESS_OF": (
            "awareness of",
            [{"LOWER": "awareness"}, {"LOWER": "of"}],
        ),
        "CAPABLE_OF": (
            "capable of",
            [{"LOWER": "capable"}, {"LOWER": "of"}],
        ),
        "COMPREHENSION_OF": (
            "comprehension of",
            [{"LOWER": "comprehension"}, {"LOWER": "of"}],
        ),
        "COGNIZANT_OF": (
            "cognizant of",
            [{"LOWER": "cognizant"}, {"LOWER": "of"}],
        ),
        "ENJOYMENT_OF": (
            "enjoyment of",
            [{"LOWER": "enjoyment"}, {"LOWER": "of"}],
        ),
        "CONSCIOUS_OF": (
            "conscious of",
            [{"LOWER": "conscious"}, {"LOWER": "of"}],
        ),
        "FAMILIAR_WITH": (
            "familiar with",
            [{"LOWER": "familiar"}, {"LOWER": "with"}],
        ),
        "INTEREST_IN": (
            "interest in",
            [{"LOWER": "interest"}, {"LOWER": "in"}],
        ),
        "INTERESTED_IN": (
            "interested in",
            [{"LOWER": "interested"}, {"LOWER": "in"}],
        ),
        "KNOWLEDGE_OF": (
            "knowledge of",
            [{"LOWER": "knowledge"}, {"LOWER": "of"}],
        ),
        "KNOWLEDGEABLE_ABOUT": (
            "knowledgeable about",
            [{"LOWER": "knowledgeable"}, {"LOWER": "about"}],
        ),
        "UNDERSTANDING_OF": (
            "understanding of",
            [{"LOWER": "understanding"}, {"LOWER": "of"}],
        ),
        "GAIN_INSIGHT_INTO": (
            "gain insight into",
            [{"LEMMA": "gain"}, {"LOWER": "insight"}, {"LOWER": "into"}],
        ),
        "BE_AWARE_OF": (
            "be aware of",
            [{"LEMMA": "be"}, {"LOWER": "aware"}, {"LOWER": "of"}],
        ),
    }

    for label, (_, pattern) in vague_phrase_patterns.items():
        matcher.add(label, [pattern])

    return matcher

def get_known_verb_lemma(token) -> str | None:
    lemma = token.lemma_.lower()
    text = token.text.lower()

    if lemma in MEASURABLE_VERBS or lemma in VAGUE_VERBS:
        return lemma

    if text in MEASURABLE_VERBS or text in VAGUE_VERBS:
        return text

    return None

def classify_verb(lemma: str) -> dict:
    if lemma in MEASURABLE_VERBS:
        return {
            "known": True,
            "measurable": True,
            "bloom_category": MEASURABLE_VERBS[lemma],
        }

    if lemma in VAGUE_VERBS:
        return {
            "known": True,
            "measurable": False,
            "bloom_category": "unclear",
        }

    return {
        "known": False,
        "measurable": None,
        "bloom_category": "unknown",
    }


def get_vague_phrase_labels() -> dict[str, str]:
    return {
        "APPRECIATION_FOR": "appreciation for",
        "ACQUAINTED_WITH": "acquainted with",
        "ADJUSTED_TO": "adjusted to",
        "AWARENESS_OF": "awareness of",
        "CAPABLE_OF": "capable of",
        "COMPREHENSION_OF": "comprehension of",
        "COGNIZANT_OF": "cognizant of",
        "ENJOYMENT_OF": "enjoyment of",
        "CONSCIOUS_OF": "conscious of",
        "FAMILIAR_WITH": "familiar with",
        "INTEREST_IN": "interest in",
        "INTERESTED_IN": "interested in",
        "KNOWLEDGE_OF": "knowledge of",
        "KNOWLEDGEABLE_ABOUT": "knowledgeable about",
        "UNDERSTANDING_OF": "understanding of",
        "GAIN_INSIGHT_INTO": "gain insight into",
        "BE_AWARE_OF": "be aware of",
    }


def extract_vague_phrases(doc) -> list[dict]:
    matcher = get_vague_phrase_matcher()
    matches = matcher(doc)
    phrase_labels = get_vague_phrase_labels()

    extracted = []

    for match_id, start, end in matches:
        label = doc.vocab.strings[match_id]
        canonical = phrase_labels.get(label, doc[start:end].text.lower())

        extracted.append(
            {
                "verb": canonical,
                "lemma": canonical,
                "known": True,
                "measurable": False,
                "bloom_category": "unclear",
            }
        )

    return extracted


def extract_verbs(learning_objective: str) -> list[dict]:
    nlp = get_nlp()
    doc = nlp(learning_objective)

    extracted = []

    extracted.extend(extract_vague_phrases(doc))

    for token in doc:
        known_lemma = get_known_verb_lemma(token)

        is_spacy_verb = token.pos_ == "VERB"
        is_known_first_token = token.i == 0 and known_lemma is not None

        if not is_spacy_verb and not is_known_first_token:
            continue

        lemma = known_lemma or token.lemma_.lower()

        if lemma in AUXILIARY_LEMMAS_TO_IGNORE:
            continue

        classification = classify_verb(lemma)

        extracted.append(
            {
                "verb": token.text.lower(),
                "lemma": lemma,
                "known": classification["known"],
                "measurable": classification["measurable"],
                "bloom_category": classification["bloom_category"],
            }
        )

    return remove_duplicates(extracted)


def remove_duplicates(items: list[dict]) -> list[dict]:
    seen = set()
    unique_items = []

    for item in items:
        key = item["lemma"]

        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return unique_items