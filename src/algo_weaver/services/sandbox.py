"""Docker-only sandbox boundary for generated code execution."""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from algo_weaver.schemas.execution import ExecutionPolicy, ExecutionResult


class DockerSandboxRunner:
    """Run commands only inside Docker; never fall back to host execution."""

    def __init__(self, client_factory: Callable[[], Any] | None = None) -> None:
        self._client_factory = client_factory

    def run(
        self,
        workspace: str | Path,
        command: Sequence[str],
        *,
        policy: ExecutionPolicy | None = None,
    ) -> ExecutionResult:
        active_policy = policy or ExecutionPolicy()
        command_list = [str(part) for part in command]
        if not command_list:
            raise ValueError("command cannot be empty")
        workspace_path = Path(workspace)
        if not workspace_path.exists():
            raise FileNotFoundError(f"workspace does not exist: {workspace_path}")
        if not workspace_path.is_dir():
            raise ValueError(f"workspace is not a directory: {workspace_path}")

        try:
            client = self._client_factory() if self._client_factory else _docker_client()
        except Exception as exc:
            return _blocked_result(active_policy, command_list, f"Docker unavailable: {exc}")

        container: Any | None = None
        started = time.monotonic()
        try:
            container = client.containers.run(
                image=active_policy.image,
                command=command_list,
                working_dir="/workspace",
                volumes={
                    str(workspace_path.resolve()): {
                        "bind": "/workspace",
                        "mode": "ro" if active_policy.read_only_workspace else "rw",
                    }
                },
                network_disabled=not active_policy.network_enabled,
                mem_limit=f"{active_policy.memory_mb}m",
                nano_cpus=int(active_policy.cpu_limit * 1_000_000_000),
                pids_limit=active_policy.pids_limit,
                environment={},
                detach=True,
                remove=False,
            )
            try:
                wait_result = container.wait(timeout=active_policy.timeout_seconds)
            except Exception as exc:
                _stop_container(container)
                return ExecutionResult(
                    status="timeout",
                    command=command_list,
                    image=active_policy.image,
                    duration_seconds=time.monotonic() - started,
                    error=f"sandbox timeout or wait failure: {exc}",
                )

            stdout = _decode(container.logs(stdout=True, stderr=False))
            stderr = _decode(container.logs(stdout=False, stderr=True))
            stdout = stdout[: active_policy.max_output_chars]
            stderr = stderr[: active_policy.max_output_chars]
            exit_code = _exit_code(wait_result)
            return ExecutionResult(
                status="passed" if exit_code == 0 else "failed",
                command=command_list,
                image=active_policy.image,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=time.monotonic() - started,
            )
        except Exception as exc:
            return ExecutionResult(
                status="failed",
                command=command_list,
                image=active_policy.image,
                duration_seconds=time.monotonic() - started,
                error=f"sandbox execution failed: {exc}",
            )
        finally:
            if container is not None:
                _remove_container(container)


def _docker_client() -> Any:
    from docker import from_env

    return from_env()


def _blocked_result(policy: ExecutionPolicy, command: list[str], error: str) -> ExecutionResult:
    return ExecutionResult(
        status="blocked",
        command=command,
        image=policy.image,
        duration_seconds=0,
        error=error,
    )


def _exit_code(wait_result: Any) -> int | None:
    if isinstance(wait_result, dict):
        value = wait_result.get("StatusCode")
        return value if isinstance(value, int) else None
    return None


def _decode(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value or "")


def _stop_container(container: Any) -> None:
    try:
        container.kill()
    except Exception:
        pass


def _remove_container(container: Any) -> None:
    try:
        container.remove(force=True)
    except Exception:
        pass
