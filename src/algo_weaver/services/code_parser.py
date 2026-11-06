"""Dependency-free Python AST parser for historical algorithm code."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from algo_weaver.schemas.code import (
    PythonClassSymbol,
    PythonFunctionSymbol,
    PythonImport,
    PythonSourceFile,
)


class PythonCodeParser:
    """Extract source symbols and provenance without executing the input code."""

    def parse_path(self, path: str | Path, *, source_id: str | None = None) -> PythonSourceFile:
        source_path = Path(path)
        if not source_path.exists():
            raise FileNotFoundError(f"source path does not exist: {source_path}")
        if not source_path.is_file():
            raise ValueError(f"source path is not a file: {source_path}")
        raw = source_path.read_bytes()
        text = raw.decode("utf-8-sig")
        return self.parse_text(
            text,
            source_id=source_id or source_path.name,
            path=str(source_path),
            raw_bytes=raw,
        )

    def parse_text(
        self,
        source_text: str,
        *,
        source_id: str,
        path: str = "<memory>",
        raw_bytes: bytes | None = None,
    ) -> PythonSourceFile:
        if not source_id.strip():
            raise ValueError("source_id cannot be empty")
        if not source_text.strip():
            raise ValueError("source_text cannot be empty")

        digest = hashlib.sha256(
            raw_bytes if raw_bytes is not None else source_text.encode("utf-8")
        ).hexdigest()
        line_count = source_text.count("\n") + 1
        try:
            tree = ast.parse(source_text, filename=path)
        except SyntaxError as exc:
            return PythonSourceFile(
                source_id=source_id,
                path=path,
                content_sha256=digest,
                line_count=line_count,
                status="failed",
                syntax_error=_format_syntax_error(exc),
            )

        visitor = _SymbolVisitor()
        visitor.visit(tree)
        return PythonSourceFile(
            source_id=source_id,
            path=path,
            content_sha256=digest,
            line_count=line_count,
            module_docstring=ast.get_docstring(tree, clean=False),
            imports=visitor.imports,
            functions=visitor.functions,
            classes=visitor.classes,
        )


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imports: list[PythonImport] = []
        self.functions: list[PythonFunctionSymbol] = []
        self.classes: list[PythonClassSymbol] = []
        self._scope: list[str] = []
        self._class_indexes: list[int] = []

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.append(
            PythonImport(
                module=", ".join(alias.name for alias in node.names),
                names=[_alias_text(alias) for alias in node.names],
                line_start=node.lineno,
                line_end=_end_lineno(node),
            )
        )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = "." * node.level + (node.module or "")
        self.imports.append(
            PythonImport(
                module=module or ".",
                names=[_alias_text(alias) for alias in node.names],
                is_from_import=True,
                line_start=node.lineno,
                line_end=_end_lineno(node),
            )
        )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qualified_name = ".".join([*self._scope, node.name])
        self.classes.append(
            PythonClassSymbol(
                name=node.name,
                qualified_name=qualified_name,
                bases=[_unparse(base) for base in node.bases],
                decorators=[_unparse(item) for item in node.decorator_list],
                docstring=ast.get_docstring(node, clean=False),
                line_start=node.lineno,
                line_end=_end_lineno(node),
            )
        )
        class_index = len(self.classes) - 1
        self._scope.append(node.name)
        self._class_indexes.append(class_index)
        self.generic_visit(node)
        self._class_indexes.pop()
        self._scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_function(node, is_async=True)

    def _record_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        *,
        is_async: bool,
    ) -> None:
        qualified_name = ".".join([*self._scope, node.name])
        self.functions.append(
            PythonFunctionSymbol(
                name=node.name,
                qualified_name=qualified_name,
                is_async=is_async,
                arguments=_argument_names(node.args),
                decorators=[_unparse(item) for item in node.decorator_list],
                return_annotation=_unparse(node.returns) if node.returns else None,
                docstring=ast.get_docstring(node, clean=False),
                line_start=node.lineno,
                line_end=_end_lineno(node),
            )
        )
        if self._class_indexes:
            self.classes[self._class_indexes[-1]].methods.append(qualified_name)
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()


def _alias_text(alias: ast.alias) -> str:
    return f"{alias.name} as {alias.asname}" if alias.asname else alias.name


def _argument_names(arguments: ast.arguments) -> list[str]:
    positional = [*arguments.posonlyargs, *arguments.args]
    names = [item.arg for item in positional]
    names.extend(item.arg for item in arguments.kwonlyargs)
    if arguments.vararg:
        names.append(f"*{arguments.vararg.arg}")
    if arguments.kwarg:
        names.append(f"**{arguments.kwarg.arg}")
    return names


def _end_lineno(node: ast.AST) -> int:
    end_lineno = getattr(node, "end_lineno", None)
    if isinstance(end_lineno, int):
        return end_lineno
    line = getattr(node, "lineno", 1)
    return line if isinstance(line, int) else 1


def _unparse(node: ast.AST) -> str:
    return ast.unparse(node)


def _format_syntax_error(error: SyntaxError) -> str:
    location = f"line {error.lineno}" if error.lineno else "unknown line"
    return f"{location}: {error.msg}"
