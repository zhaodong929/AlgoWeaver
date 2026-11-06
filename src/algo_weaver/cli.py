"""Command-line interface for AlgoWeaver."""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint

from algo_weaver.config import get_settings
from algo_weaver.llm.factory import create_chat_model
from algo_weaver.services.capability_extractor import CapabilityExtractor
from algo_weaver.services.ingestion import SourceIngestor

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
