# Bounded repair loop

`BoundedRepairLoop` consumes an `ExecutionResult`, passes the external observation to a repair callback, and asks an execution callback for the next result. It never runs a command or edits files itself. The caller supplies the sandbox-backed callbacks, so the safety boundary remains in `DockerSandboxRunner`.

The loop stops on a pass, a blocked execution, a declined/failed repair callback, or `max_attempts`. Every applied attempt records the resulting execution status and a bounded observation string. This supports reflection from test feedback while preventing infinite autonomous repair.
