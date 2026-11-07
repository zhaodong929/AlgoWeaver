from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.services.validation import ValidationService


def _capability(status: str = "draft") -> AlgorithmCapability:
    return AlgorithmCapability(
        name="Moving Average",
        problem_definition="Smooth a time series.",
        inputs=["data"],
        outputs=["smoothed"],
        algorithm_steps=["Slide a fixed window."],
        evidence=[
            EvidenceRef(
                source_id="doc-001",
                source_type="document",
                excerpt="Moving average smooths a time series.",
            )
        ],
        status=status,
    )


def test_capability_validation_is_partial_until_independent_verification() -> None:
    report = ValidationService().validate_capability(_capability())

    assert report.target_type == "capability"
    assert report.overall_status == "partial"
    assert report.passed_count == 2
    assert report.skipped_count == 1


def test_missing_capability_evidence_fails_contract_check() -> None:
    capability = _capability()
    capability.evidence = []

    report = ValidationService().validate_capability(capability)

    assert report.overall_status == "failed"
    assert report.failed_count == 1


def test_python_source_is_parsed_without_execution() -> None:
    report = ValidationService().validate_python_source(
        "def predict(data):\n    return data\n",
        source_id="generated.py",
        required_function="predict",
    )

    assert report.overall_status == "passed"
    assert report.passed_count == 2


def test_invalid_python_and_missing_entrypoint_are_reported() -> None:
    service = ValidationService()
    syntax_report = service.validate_python_source("def broken(:\n", source_id="bad.py")
    entrypoint_report = service.validate_python_source(
        "def other(data):\n    return data\n",
        source_id="other.py",
        required_function="predict",
    )

    assert syntax_report.overall_status == "failed"
    assert entrypoint_report.overall_status == "failed"


def test_runtime_report_can_promote_complete_draft_after_sandbox_passes() -> None:
    capability = _capability()
    execution = ExecutionResult(
        status="passed",
        command=["pytest", "-q"],
        image="python:3.12-slim",
        exit_code=0,
        duration_seconds=0.2,
    )

    report = ValidationService().build_runtime_report(capability, execution)

    assert report.target_type == "capability"
    assert report.target_id == capability.capability_id
    assert report.overall_status == "passed"


def test_runtime_report_rejects_review_pending_or_blocked_execution() -> None:
    capability = _capability(status="needs_review")
    execution = ExecutionResult(
        status="blocked",
        command=["pytest", "-q"],
        image="python:3.12-slim",
        duration_seconds=0,
        error="Docker unavailable",
    )

    report = ValidationService().build_runtime_report(capability, execution)

    assert report.overall_status == "failed"


def test_runtime_report_revalidates_an_existing_verified_capability() -> None:
    capability = _capability().model_copy(update={"status": "verified"})
    execution = ExecutionResult(
        status="passed",
        command=["pytest", "-q"],
        image="python:3.12-slim",
        exit_code=0,
        duration_seconds=0.1,
    )

    report = ValidationService().build_runtime_report(capability, execution)

    assert report.overall_status == "passed"
