from typer.testing import CliRunner

from algo_weaver.cli import app


def test_version_command() -> None:
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert "AlgoWeaver 0.1.0" in result.stdout
