# Isolated execution boundary

`DockerSandboxRunner` is the only execution path for generated code. It lazy-loads the optional Docker SDK and returns an explicit `blocked` result when Docker is unavailable; it never calls `subprocess`, `os.system` or a host Python interpreter as a fallback.

Each run applies an `ExecutionPolicy` with an image, timeout, memory limit, CPU quota, PID limit, disabled network by default, read-only workspace by default and bounded output. The result records status, command, image, exit code, logs and duration. The current tests use a fake Docker client to verify policy translation; no real Docker daemon is available in the baseline environment, so real container execution remains unverified.
