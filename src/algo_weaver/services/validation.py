"""Safe, deterministic validation without executing generated code."""

from __future__ import annotations

import ast
import hashlib

from algo_weaver.schemas.capability import AlgorithmCapability
from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.schemas.validation import (
    ReportStatus,
    ValidationCheck,
    ValidationReport,
    ValidationTarget,
)


class ValidationService:
    """Run contract and static checks that are safe to execute on the host."""

    def validate_capability(self, capability: AlgorithmCapability) -> ValidationReport:
        checks = [
            self._check_required_fields(capability),
            self._check_evidence(capability),
            self._check_review_state(capability),
        ]
        return _report("capability", capability.capability_id, checks)

    def validate_python_source(
        self,
        source: str,
        *,
        source_id: str | None = None,
        required_function: str | None = None,
    ) -> ValidationReport:
        target_id = source_id or f"sha256:{hashlib.sha256(source.encode('utf-8')).hexdigest()}"
        checks: list[ValidationCheck] = []
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            checks.append(
                ValidationCheck(
                    check_id="python.syntax",
                    name="Python syntax",
                    status="failed",
                    message=f"Source is not valid Python: {exc.msg}",
                    details={"line": exc.lineno or 0, "column": exc.offset or 0},
                )
            )
            return _report("python_source", target_id, checks)

        checks.append(
            ValidationCheck(
                check_id="python.syntax",
                name="Python syntax",
                status="passed",
                message="Source parses successfully without executing it.",
            )
        )
        if required_function is None:
            checks.append(
                ValidationCheck(
                    check_id="python.entrypoint",
                    name="Required entrypoint",
                    status="skipped",
                    message="No required function was supplied.",
                )
            )
        else:
            functions = {
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            found = required_function in functions
            checks.append(
                ValidationCheck(
                    check_id="python.entrypoint",
                    name="Required entrypoint",
                    status="passed" if found else "failed",
                    message=(
                        f"Function '{required_function}' is defined."
                        if found
                        else f"Function '{required_function}' is not defined."
                    ),
                    details={"required_function": required_function},
                )
            )
        return _report("python_source", target_id, checks)

    def build_runtime_report(
        self,
        capability: AlgorithmCapability,
        execution: ExecutionResult,
        artifact_reports: list[ValidationReport] | None = None,
    ) -> ValidationReport:
        """Combine contract, artifact and sandbox evidence for verified promotion."""
        checks = [
            self._check_required_fields(capability),
            self._check_evidence(capability),
            ValidationCheck(
                check_id="capability.review_state",
                name="Review state",
                status="passed" if capability.status in {"draft", "verified"} else "failed",
                message=(
                    "Capability is a complete draft eligible for independent runtime verification."
                    if capability.status == "draft"
                    else "Capability is already verified and passed runtime revalidation."
                    if capability.status == "verified"
                    else f"Capability status '{capability.status}' still requires review."
                ),
            ),
            ValidationCheck(
                check_id="sandbox.execution",
                name="Sandbox execution",
                status="passed" if execution.status == "passed" else "failed",
                message=(
                    "Sandbox command completed successfully."
                    if execution.status == "passed"
                    else f"Sandbox execution status is '{execution.status}'."
                ),
                details={"exit_code": execution.exit_code or -1},
            ),
            ValidationCheck(
                check_id="sandbox.duration",
                name="Sandbox duration metric",
                status="passed" if execution.status == "passed" else "failed",
                message=f"Sandbox wall time: {execution.duration_seconds:.3f} seconds.",
                details={"duration_seconds": execution.duration_seconds},
            ),
        ]
        for report in artifact_reports or []:
            checks.append(
                ValidationCheck(
                    check_id=f"artifact.{report.target_id}",
                    name=f"Artifact checks: {report.target_id}",
                    status="passed" if report.overall_status == "passed" else "failed",
                    message=f"Artifact report status is '{report.overall_status}'.",
                )
            )
        return _report("capability", capability.capability_id, checks)

    @staticmethod
    def _check_required_fields(capability: AlgorithmCapability) -> ValidationCheck:
        required = {
            "problem_definition": bool(capability.problem_definition.strip()),
            "inputs": bool(capability.inputs),
            "outputs": bool(capability.outputs),
            "algorithm_steps": bool(capability.algorithm_steps),
        }
        missing = [name for name, present in required.items() if not present]
        return ValidationCheck(
            check_id="capability.required_fields",
            name="Required capability fields",
            status="passed" if not missing else "failed",
            message=(
                "All required capability fields are populated."
                if not missing
                else "Missing required capability fields."
            ),
            details={"missing": ",".join(missing)},
        )

    @staticmethod
    def _check_evidence(capability: AlgorithmCapability) -> ValidationCheck:
        valid = bool(capability.evidence) and all(
            evidence.source_id.strip() and evidence.excerpt.strip()
            for evidence in capability.evidence
        )
        return ValidationCheck(
            check_id="capability.evidence",
            name="Evidence provenance",
            status="passed" if valid else "failed",
            message=(
                "At least one source evidence reference is attached."
                if valid
                else "A non-empty source evidence reference is required."
            ),
            details={"evidence_count": len(capability.evidence)},
        )

    @staticmethod
    def _check_review_state(capability: AlgorithmCapability) -> ValidationCheck:
        if capability.status == "verified":
            return ValidationCheck(
                check_id="capability.review_state",
                name="Independent verification state",
                status="passed",
                message="Capability is marked verified by an upstream verification workflow.",
            )
        return ValidationCheck(
            check_id="capability.review_state",
            name="Independent verification state",
            status="skipped",
            message=f"Capability status is '{capability.status}'; independent verification is pending.",
        )


def _report(
    target_type: ValidationTarget,
    target_id: str,
    checks: list[ValidationCheck],
) -> ValidationReport:
    statuses = {check.status for check in checks}
    if "failed" in statuses:
        overall: ReportStatus = "failed"
    elif "skipped" in statuses:
        overall = "partial"
    else:
        overall = "passed"
    return ValidationReport(
        target_type=target_type,
        target_id=target_id,
        checks=checks,
        overall_status=overall,
    )
