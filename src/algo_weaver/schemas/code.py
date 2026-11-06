"""Schemas for syntax-aware Python source indexing."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CodeParseStatus = Literal["parsed", "failed"]


class PythonImport(BaseModel):
    """One import statement and its source location."""

    model_config = ConfigDict(extra="forbid")

    module: str = Field(min_length=1)
    names: list[str] = Field(default_factory=list)
    is_from_import: bool = False
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)


class PythonFunctionSymbol(BaseModel):
    """A function or method discovered from a Python module."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    qualified_name: str = Field(min_length=1)
    is_async: bool = False
    arguments: list[str] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)
    return_annotation: str | None = None
    docstring: str | None = None
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)


class PythonClassSymbol(BaseModel):
    """A class and its directly declared methods."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    qualified_name: str = Field(min_length=1)
    bases: list[str] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    docstring: str | None = None
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)


class PythonSourceFile(BaseModel):
    """Structured, provenance-linked representation of one Python source file."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    path: str = Field(min_length=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    line_count: int = Field(ge=0)
    module_docstring: str | None = None
    imports: list[PythonImport] = Field(default_factory=list)
    functions: list[PythonFunctionSymbol] = Field(default_factory=list)
    classes: list[PythonClassSymbol] = Field(default_factory=list)
    status: CodeParseStatus = "parsed"
    syntax_error: str | None = None
