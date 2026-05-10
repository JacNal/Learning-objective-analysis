import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ["ENABLE_LLM"] = "false"

from app.main import app


DATASET_PATH = Path("data/dtu_examples_test.jsonl")


client = TestClient(app)


def load_examples(path: Path) -> list[dict]:
    examples = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                examples.append(json.loads(line))

    return examples


def call_analyse_endpoint(example: dict) -> dict:
    response = client.post(
        "/api/v1/analyse",
        json={
            "learning_objective": example["learning_objective"],
            "course_content": example["course_content"],
        },
    )

    response.raise_for_status()
    return response.json()


def evaluate_example(example: dict) -> dict:
    result = call_analyse_endpoint(example)

    detected_lemmas = {
        verb["lemma"]
        for verb in result["detected_verbs"]
    }

    detected_issue_types = {
        issue["type"]
        for issue in result["issues"]
    }

    expected_lemmas = set(example["expected_lemmas"])
    expected_issue_types = set(example["expected_issue_types"])

    return {
        "id": example["id"],
        "lemma_match": expected_lemmas.issubset(detected_lemmas),
        "issue_match": expected_issue_types.issubset(detected_issue_types),
        "content_support_match": (
            result["content_support"]["status"]
            == example["expected_content_support"]
        ),
        "expected_lemmas": sorted(expected_lemmas),
        "detected_lemmas": sorted(detected_lemmas),
        "expected_issue_types": sorted(expected_issue_types),
        "detected_issue_types": sorted(detected_issue_types),
        "expected_content_support": example["expected_content_support"],
        "detected_content_support": result["content_support"]["status"],
    }


def calculate_accuracy(rows: list[dict], field: str) -> float:
    if not rows:
        return 0.0

    correct = sum(1 for row in rows if row[field])
    return correct / len(rows)


def main():
    examples = load_examples(DATASET_PATH)
    rows = [evaluate_example(example) for example in examples]

    lemma_accuracy = calculate_accuracy(rows, "lemma_match")
    issue_accuracy = calculate_accuracy(rows, "issue_match")
    support_accuracy = calculate_accuracy(rows, "content_support_match")

    print("Evaluation results")
    print("==================")
    print(f"Examples: {len(rows)}")
    print(f"Verb lemma accuracy: {lemma_accuracy:.2f}")
    print(f"Issue detection accuracy: {issue_accuracy:.2f}")
    print(f"Content-support accuracy: {support_accuracy:.2f}")
    print()

    print("Per-example results")
    print("===================")

    for row in rows:
        print(f"{row['id']}:")
        print(f"  lemma_match: {row['lemma_match']}")
        print(f"  issue_match: {row['issue_match']}")
        print(f"  content_support_match: {row['content_support_match']}")
        print(f"  expected_lemmas: {row['expected_lemmas']}")
        print(f"  detected_lemmas: {row['detected_lemmas']}")
        print(f"  expected_issue_types: {row['expected_issue_types']}")
        print(f"  detected_issue_types: {row['detected_issue_types']}")
        print(f"  expected_content_support: {row['expected_content_support']}")
        print(f"  detected_content_support: {row['detected_content_support']}")
        print()


if __name__ == "__main__":
    main()