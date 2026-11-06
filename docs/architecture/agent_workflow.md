# Agent 工作流

The production graph will use bounded state transitions:

`ingest -> understand -> retrieve -> plan -> generate -> static_check -> sandbox_execute -> evaluate -> repair(loop) -> persist`

LangGraph is the intended orchestration layer because its state, conditional edges, checkpoints and interrupts match long-running reproduction tasks. The current extraction graph remains a small single-node slice and includes an offline runner when LangGraph is unavailable.

Reflection is driven by external observations: syntax errors, test failures, metric reports and resource limits. A model's self-rating alone cannot promote a capability.

The current `build_reproduction_graph()` implements the safe middle slice `retrieve -> plan -> generate -> validate`. It uses the same state shape with LangGraph when installed and a small in-process fallback otherwise. Generated artifacts remain `unverified`; sandbox execution and repair callbacks are later graph boundaries.
