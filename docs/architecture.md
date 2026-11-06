# AlgoWeaver Architecture Notes

## Current vertical slice

`Markdown/text source -> CapabilityExtractor -> Pydantic validation -> EvidenceRef -> LangGraph -> JSON output`

## Domain invariants

- `AlgorithmDraft` is an untrusted model response and must be schema-validated.
- `AlgorithmCapability` is a persisted draft, not proof of correctness.
- `EvidenceRef` is attached by the application from the actual input source, not invented by the LLM.
- `verified` must only be assigned by a later verification workflow after independent tests pass.
- Source chunking and claim-level evidence alignment will be added with the ingestion/retrieval milestones.

## Planned graph expansion

`ingest -> understand -> retrieve -> extract -> validate_card -> plan_reproduction -> generate -> sandbox_execute -> evaluate -> repair(loop) -> save`

The graph will gain bounded retries, checkpointing, human approval, and structured execution events in later milestones.
