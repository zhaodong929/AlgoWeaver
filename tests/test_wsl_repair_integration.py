import shutil
import sys
from pathlib import Path

import pytest

from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.services.repair import BoundedRepairLoop
from algo_weaver.services.reproduction import ReproductionPlanner, TemplateArtifactWriter
from algo_weaver.services.sandbox import WslDockerSandboxRunner
from algo_weaver.services.template_repair import TemplateRepairer

pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or shutil.which("wsl.exe") is None,
    reason="Windows WSL runtime unavailable",
)


def test_wsl_runtime_repair_loop_recovers_from_controlled_failure(tmp_path: Path) -> None:
    capability = AlgorithmCapability(
        name="Moving Average",
        problem_definition="Smooth a time series.",
        algorithm_family="time_series",
        inputs=["data", "window"],
        outputs=["averages"],
        algorithm_steps=["Slide a fixed window."],
        evidence=[EvidenceRef(source_id="repair-doc", excerpt="moving average")],
    )
    bundle = TemplateArtifactWriter().generate(ReproductionPlanner().build_plan(capability))
    TemplateArtifactWriter().write(bundle, tmp_path)
    (tmp_path / "algorithm.py").write_text(
        "def moving_average(data, window):\n    return []\n", encoding="utf-8"
    )
    runner = WslDockerSandboxRunner()
    command = ["python", "-m", "unittest", "discover", "-v"]

    initial = runner.run(tmp_path, command)
    loop = BoundedRepairLoop(max_attempts=2)
    result = loop.run(
        initial,
        repair=lambda observation, _attempt: TemplateRepairer().repair(
            bundle, tmp_path, observation
        ),
        execute=lambda: runner.run(tmp_path, command),
    )

    assert initial.status == "failed"
    assert result.final_status == "passed"
    assert len(result.attempts) == 1
