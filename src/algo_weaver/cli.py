"""Command-line interface for AlgoWeaver."""

import csv
import json
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint

from algo_weaver.config import get_settings
from algo_weaver.llm.factory import create_chat_model
from algo_weaver.schemas.execution import ExecutionPolicy
from algo_weaver.services.capability_extractor import CapabilityExtractor
from algo_weaver.services.code_generation import LLMCodeGenerator, MockCodeGenerator
from algo_weaver.services.dependency import PythonDependencyAnalyzer
from algo_weaver.services.ingestion import SourceIngestor
from algo_weaver.services.llm_repair import LLMRepairer
from algo_weaver.services.metrics import RegressionMetricEvaluator
from algo_weaver.services.registry import CapabilityRegistry
from algo_weaver.services.repair import BoundedRepairLoop
from algo_weaver.services.reproduction import ReproductionPlanner, TemplateArtifactWriter
from algo_weaver.services.retrieval import LocalLexicalRetriever, SourceChunker
from algo_weaver.services.sandbox import DockerSandboxRunner, WslDockerSandboxRunner
from algo_weaver.services.template_repair import TemplateRepairer
from algo_weaver.services.validation import ValidationService

app = typer.Typer(
    name="algo-weaver",
    help="Algorithm knowledge extraction and reproduction agent.",
    no_args_is_help=True,
)


