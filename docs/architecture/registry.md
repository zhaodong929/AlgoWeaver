# Capability registry

`CapabilityRegistry` uses SQLite from the Python standard library so the first persistence milestone does not require a database service. Each `save()` appends an immutable capability snapshot with an integer version, status, timestamp and JSON payload.

Promotion to `verified` is guarded by `promote_verified()`: the supplied `ValidationReport` must target the same capability and have `overall_status="passed"`. Draft or partial reports cannot promote a capability. Search currently uses an indexed SQLite name query; later retrieval integration can attach evidence hits without changing the version contract.
