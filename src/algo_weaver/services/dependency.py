"""Static Python dependency inventory without importing target code."""

from __future__ import annotations

import ast
import sys

from algo_weaver.schemas.dependency import DependencyReport


class PythonDependencyAnalyzer:
    """Classify imports using AST and the current interpreter's stdlib names."""

    def analyze(self, source: str, *, source_id: str = "<memory>") -> DependencyReport:
        try:
            tree = ast.parse(source, filename=source_id)
        except SyntaxError as exc:
            return DependencyReport(
                source_id=source_id,
                parse_error=f"line {exc.lineno or 0}: {exc.msg}",
            )

        imports: set[str] = set()
        relative: set[str] = set()
        dynamic: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level:
                    relative.add("." * node.level + module)
                elif module:
                    imports.add(module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"__import__", "import_module"}:
                    dynamic.add(node.func.id)

        standard_library = sorted(name for name in imports if name in sys.stdlib_module_names)
        third_party = sorted(name for name in imports if name not in standard_library)
        return DependencyReport(
            source_id=source_id,
            imports=sorted(imports),
            standard_library=standard_library,
            third_party=third_party,
            relative_imports=sorted(relative),
            dynamic_imports=sorted(dynamic),
        )