@app.command()
def extract(
    input_file: Annotated[Path, typer.Option("--input", "-i", exists=True, readable=True)],
    output_file: Annotated[Path, typer.Option("--output", "-o")] = Path("data/processed/capability.json"),
    source_id: Annotated[str, typer.Option("--source-id")] = "local-input-001",
    source_type: Annotated[str, typer.Option("--source-type")] = "document",
    mode: Annotated[str | None, typer.Option("--mode", help="mock or litellm; defaults to .env settings")] = None,
) -> None:
    """Extract an algorithm capability card from a UTF-8 text/Markdown file."""
    settings = get_settings()
    if mode is not None:
        if mode not in {"mock", "litellm"}:
            raise typer.BadParameter("mode must be 'mock' or 'litellm'")
        settings = settings.model_copy(update={"llm_mode": mode})

    allowed_source_types = {
        "document", "code", "experiment", "expert_note", "test_report", "unknown"
    }
    if source_type not in allowed_source_types:
        raise typer.BadParameter(
            f"source-type must be one of: {', '.join(sorted(allowed_source_types))}"
        )

    ingested = SourceIngestor().ingest_path(
        input_file,
        source_id=source_id,
        source_type=source_type,
    )
    if ingested.status != "ingested":
        rprint(f"[bold red]Ingestion failed:[/bold red] {ingested.error}")
        raise typer.Exit(code=1)

    text = ingested.content
    model = create_chat_model(settings)
    from algo_weaver.agents.extraction_graph import build_extraction_graph

    extractor = CapabilityExtractor(model, max_input_chars=settings.max_input_chars)
    graph = build_extraction_graph(extractor)
    result = graph.invoke(
        {
            "source_text": text,
            "source_id": source_id,
            "source_type": source_type,
            "source_location": str(input_file),
        }
    )

    if "error" in result:
        rprint(f"[bold red]Extraction failed:[/bold red] {result['error']}")
        raise typer.Exit(code=1)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(result["capability"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    rprint(f"[green]Capability card saved:[/green] {output_file}")
    rprint(f"Status: {result['capability']['status']}")


@app.command()
def version() -> None:
    """Print the installed AlgoWeaver version."""
    from algo_weaver import __version__

    rprint(f"AlgoWeaver {__version__}")


@app.command()
def reuse(
    query: Annotated[str, typer.Argument(help="Capability name or text to search")],
    registry_path: Annotated[Path, typer.Option("--registry")] = Path(
        "data/processed/capabilities.sqlite3"
    ),
    limit: Annotated[int, typer.Option("--limit", min=1, max=100)] = 20,
) -> None:
    """Search only independently verified capability versions for reuse."""
    records = CapabilityRegistry(registry_path).search_reusable(query, limit=limit)
    rprint(json.dumps([record.model_dump(mode="json") for record in records], ensure_ascii=False, indent=2))


@app.command()
def reproduce(
    input_file: Annotated[Path, typer.Option("--input", "-i", exists=True, readable=True)],
    additional_input: Annotated[
        list[Path] | None, typer.Option("--additional-input", exists=True, readable=True)
    ] = None,
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")] = Path(
        "data/processed/reproduction"
    ),
    source_id: Annotated[str, typer.Option("--source-id")] = "local-input-001",
    mode: Annotated[str, typer.Option("--mode", help="mock or litellm")] = "mock",
    generation_mode: Annotated[
        str, typer.Option("--generation-mode", help="template, mock or llm")
    ] = "template",
    execute: Annotated[bool, typer.Option("--execute", help="run pytest inside Docker")] = False,
    registry_path: Annotated[Path | None, typer.Option("--registry")] = None,
    backend: Annotated[str, typer.Option("--backend", help="docker or wsl")] = "docker",
    repair: Annotated[bool, typer.Option("--repair", help="attempt bounded template repair")] = False,
    repair_mode: Annotated[
        str, typer.Option("--repair-mode", help="template or llm; requires --repair")
    ] = "template",
    capability_file: Annotated[
        Path | None,
        typer.Option("--capability-file", exists=True, readable=True),
    ] = None,
    reuse_query: Annotated[str | None, typer.Option("--reuse-query")] = None,
    metrics_file: Annotated[Path | None, typer.Option("--metrics-file", exists=True, readable=True)] = None,
    metrics_window: Annotated[int, typer.Option("--metrics-window", min=1)] = 3,
    max_mae: Annotated[float | None, typer.Option("--max-mae", min=0)] = None,
    max_rmse: Annotated[float | None, typer.Option("--max-rmse", min=0)] = None,
) -> None:
    """Build an evidence-linked reproduction bundle and run safe static checks."""
    if additional_input is None:
        additional_input = []
    if mode not in {"mock", "litellm"}:
        raise typer.BadParameter("mode must be 'mock' or 'litellm'")
    if generation_mode not in {"template", "mock", "llm"}:
        raise typer.BadParameter("generation-mode must be 'template', 'mock' or 'llm'")
    if generation_mode == "llm" and mode != "litellm":
        raise typer.BadParameter("generation-mode 'llm' requires --mode litellm")
    if repair_mode not in {"template", "llm"}:
        raise typer.BadParameter("repair-mode must be 'template' or 'llm'")
    if repair_mode == "llm" and not repair:
        raise typer.BadParameter("repair-mode 'llm' requires --repair")
    if repair_mode == "llm" and mode != "litellm":
        raise typer.BadParameter("repair-mode 'llm' requires --mode litellm")
    if backend not in {"docker", "wsl"}:
        raise typer.BadParameter("backend must be 'docker' or 'wsl'")
    if capability_file is not None and reuse_query is not None:
        raise typer.BadParameter("use either --capability-file or --reuse-query, not both")

    settings = get_settings().model_copy(update={"llm_mode": mode})
    ingested = SourceIngestor().ingest_path(
        input_file,
        source_id=source_id,
        source_type="document",
    )
    if ingested.status != "ingested":
        rprint(f"[bold red]Ingestion failed:[/bold red] {ingested.error}")
        raise typer.Exit(code=1)
    additional_batch = (
        SourceIngestor().ingest_paths(additional_input, source_type="unknown")
        if additional_input
        else None
    )
    if additional_batch is not None:
        rprint(
            "Additional sources: "
            f"{additional_batch.ingested_count} ingested, "
            f"{additional_batch.unsupported_count} unsupported, "
            f"{additional_batch.failed_count} failed"
        )

    from algo_weaver.schemas.capability import AlgorithmCapability

    if reuse_query is not None:
        if registry_path is None:
            raise typer.BadParameter("--reuse-query requires --registry")
        reusable = CapabilityRegistry(registry_path).search_reusable(reuse_query, limit=1)
        if not reusable:
            rprint(f"[bold red]No verified capability matched:[/bold red] {reuse_query}")
            raise typer.Exit(code=1)
        capability = AlgorithmCapability.model_validate(reusable[0].capability)
        rprint(f"Reusing verified capability: {capability.name} (v{reusable[0].version})")
    elif capability_file is not None:
        capability = AlgorithmCapability.model_validate_json(
            capability_file.read_text(encoding="utf-8")
        )
        rprint(f"Using reviewed capability card: {capability_file}")
    else:
        model = create_chat_model(settings)
        from algo_weaver.agents.extraction_graph import build_extraction_graph

        extractor = CapabilityExtractor(model, max_input_chars=settings.max_input_chars)
        graph = build_extraction_graph(extractor)
        result = graph.invoke(
            {
                "source_text": ingested.content,
                "source_id": source_id,
                "source_type": "document",
                "source_location": str(input_file),
            }
        )
        if "error" in result:
            rprint(f"[bold red]Extraction failed:[/bold red] {result['error']}")
            raise typer.Exit(code=1)
        capability = AlgorithmCapability.model_validate(result["capability"])
    chunks = SourceChunker().chunk(ingested)
    if additional_batch is not None:
        for additional_source in additional_batch.sources:
            chunks.extend(SourceChunker().chunk(additional_source))
    hits = LocalLexicalRetriever(chunks).search(capability.name, top_k=5)
    plan = ReproductionPlanner().build_plan(capability, hits)
    if plan.status != "ready":
        rprint(f"[bold red]Reproduction plan blocked:[/bold red] {plan.blocking_reasons}")
        raise typer.Exit(code=1)

    if generation_mode == "mock":
        bundle = MockCodeGenerator().generate(plan, hits)
    elif generation_mode == "llm":
        bundle = LLMCodeGenerator(
            create_chat_model(settings, model=settings.code_llm_model)
        ).generate(plan, hits)
    else:
        bundle = TemplateArtifactWriter().generate(plan)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths = TemplateArtifactWriter().write(bundle, output_dir)
    validator = ValidationService()
    reports = [validator.validate_capability(capability)]
    dependency_reports = []
    for artifact in bundle.artifacts:
        if artifact.kind == "python_source":
            dependency_reports.append(
                PythonDependencyAnalyzer().analyze(artifact.content, source_id=artifact.path)
            )
            reports.append(
                validator.validate_python_source(
                    artifact.content,
                    source_id=artifact.path,
                    required_function=("moving_average" if "moving_average" in artifact.content else None),
                )
            )
    (output_dir / "reproduction_bundle.json").write_text(
        json.dumps(bundle.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "validation_reports.json").write_text(
        json.dumps([report.model_dump(mode="json") for report in reports], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "dependency_report.json").write_text(
        json.dumps(
            [report.model_dump(mode="json") for report in dependency_reports],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    if additional_batch is not None:
        (output_dir / "ingestion_batch.json").write_text(
            json.dumps(additional_batch.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    saved = None
    verification_status = "verified" if capability.status == "verified" else "unverified"
    if registry_path is not None:
        saved = CapabilityRegistry(registry_path).save(capability)
        (output_dir / "registry_record.json").write_text(
            json.dumps(saved.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        rprint(f"Registry version saved: {saved.version} ({saved.status})")

    if execute:
        runner = WslDockerSandboxRunner() if backend == "wsl" else DockerSandboxRunner()
        execution_result = runner.run(
            output_dir,
            ["python", "-m", "unittest", "discover", "-v"],
            policy=ExecutionPolicy(),
        )
        if repair and execution_result.status in {"failed", "timeout"}:
            repairer = (
                LLMRepairer(
                    create_chat_model(settings, model=settings.code_llm_model)
                )
                if repair_mode == "llm"
                else TemplateRepairer()
            )
            repair_result = BoundedRepairLoop(max_attempts=2).run(
                execution_result,
                repair=lambda observation, _attempt: repairer.repair(
                    bundle, output_dir, observation
                ),
                execute=lambda: runner.run(
                    output_dir,
                    ["python", "-m", "unittest", "discover", "-v"],
                    policy=ExecutionPolicy(),
                ),
            )
            rprint(f"Repair loop: {repair_result.final_status}")
            if repair_result.attempts:
                execution_result = runner.run(
                    output_dir,
                    ["python", "-m", "unittest", "discover", "-v"],
                    policy=ExecutionPolicy(),
                )
            (output_dir / "reproduction_bundle.json").write_text(
                json.dumps(bundle.model_dump(mode="json"), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        (output_dir / "execution_result.json").write_text(
            json.dumps(execution_result.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        rprint(f"Sandbox execution: {execution_result.status}")
        if execution_result.status != "passed":
            rprint(f"[yellow]Verification remains unverified:[/yellow] {execution_result.error}")
        runtime_report = validator.build_runtime_report(
            capability,
            execution_result,
            reports[1:],
        )
        reports.append(runtime_report)
        (output_dir / "validation_reports.json").write_text(
            json.dumps([report.model_dump(mode="json") for report in reports], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if registry_path is not None and saved is not None and runtime_report.overall_status == "passed":
            promoted = CapabilityRegistry(registry_path).promote_verified(
                capability.capability_id,
                runtime_report,
            )
            (output_dir / "registry_record.json").write_text(
                json.dumps(promoted.model_dump(mode="json"), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            verification_status = "verified"
            rprint("Registry promotion: verified")
        if metrics_file is not None and execution_result.status == "passed":
            rows = list(csv.DictReader(metrics_file.read_text(encoding="utf-8").splitlines()))
            actual = [float(row["sales"]) for row in rows]
            if metrics_window > len(actual):
                raise typer.BadParameter("metrics-window cannot exceed the number of sales rows")
            metric_input = output_dir / "metric_input.json"
            metric_input.write_text(
                json.dumps({"sales": actual, "window": metrics_window}),
                encoding="utf-8",
            )
            metric_code = (
                "import json; from algorithm import moving_average; "
                "p=json.load(open('/workspace/metric_input.json')); "
                "print(json.dumps(moving_average(p['sales'], p['window'])))"
            )
            metric_execution = runner.run(
                output_dir,
                ["python", "-c", metric_code],
                policy=ExecutionPolicy(),
            )
            (output_dir / "metric_execution.json").write_text(
                json.dumps(metric_execution.model_dump(mode="json"), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            if metric_execution.status == "passed":
                predicted = json.loads(metric_execution.stdout.strip())
                metric_report = RegressionMetricEvaluator().evaluate(
                    actual[metrics_window - 1 :],
                    predicted,
                    task="inventory_demand",
                    max_mae=max_mae,
                    max_rmse=max_rmse,
                )
                (output_dir / "metric_report.json").write_text(
                    json.dumps(metric_report.model_dump(mode="json"), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                rprint(f"Metrics: MAE/RMSE computed for {metric_report.sample_count} samples")
    rprint(f"[green]Reproduction bundle saved:[/green] {output_dir}")
    rprint(f"Artifacts: {', '.join(path.name for path in artifact_paths)}")
    rprint(f"Verification status: {verification_status}")
