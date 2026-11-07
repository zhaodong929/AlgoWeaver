"""Conservative deterministic repair action for generated template artifacts."""

from __future__ import annotations

from pathlib import Path

from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.schemas.reproduction import ReproductionBundle
from algo_weaver.services.reproduction import TemplateArtifactWriter


class TemplateRepairer:
    """Restore only the files belonging to a reviewed template bundle."""

    def repair(
        self,
        bundle: ReproductionBundle,
        workspace: str | Path,
        observation: ExecutionResult,
    ) -> bool:
        if observation.status not in {"failed", "timeout"}:
            return False
        destination = Path(workspace).resolve()
        destination.mkdir(parents=True, exist_ok=True)
        for artifact in bundle.artifacts:
            target = (destination / artifact.path).resolve()
            if destination not in target.parents:
                raise ValueError("artifact path escapes repair workspace")
        TemplateArtifactWriter().write(bundle, destination)
        return True
