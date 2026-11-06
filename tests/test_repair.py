from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.services.repair import BoundedRepairLoop


def _result(status: str, error: str = "") -> ExecutionResult:
    return ExecutionResult(
        status=status,
        command=["pytest", "-q"],
        image="python:3.12-slim",
        exit_code=0 if status == "passed" else 1,
        stderr=error,
        duration_seconds=0.1,
    )


def test_repair_loop_retries_from_external_failure_and_stops_on_pass() -> None:
    executions = iter([_result("failed", "assertion failed"), _result("passed")])
    applied: list[int] = []

    result = BoundedRepairLoop(max_attempts=2).run(
        next(executions),
        repair=lambda observation, attempt: applied.append(attempt) or observation.status == "failed",
        execute=lambda: next(executions),
    )

    assert result.final_status == "passed"
    assert applied == [1]
    assert result.attempts[0].observation.startswith("execution status=passed")


def test_repair_loop_exhausts_without_infinite_retry() -> None:
    result = BoundedRepairLoop(max_attempts=2).run(
        _result("failed", "still broken"),
        repair=lambda _observation, _attempt: True,
        execute=lambda: _result("failed", "still broken"),
    )

    assert result.final_status == "exhausted"
    assert len(result.attempts) == 2


def test_blocked_execution_is_not_repaired() -> None:
    result = BoundedRepairLoop(max_attempts=3).run(
        _result("blocked", "Docker unavailable"),
        repair=lambda _observation, _attempt: (_ for _ in ()).throw(AssertionError()),
        execute=lambda: _result("passed"),
    )

    assert result.final_status == "blocked"
    assert result.attempts == []
