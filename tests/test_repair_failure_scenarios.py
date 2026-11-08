import subprocess
from pathlib import Path

from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.services.dependency import PythonDependencyAnalyzer
from algo_weaver.services.repair import BoundedRepairLoop
from algo_weaver.services.sandbox import WslDockerSandboxRunner


def _result(status: str, *, error: str = "", stderr: str = "") -> ExecutionResult:
    return ExecutionResult(
        status=status,
        command=["python", "-m", "unittest", "discover"],
        image="python:3.12-slim",
        exit_code=0 if status == "passed" else 1,
        stderr=stderr,
        error=error or None,
        duration_seconds=0.1,
    )


def test_repair_loop_recovers_from_import_error() -> None:
    """A ModuleNotFoundError is an executable failure eligible for repair."""
    observations = iter(
        [
            _result(
                "failed",
                stderr="ModuleNotFoundError: No module named 'generated_helpers'",
            ),
            _result("passed"),
        ]
    )
    seen: list[str] = []

    result = BoundedRepairLoop(max_attempts=1).run(
        next(observations),
        repair=lambda observation, _attempt: seen.append(observation.stderr) or True,
        execute=lambda: next(observations),
    )

    assert result.final_status == "passed"
    assert seen == ["ModuleNotFoundError: No module named 'generated_helpers'"]


def test_dependency_inventory_guides_repair_of_missing_package() -> None:
    """Static dependency analysis preserves the package named by a runtime failure."""
    source = "import pandas as pd\n\ndef run(data):\n    return pd.DataFrame(data)\n"
    report = PythonDependencyAnalyzer().analyze(source, source_id="algorithm.py")
    assert report.parse_error is None
    assert report.third_party == ["pandas"]

    observations = iter(
        [
            _result(
                "failed",
                error="ModuleNotFoundError: No module named 'pandas'",
            ),
            _result("passed"),
        ]
    )

    def repair(observation: ExecutionResult, _attempt: int) -> bool:
        return "pandas" in (observation.error or "") and report.third_party == ["pandas"]

    result = BoundedRepairLoop(max_attempts=1).run(
        next(observations), repair=repair, execute=lambda: next(observations)
    )
    assert result.final_status == "passed"


def test_wsl_timeout_is_repairable_and_remains_bounded(
    tmp_path: Path, monkeypatch
) -> None:
    """A Docker timeout is surfaced as timeout and can trigger one repair attempt."""

    def fake_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="docker run", timeout=0.01)

    monkeypatch.setattr(
        "algo_weaver.services.sandbox._windows_to_wsl_path",
        lambda _path: "/mnt/c/workspace",
    )
    initial = WslDockerSandboxRunner(run_fn=fake_run).run(
        tmp_path, ["python", "-m", "unittest"],
    )
    assert initial.status == "timeout"
    assert "timeout" in (initial.error or "").lower()

    result = BoundedRepairLoop(max_attempts=1).run(
        initial,
        repair=lambda observation, _attempt: observation.status == "timeout",
        execute=lambda: _result("passed"),
    )
    assert result.final_status == "passed"
    assert len(result.attempts) == 1
