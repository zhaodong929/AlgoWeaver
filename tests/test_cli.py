from typer.testing import CliRunner

from algo_weaver.cli import app


def test_version_command() -> None:
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert "AlgoWeaver 0.1.0" in result.stdout


def test_reproduce_command_writes_unverified_bundle(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# 移动平均算法\n用于时间序列平滑。", encoding="utf-8")
    output_dir = tmp_path / "bundle"

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--mode",
            "mock",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "unverified" in result.stdout
    assert (output_dir / "algorithm.py").exists()
    assert (output_dir / "test_algorithm.py").exists()
    assert (output_dir / "reproduction_bundle.json").exists()
    assert (output_dir / "validation_reports.json").exists()


def test_reproduce_accepts_an_explicit_reviewed_capability_file(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# Moving Average\nSmooth a time series.", encoding="utf-8")
    capability = tmp_path / "capability.json"
    capability.write_text(
        '{"name":"Moving Average","problem_definition":"Smooth a time series.",'
        '"inputs":["data"],"outputs":["averages"],"algorithm_steps":["Slide a window."],'
        '"evidence":[{"source_id":"doc-001","source_type":"document","excerpt":"source"}],'
        '"status":"draft"}',
        encoding="utf-8",
    )
    output_dir = tmp_path / "bundle"

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--capability-file",
            str(capability),
            "--mode",
            "mock",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "reviewed capability card" in result.stdout
