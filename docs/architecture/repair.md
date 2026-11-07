# Bounded repair loop

`BoundedRepairLoop` consumes an `ExecutionResult`, passes the external observation to a repair callback, and asks an execution callback for the next result. It never runs a command or edits files itself. The caller supplies the sandbox-backed callbacks, so the safety boundary remains in `DockerSandboxRunner`.

The loop stops on a pass, a blocked execution, a declined/failed repair callback, or `max_attempts`. Every applied attempt records the resulting execution status and a bounded observation string. This supports reflection from test feedback while preventing infinite autonomous repair.

`LLMRepairer` is an optional callback behind the same loop. It sends the reviewed plan, existing artifact contents and the external `ExecutionResult` to `ChatModel.complete_json`, then validates a strict `RepairPatch` with Pydantic. A patch must name an existing artifact, remain inside the workspace, and replace source text only; the service updates the artifact hash and never executes code on the host. The CLI uses `--repair-mode llm --repair --mode litellm`, and the API uses `repair_mode="llm"` with `repair=true`. Template repair remains the default offline path. A real provider call is not part of the current test evidence.
