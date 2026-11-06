from algo_weaver.services.dependency import PythonDependencyAnalyzer


def test_dependency_analyzer_classifies_imports_without_execution() -> None:
    report = PythonDependencyAnalyzer().analyze(
        "import json\nimport numpy as np\nfrom .helpers import load\n",
        source_id="algorithm.py",
    )

    assert report.parse_error is None
    assert report.imports == ["json", "numpy"]
    assert report.standard_library == ["json"]
    assert report.third_party == ["numpy"]
    assert report.relative_imports == [".helpers"]


def test_dependency_analyzer_reports_syntax_errors() -> None:
    report = PythonDependencyAnalyzer().analyze("def broken(:\n", source_id="bad.py")

    assert report.parse_error and "line 1" in report.parse_error
    assert report.imports == []
