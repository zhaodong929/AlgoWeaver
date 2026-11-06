# AlgoWeaver Project Master Plan

This document is the stable project-level map. Detailed execution state lives in `docs/implementation/phase_status.md`; chronological evidence lives in `docs/implementation/build_log.md`.

## Product objective

Deliver a reproducible algorithm capability factory for the Zhejiang University doctoral assessment: ingest source material, extract evidence-linked capability cards, retrieve prior knowledge, plan and generate an algorithm implementation, validate it in isolation, repair bounded failures, and persist verified capabilities for reuse.

## Must-have scope

1. Multi-source document and Python code ingestion with provenance.
2. Structured capability extraction with evidence and review status.
3. Searchable knowledge representation and retrieval.
4. Reproduction planning and generated algorithm/test artifacts.
5. Isolated execution with time/resource/file/network controls.
6. Automated validation, bounded repair and traceable reports.
7. Capability versioning, persistence and reuse.
8. One reproducible end-to-end demo with CLI or API entry point.

## Delivery principles

- Keep the existing Pydantic, provider-neutral model and CLI interfaces stable.
- Prefer small project-owned interfaces before optional infrastructure adapters.
- Treat model output as untrusted; attach evidence from application-controlled sources.
- Keep Mock paths explicit and separate from real-provider evidence.
- Never execute generated code on the host; use static checks or an isolated runner.
- Every milestone requires code, tests, documentation, and a Git feature-branch commit.

## Dependency order

`baseline -> ingestion -> code parsing -> extraction/evidence -> retrieval -> reproduction -> sandbox/validation -> persistence/reuse -> API/demo -> final audit`

The order may change only when a dependency or environment constraint is recorded in an ADR or `known_issues.md`.
