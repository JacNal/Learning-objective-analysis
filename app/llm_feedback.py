import json
import os
from functools import lru_cache
from typing import Any

import dspy
from dotenv import load_dotenv


class LearningObjectiveFeedback(dspy.Signature):
    learning_objective: str = dspy.InputField()
    course_content: str = dspy.InputField()
    detected_verbs_json: str = dspy.InputField()
    issues_json: str = dspy.InputField()
    content_support_json: str = dspy.InputField()

    explanation: str = dspy.OutputField(
        desc=(
            "A short explanation of the main problems or strengths of the learning objective. Use 1-2 sentences."
        )
    )
    suggested_rewrite: str = dspy.OutputField(
        desc=(
            "One improved learning objective. It should use a measurable action verb when possible and stay aligned with the course content."
        )
    )


@lru_cache
def get_feedback_program():
    return dspy.Predict(LearningObjectiveFeedback)


def llm_is_enabled() -> bool:
    load_dotenv()

    return os.getenv("ENABLE_LLM", "false").lower() == "true"


def configure_dspy() -> bool:
    load_dotenv()

    if not llm_is_enabled():
        return False

    api_key = os.getenv("CAMPUSAI_API_KEY")
    api_base = os.getenv("CAMPUSAI_API_URL")
    model = os.getenv("CAMPUSAI_MODEL")

    if not api_key or not api_base or not model: #or api_base != "https://api.campusai.compute.dtu.dk/v1" or model not in {"Gemma 4"}:
        return False

    lm = dspy.LM(
        f"openai/{model}",
        api_key=api_key,
        api_base=api_base,
        model_type="chat",
        temperature=0.2,
        max_tokens=1000,
        cache=False,
    )

    dspy.configure(lm=lm)
    return True


def generate_feedback(learning_objective: str, course_content: str, detected_verbs: list[Any], issues: list[Any], content_support: dict) -> dict:
    
    if llm_is_enabled():
        if configure_dspy() != True:
            return fallback_feedback(
                detected_verbs=detected_verbs,
                issues=issues,
                content_support=content_support,
            )

        try:
            program = get_feedback_program()

            response = program(
                learning_objective=learning_objective,
                course_content=course_content,
                detected_verbs_json=to_json(detected_verbs),
                issues_json=to_json(issues),
                content_support_json=to_json(content_support),
            )

            return {
                "llm_used": True,
                "explanation": clean_text(response.explanation),
                "suggested_rewrite": clean_text(response.suggested_rewrite),
            }

        except Exception:
            return fallback_feedback(
                detected_verbs=detected_verbs,
                issues=issues,
                content_support=content_support,
            )
    else:
        return fallback_feedback(
                detected_verbs=detected_verbs,
                issues=issues,
                content_support=content_support,
        )



def fallback_feedback(detected_verbs: list[Any], issues: list[Any], content_support: dict) -> dict:
    issue_types = extract_issue_types(issues)

    explanation_parts = []

    if "vague verb" in issue_types:
        explanation_parts.append(
            "The learning objective contains vague wording that may be difficult to measure."
        )

    if "unknown verb" in issue_types:
        explanation_parts.append(
            "At least one detected action verb isn't present in the current Bloom verb graph."
        )

    if "missing action verb" in issue_types:
        explanation_parts.append(
            "No clear action verb was detected in the learning objective."
        )

    if content_support["status"] == "unsupported":
        explanation_parts.append(
            "The objective doesn't appear to be clearly supported by the course content."
        )

    elif content_support["status"] == "partially supported":
        explanation_parts.append(
            "The objective appears to be only partially supported by the course content."
        )

    if not explanation_parts:
        explanation_parts.append(
            "The learning objective appears to use measurable wording and is reasonably aligned with the course content."
        )

    return {
        "llm_used": False,
        "explanation": " ".join(explanation_parts),
        "suggested_rewrite": None,
    }


def extract_issue_types(issues: list[Any]) -> set[str]:
    issue_types = set()

    for issue in issues:
        if hasattr(issue, "type"):
            issue_types.add(issue.type)
        elif isinstance(issue, dict) and "type" in issue:
            issue_types.add(issue["type"])

    return issue_types


def to_json(value: Any) -> str:
    def default(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()

        if hasattr(obj, "dict"):
            return obj.dict()

        return str(obj)

    return json.dumps(value, default=default, ensure_ascii=False, indent=2)


def clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text