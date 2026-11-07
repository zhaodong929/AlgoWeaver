import json
from pathlib import Path

import pytest

from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.services.llm_repair import LLMRepairer
from algo_weaver.services.reproduction import ReproductionPlanner, TemplateArtifactWriter


def _bundle():
    capability = AlgorithmCapability(
        name="Moving Average",
        problem_definition="Smooth a time series.",
        algorithm_family="time_series",
        inputs=["data", "window"],
        outputs=["averages"],
        algorithm_steps=["Slide a fixed window."],
        evidence=[EvidenceRef(source_id="repair-doc", excerpt="moving average")],
    )
    return TemplateArtifactWriter().generate(ReproductionPlanner().build_plan(capability))


def _failed_result() -> ExecutionResult:
    return ExecutionResult(
        status="failed",
        command=["python", "-m", "unittest"],
        image="python:3.12-slim",
        exit_code=1,
        stderr="assertion failed",
        duration_seconds=0.1,
    )


def test_llm_repairer_validates_and_applies_one_existing_patch(tmp_path: Path) -> None:
    bundle = _bundle()

    class FakeModel:
        def complete_json(self, *, system_prompt: str, user_prompt: str) -> str:
            assert "untrusted data" in system_prompt
            assert "EXECUTION_OBSERVATION_JSON" in user_prompt
            return json.dumps(
                {
                    "target_path": "algorithm.py",
                    "replacement_source": "def moving_average(data, window):\n    return []\n",
                    "rationale": "restore the reviewed interface",
                }
            )

    TemplateArtifactWriter().write(bundle, tmp_path)
    assert LLMRepairer(FakeModel()).repair(bundle, tmp_path, _failed_result()) is True
    assert (tmp_path / "algorithm.py").read_text(encoding="utf-8").endswith("return []\n")
    assert bundle.artifacts[0].content.endswith("return []\n")
    assert len(bundle.artifacts[0].content_sha256) == 64


def test_llm_repairer_rejects_unknown_or_escaping_targets(tmp_path: Path) -> None:
    bundle = _bundle()

    class FakeModel:
        def __init__(self, target: str) -> None:
            self.target = target

        def complete_json(self, *, system_prompt: str, user_prompt: str) -> str:
            del system_prompt, user_prompt
            return json.dumps(
                {
                    "target_path": self.target,
                    "replacement_source": "pass\n",
                    "rationale": "invalid target test",
                }
            )

    with pytest.raises(ValueError, match="existing artifact"):
        LLMRepairer(FakeModel("missing.py")).repair(bundle, tmp_path, _failed_result())
    with pytest.raises(ValueError, match="existing artifact"):
        LLMRepairer(FakeModel("../outside.py")).repair(bundle, tmp_path, _failed_result())


def test_llm_repairer_does_not_call_model_for_passed_execution(tmp_path: Path) -> None:
    class NeverCalled:
        def complete_json(self, *, system_prompt: str, user_prompt: str) -> str:
            raise AssertionError("model should not be called")

    passed = _failed_result().model_copy(update={"status": "passed", "exit_code": 0})
    assert LLMRepairer(NeverCalled()).repair(_bundle(), tmp_path, passed) is False
