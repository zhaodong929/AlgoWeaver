"""Pydantic schemas used by AlgoWeaver."""
from algo_weaver.schemas.code import PythonSourceFile
from algo_weaver.schemas.comparison import (
    AlgorithmComparisonReport,
    CandidateResult,
    ForecastCandidateResult,
    InventoryForecastComparisonReport,
)
from algo_weaver.schemas.dependency import DependencyReport
from algo_weaver.schemas.execution import ExecutionPolicy, ExecutionResult
from algo_weaver.schemas.failure import RepairFailureRecord
from algo_weaver.schemas.ingestion import IngestedSource, IngestionBatch
from algo_weaver.schemas.metrics import MetricReport, MetricResult
from algo_weaver.schemas.registry import CapabilityVersion
from algo_weaver.schemas.repair import RepairAttempt, RepairLoopResult, RepairPatch
from algo_weaver.schemas.reproduction import GeneratedArtifact, ReproductionPlan
from algo_weaver.schemas.retrieval import (
    EvidenceChunk,
    RerankResult,
    RetrievalCase,
    RetrievalCaseResult,
    RetrievalEvaluation,
    RetrievalHit,
)
from algo_weaver.schemas.validation import ValidationCheck, ValidationReport

__all__ = [
    "CapabilityVersion",
    "AlgorithmComparisonReport",
    "CandidateResult",
    "DependencyReport",
    "EvidenceChunk",
    "ExecutionPolicy",
    "ExecutionResult",
    "ForecastCandidateResult",
    "IngestedSource",
    "IngestionBatch",
    "InventoryForecastComparisonReport",
    "MetricReport",
    "MetricResult",
    "PythonSourceFile",
    "RepairAttempt",
    "RepairLoopResult",
    "RepairPatch",
    "RepairFailureRecord",
    "GeneratedArtifact",
    "ReproductionPlan",
    "RetrievalHit",
    "RetrievalCase",
    "RetrievalCaseResult",
    "RetrievalEvaluation",
    "RerankResult",
    "ValidationCheck",
    "ValidationReport",
]
