from fastapi import FastAPI

app = FastAPI(
    title="Learning Objective Analysis API",
    description="API for analysing learning objectives using NLP, a small knowledge graph, and an LLM-based rewrite component.",
    version="0.1.0",
)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "learning-objective-analysis",
        "version": "0.1.0",
    }
