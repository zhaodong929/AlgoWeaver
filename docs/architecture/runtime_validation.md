# Runtime validation and promotion

`ValidationService.build_runtime_report()` combines capability contract checks, artifact static reports, draft review state and `ExecutionResult` into one capability-targeted report. A report is `passed` only when the capability is a complete `draft`, every supplied artifact report passes and the Docker execution status is `passed`.

The CLI appends this runtime report when `reproduce --execute` is used. `CapabilityRegistry.promote_verified()` accepts only this passing report, so `blocked`, `failed`, `timeout` and `needs_review` runs remain unverified.
