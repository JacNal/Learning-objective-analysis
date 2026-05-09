from fastapi import FastAPI

from app.schemas import (
    AnalyseRequest,
    AnalyseResponse,
    ContentMatch,
    DetectedVerb,
    Issue,
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
    return AnalyseResponse(

        learning_objective=request.learning_objective,

        detected_verbs=[
            DetectedVerb(
                verb="placeholder",
                measurable=False,
                bloom_category="unknown",
            )
        ],
        issues=[
            Issue(
                type="not implemented",
                message="No parts of the response is implemented :)",
            )
        ],
        content_match=ContentMatch(
            status="unknown",
            score=0.0,
            matched_terms=[],
        ),
        suggested_rewrite=None,
    )