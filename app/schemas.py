from pydantic import BaseModel, Field


class AnalyseRequest(BaseModel):
    learning_objective: str = Field(
        ...,
        min_length=1,
        description="The learning objective to analyse.",
    )
    course_content: str = Field(
        ...,
        min_length=1,
        description="The course description or course content.",
    )

class ReplacementSuggestion(BaseModel):
    verb: str
    bloom_category: str
    bloom_rank: int

class DetectedVerb(BaseModel):
    verb: str
    lemma: str
    known: bool
    type: str
    measurable: bool | None
    bloom_category: str
    bloom_rank: int | None
    replacement_suggestions: list[ReplacementSuggestion]

class VerbLookupResponse(BaseModel):
    verb: str
    known: bool
    type: str
    measurable: bool | None
    bloom_category: str
    bloom_rank: int | None
    replacement_suggestions: list[ReplacementSuggestion]


class Issue(BaseModel):
    type: str
    message: str


class ContentMatch(BaseModel):
    status: str
    score: float
    matched_terms: list[str]


class AnalyseResponse(BaseModel):
    learning_objective: str
    detected_verbs: list[DetectedVerb]
    issues: list[Issue]
    content_match: ContentMatch
    suggested_rewrite: str | None