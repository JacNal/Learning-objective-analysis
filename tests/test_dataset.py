import json
from pathlib import Path


DATASET_PATH = Path("data/dtu_examples_test.jsonl")


def test_dtu_examples_dataset_exists():
    assert DATASET_PATH.exists()


def test_dtu_examples_dataset_has_required_fields():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        examples = [json.loads(line) for line in file if line.strip()]

    assert len(examples) > 0

    required_fields = {
        "id",
        "source_course_code",
        "source_course_title",
        "source_url",
        "learning_objective",
        "course_content",
        "expected_lemmas",
        "expected_issue_types",
        "expected_content_support",
    }

    for example in examples:
        assert required_fields.issubset(example.keys())
        assert isinstance(example["expected_lemmas"], list)
        assert isinstance(example["expected_issue_types"], list)
        assert example["expected_content_support"] in {
            "supported",
            "partially supported",
            "unsupported",
        }