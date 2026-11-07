# Isolated execution boundary

`DockerSandboxRunner` is the Windows Docker SDK path, and `WslDockerSandboxRunner` is the explicit WSL2 path for a Docker daemon stored inside the D-drive Ubuntu distribution. Both execute generated code only inside Docker; the WSL backend invokes `wsl.exe` to reach Docker and never runs the generated command directly on the host.

Each run applies an `ExecutionPolicy` with an image, timeout, memory limit, CPU quota, PID limit, disabled network by default, read-only workspace by default and bounded output. The result records status, command, image, exit code, logs and duration. The WSL2 runtime has been verified with the inventory forecast bundle; Windows Docker SDK remains an alternative when Docker Desktop exposes its pipe.
