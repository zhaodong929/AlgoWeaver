from pathlib import Path, PureWindowsPath

import pytest

from algo_weaver.schemas.execution import ExecutionPolicy
from algo_weaver.services import sandbox as sandbox_module
from algo_weaver.services.sandbox import DockerSandboxRunner, WslDockerSandboxRunner


def test_policy_rejects_unbounded_values() -> None:
    with pytest.raises(ValueError):
        ExecutionPolicy(timeout_seconds=0)
    with pytest.raises(ValueError):
        ExecutionPolicy(memory_mb=32)


def test_runner_blocks_when_docker_is_unavailable(tmp_path: Path) -> None:
    runner = DockerSandboxRunner(client_factory=lambda: (_ for _ in ()).throw(RuntimeError("offline")))

    result = runner.run(tmp_path, ["python", "-c", "print('must stay in sandbox')"])

    assert result.status == "blocked"
    assert result.exit_code is None
    assert result.error and "Docker unavailable" in result.error


def test_runner_applies_isolation_policy_with_fake_client(tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    class FakeContainer:
        def wait(self, *, timeout: float) -> dict[str, int]:
            calls["timeout"] = timeout
            return {"StatusCode": 0}

        def logs(self, *, stdout: bool, stderr: bool) -> bytes:
            return b"ok" if stdout and not stderr else b""

        def remove(self, *, force: bool) -> None:
            calls["removed"] = force

    class FakeContainers:
        def run(self, **kwargs: object) -> FakeContainer:
            calls.update(kwargs)
            return FakeContainer()

    class FakeClient:
        containers = FakeContainers()

    result = DockerSandboxRunner(client_factory=lambda: FakeClient()).run(
        tmp_path,
        ["pytest", "-q"],
        policy=ExecutionPolicy(memory_mb=256, cpu_limit=0.5),
    )

    assert result.status == "passed"
    assert calls["network_disabled"] is True
    assert calls["read_only"] is True
    assert calls["cap_drop"] == ["ALL"]
    assert calls["security_opt"] == ["no-new-privileges:true"]
    assert calls["mem_limit"] == "256m"
    assert calls["nano_cpus"] == 500_000_000
    assert calls["removed"] is True


def test_windows_to_wsl_path_uses_drive_mounts() -> None:
    assert sandbox_module._windows_to_wsl_path(PureWindowsPath(r"C:\workspace\job")) == (
        "/mnt/c/workspace/job"
    )


def test_wsl_runner_translates_policy_without_host_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: dict[str, object] = {}

    class Completed:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(command, **kwargs):
        calls["command"] = command
        calls["kwargs"] = kwargs
        return Completed()

    monkeypatch.setattr(sandbox_module, "_windows_to_wsl_path", lambda _: "/mnt/c/workspace")
    result = WslDockerSandboxRunner(run_fn=fake_run).run(
        tmp_path,
        ["python", "-m", "unittest", "discover"],
    )

    assert result.status == "passed"
    assert calls["command"][0:5] == ["wsl.exe", "-d", "Ubuntu-24.04", "--", "docker"]
    assert "--network" in calls["command"]
    assert "none" in calls["command"]
    assert "--read-only" in calls["command"]
    assert "--cap-drop=ALL" in calls["command"]
    assert calls["kwargs"]["text"] is False


def test_wsl_output_decoder_handles_utf16_diagnostics() -> None:
    encoded = "WSL diagnostic".encode("utf-16-le")

    assert sandbox_module._decode_process_output(encoded) == "WSL diagnostic"
