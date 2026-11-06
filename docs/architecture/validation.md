# Deterministic validation baseline

`ValidationService` is the first validation layer. It runs only deterministic, host-safe checks:

- required capability fields are populated;
- capability evidence contains source IDs and excerpts;
- a Python source string parses with `ast` without execution;
- an optional required function is present;
- a `ValidationReport` records every check, status, message and compact details.

The report deliberately distinguishes `passed`, `failed` and `skipped`. A draft capability with complete fields and evidence remains `partial` while independent verification is pending. This report is a contract/static layer; it does not claim runtime metrics, dependency safety or sandbox execution. Those checks require the later isolated runner.
