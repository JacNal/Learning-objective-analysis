from fastapi import FastAPI
from app.verb_extractor import extract_verbs
from app.kg import lookup_verb

from app.schemas import (
    AnalyseRequest,
    AnalyseResponse,
    ContentMatch,
    DetectedVerb,
    Issue,
    VerbLookupResponse,
)

app = FastAPI(
    title="Learning Objective Analysis API",
    description="API for analysing learning objectives using NLP, a small knowledge graph, and an LLM-based rewrite component.",
    version="0.1.1",
)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "learning-objective-analysis",
        "version": app.version,
    }


@app.post("/api/v1/analyse", response_model=AnalyseResponse)
def analyse_learning_objective(request: AnalyseRequest):
    extracted_verbs = extract_verbs(request.learning_objective)

    detected_verbs = [
        DetectedVerb(
            verb=item["verb"],
            lemma=item["lemma"],
            known=item["known"],
            type=item["type"],
            measurable=item["measurable"],
            bloom_category=item["bloom_category"],
            bloom_rank=item["bloom_rank"],
            replacement_suggestions=item["replacement_suggestions"],
        )
        for item in extracted_verbs
    ]

    issues = []
    if not detected_verbs:
        issues.append(
            Issue(
                type="missing action verb",
                message="No action verb was detected in the learning objective.",
            )
        )

    for verb in detected_verbs:
        if not verb.known:
            issues.append(
                Issue(
                    type="unknown verb",
                    message=(
                        f"The verb or phrase '{verb.verb}' was detected, but it is not "
                        "present in the current Bloom verb classification."
                    ),
                )
            )
        elif verb.measurable is False:
            issues.append(
                Issue(
                    type="vague verb",
                    message=(
                        f"The verb or phrase '{verb.verb}' is vague or not measurable."
                    ),
                )
            )

    return AnalyseResponse(
        learning_objective=request.learning_objective,
        detected_verbs=detected_verbs,
        issues=issues,
        content_match=ContentMatch(
            status="not implemented",
            score=0.0,
            matched_terms=[],
        ),
        suggested_rewrite=None,
    )


@app.get("/api/v1/verbs/{verb}", response_model=VerbLookupResponse)
def get_verb_info(verb: str):
    result = lookup_verb(verb)

    return VerbLookupResponse(
        verb=verb.lower().strip(),
        known=result["known"],
        type=result["type"],
        measurable=result["measurable"],
        bloom_category=result["bloom_category"],
        bloom_rank=result["bloom_rank"],
        replacement_suggestions=result["replacement_suggestions"],
    )