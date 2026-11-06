"""Bounded repair orchestration driven by sandbox observations."""

from __future__ import annotations

from collections.abc import Callable

from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.schemas.repair import RepairAttempt, RepairLoopResult

RepairAction = Callable[[ExecutionResult, int], bool]
ExecuteAction = Callable[[], ExecutionResult]


class BoundedRepairLoop:
    """Coordinate finite repair attempts without executing code itself."""

    def __init__(self, *, max_attempts: int = 3) -> None:
        if max_attempts < 0:
            raise ValueError("max_attempts cannot be negative")
        self.max_attempts = max_attempts

    def run(
        self,
        initial_result: ExecutionResult,
        *,
        repair: RepairAction,
        execute: ExecuteAction,
    ) -> RepairLoopResult:
        if initial_result.status == "passed":
            return RepairLoopResult(final_status="passed", max_attempts=self.max_attempts)
        if initial_result.status == "blocked":
            return RepairLoopResult(final_status="blocked", max_attempts=self.max_attempts)

        attempts: list[RepairAttempt] = []
        current = initial_result
        for attempt_number in range(1, self.max_attempts + 1):
            try:
                applied = repair(current, attempt_number)
            except Exception as exc:
                attempts.append(
                    RepairAttempt(
                        attempt=attempt_number,
                        status="failed",
                        observation=f"repair callback failed: {type(exc).__name__}: {exc}",
                    )
                )
                return RepairLoopResult(
                    final_status="failed", attempts=attempts, max_attempts=self.max_attempts
                )
            if not applied:
                attempts.append(
                    RepairAttempt(
                        attempt=attempt_number,
                        status="failed",
                        observation="repair callback declined to apply a change",
                    )
                )
                return RepairLoopResult(
                    final_status="failed", attempts=attempts, max_attempts=self.max_attempts
                )

            current = execute()
            attempts.append(
                RepairAttempt(
                    attempt=attempt_number,
                    status="applied",
                    observation=_observation(current),
                )
            )
            if current.status == "passed":
                return RepairLoopResult(
                    final_status="passed", attempts=attempts, max_attempts=self.max_attempts
                )
            if current.status == "blocked":
                return RepairLoopResult(
                    final_status="blocked", attempts=attempts, max_attempts=self.max_attempts
                )

        return RepairLoopResult(
            final_status="exhausted", attempts=attempts, max_attempts=self.max_attempts
        )


def _observation(result: ExecutionResult) -> str:
    details = result.error or result.stderr or result.stdout
    return f"execution status={result.status}; {details[:500]}".strip()
