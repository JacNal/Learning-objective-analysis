from fastapi import FastAPI
from app.verb_extractor import extract_verbs
from app.kg import lookup_verb
from app.content_support import estimate_content_support
from app.llm_feedback import generate_feedback

from app.schemas import (
    AnalyseRequest,
    AnalyseResponse,
    ContentSupport,
    DetectedVerb,
    Issue,
    VerbLookupResponse,
    MultiAnalyseRequest,
    MultiAnalyseResponse,
)

app = FastAPI(
    title="Learning Objective Analysis API",
    description="API for analysing learning objectives using NLP, a small knowledge graph, and an LLM-based rewrite component.",
    version="1.0.1 :)",
)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "learning-objective-analysis",
        "version": app.version,
    }

def analyse_one_objective(learning_objective: str, course_content: str) -> AnalyseResponse:
    extracted_verbs = extract_verbs(learning_objective)

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

    support = estimate_content_support(
        learning_objective=learning_objective,
        course_content=course_content,
    )

    if support["status"] == "unsupported":
        issues.append(
            Issue(
                type="not supported",
                message=(
                    "The learning objective contains key terms that aren't clearly supported by the provided course content."
                ),
            )
        )

    elif support["status"] == "partially supported":
        issues.append(
            Issue(
                type="partially supported",
                message=(
                    "The learning objective is only partially supported by the course content."
                ),
            )
        )

    llm_feedback = generate_feedback(
        learning_objective=learning_objective,
        course_content=course_content,
        detected_verbs=detected_verbs,
        issues=issues,
        content_support=support,
    )
    return AnalyseResponse(
        learning_objective=learning_objective,
        detected_verbs=detected_verbs,
        issues=issues,
        content_support=ContentSupport(
            status=support["status"],
            score=support["score"],
            objective_terms=support["objective_terms"],
            course_terms=support["course_terms"],
            matched_terms=support["matched_terms"],
            missing_terms=support["missing_terms"],
        ),
        llm_used=llm_feedback["llm_used"],
        explanation=llm_feedback["explanation"],
        suggested_rewrite=llm_feedback["suggested_rewrite"],
    )

@app.post("/api/v1/analyse", response_model=AnalyseResponse)
def analyse_learning_objective(request: AnalyseRequest):
    return analyse_one_objective(
        learning_objective=request.learning_objective,
        course_content=request.course_content,
    )

@app.post("/api/v1/multi", response_model=MultiAnalyseResponse)
def analyse_multiple_learning_objectives(request: MultiAnalyseRequest):
    results = [
        analyse_one_objective(
            learning_objective=objective,
            course_content=request.course_content,
        )
        for objective in request.learning_objectives
    ]

    return MultiAnalyseResponse(results=results)

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