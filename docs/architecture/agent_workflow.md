# Agent 工作流

The production graph will use bounded state transitions:

`ingest -> understand -> retrieve -> plan -> generate -> static_check -> sandbox_execute -> evaluate -> repair(loop) -> persist`

LangGraph is the intended orchestration layer because its state, conditional edges, checkpoints and interrupts match long-running reproduction tasks. The current extraction graph remains a small single-node slice and includes an offline runner when LangGraph is unavailable.

Reflection is driven by external observations: syntax errors, test failures, metric reports and resource limits. A model's self-rating alone cannot promote a capability.

The current `build_reproduction_graph()` implements `retrieve -> plan -> generate -> validate` by default. When given an explicit workspace and injected sandbox runner, it extends the flow with `write_artifacts -> execute`; failed or timed-out observations can take a conditional edge through `BoundedRepairLoop` before runtime validation. The runner and repair callback are injected at the boundary so tests never execute generated code on the host. LangGraph is used when installed and a small in-process fallback preserves the same behavior otherwise. Generated artifacts remain `unverified` until an independent runtime report passes.
