# Static dependency analysis

`PythonDependencyAnalyzer` parses generated Python with `ast` and records top-level imports, standard-library modules, third-party modules, relative imports and dynamic import calls. It never imports the target module, installs packages or executes code. Syntax errors produce a structured `parse_error` report. The report is an input to later dependency policy checks and sandbox preparation.
