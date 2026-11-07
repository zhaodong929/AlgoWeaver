# Bounded template repair

`TemplateRepairer` is a conservative repair action for the deterministic demo bundle. It only rewrites the files declared by the reviewed `ReproductionBundle`, rejects path escapes, and runs only after an execution result is `failed` or `timeout`. `BoundedRepairLoop` then reruns the sandbox with a fixed attempt limit.

This provides a real offline repair path and test contract. It does not claim semantic LLM repair; an LLM edit action can be injected later behind the same callback boundary.
