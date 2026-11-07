import json

import pytest

from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.services.code_generation import LLMCodeGenerator, MockCodeGenerator
from algo_weaver.services.reproduction import ReproductionPlanner


def _plan():
    capability = AlgorithmCapability(
        name="Moving Average",
        problem_definition="Smooth a time series.",
        algorithm_family="time_series",
        inputs=["data"],
        outputs=["averages"],
        algorithm_steps=["Slide a window."],
        evidence=[EvidenceRef(source_id="doc", excerpt="Moving Average")],
    )
    return ReproductionPlanner().build_plan(capability)


def test_mock_code_generator_labels_deterministic_artifacts() -> None:
    bundle = MockCodeGenerator().generate(_plan())

    assert bundle.plan.generation_mode == "mock"
    assert all(artifact.generation_mode == "mock" for artifact in bundle.artifacts)
    assert bundle.artifacts[0].content_sha256


def test_llm_code_generator_validates_structured_output() -> None:
    class FakeModel:
        def complete_json(self, *, system_prompt: str, user_prompt: str) -> str:
            assert "untrusted data" in system_prompt
            assert "REPRODUCTION_PLAN_JSON" in user_prompt
            return json.dumps(
                {
                    "algorithm_source": "def moving_average(data):\n    return data",
                    "test_source": "def test_smoke():\n    assert True",
                    "dependencies": ["numpy"],
                }
            )

    bundle = LLMCodeGenerator(FakeModel()).generate(_plan())

    assert bundle.plan.generation_mode == "llm"
    assert bundle.plan.dependencies == ["python>=3.12", "numpy"]
    assert bundle.artifacts[0].generation_mode == "llm"
    assert bundle.artifacts[0].path == "algorithm.py"


def test_llm_code_generator_rejects_missing_code_fields() -> None:
    class FakeModel:
        def complete_json(self, *, system_prompt: str, user_prompt: str) -> str:
            del system_prompt, user_prompt
            return json.dumps({"algorithm_source": "pass"})

    with pytest.raises(ValueError):
        LLMCodeGenerator(FakeModel()).generate(_plan())
