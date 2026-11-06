from pathlib import Path

import pytest

from algo_weaver.services.code_parser import PythonCodeParser


def test_parser_extracts_imports_classes_methods_and_functions() -> None:
    source = '''"""Moving average implementation."""
import math as m
from collections import deque

class Window:
    """A bounded window."""
    def mean(self, values: list[float]) -> float:
        return sum(values) / len(values)

async def load_data(path: str) -> list[float]:
    return []
'''

    result = PythonCodeParser().parse_text(source, source_id="code-001", path="window.py")

    assert result.status == "parsed"
    assert result.module_docstring == "Moving average implementation."
    assert result.content_sha256
    assert [item.module for item in result.imports] == ["math", "collections"]
    assert result.imports[0].names == ["math as m"]
    assert result.classes[0].qualified_name == "Window"
    assert result.classes[0].methods == ["Window.mean"]
    assert result.functions[-1].qualified_name == "load_data"
    assert result.functions[-1].is_async is True
    assert result.functions[-1].arguments == ["path"]


def test_parser_returns_a_structured_syntax_error() -> None:
    result = PythonCodeParser().parse_text("def broken(:\n    pass\n", source_id="bad-code")

    assert result.status == "failed"
    assert result.syntax_error and "line 1" in result.syntax_error
    assert result.functions == []


def test_parser_rejects_empty_input_and_missing_file(tmp_path: Path) -> None:
    parser = PythonCodeParser()
    with pytest.raises(ValueError, match="source_text cannot be empty"):
        parser.parse_text("  ", source_id="empty")
    with pytest.raises(FileNotFoundError):
        parser.parse_path(tmp_path / "missing.py")
