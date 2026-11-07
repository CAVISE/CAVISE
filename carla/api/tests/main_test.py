"""API lifecycle regression tests; no simulator installation is required."""

import asyncio
import importlib.util
import logging
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api(monkeypatch, caplog):
    spec = importlib.util.spec_from_file_location("component_api", Path(__file__).resolve().parents[1] / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    caplog.set_level(logging.DEBUG, logger=module.logger.name)
    if hasattr(module, "_group_exists"):
        monkeypatch.setattr(module, "_group_exists", lambda pid: False)
    return module


@pytest.fixture
def client(api):
    yield TestClient(api.app)


@pytest.fixture
def process(api, monkeypatch):
    process = Mock(pid=12345, returncode=None)

    async def wait():
        process.returncode = 0
        return 0

    process.wait = AsyncMock(side_effect=wait)
    api.process = process
    if hasattr(api, "os"):
        monkeypatch.setattr(api.os, "killpg", process.send_signal)
    return process


def test_idle(client):
    assert client.get("/v1/status").json()["state"] == "IDLE"
    assert client.post("/v1/stop").json()["state"] == "IDLE"


def test_stop_and_repeat(api, client, process, caplog):
    assert client.post("/v1/stop").json() == {"state": "STOPPED", "pid": 12345, "returncode": 0}
    assert api.process is None
    assert client.post("/v1/stop").status_code == 200
    assert process.send_signal.call_count == 1
    assert "Process stopped" in caplog.text


def test_disappeared_process(api, client, process, caplog):
    process.send_signal.side_effect = ProcessLookupError()
    assert client.post("/v1/stop").status_code == 200
    assert api.process is None
    assert "already exited" in caplog.text


def test_signal_failure_can_retry(api, client, process, caplog):
    process.send_signal.side_effect = PermissionError("private detail")
    response = client.post("/v1/stop")
    assert response.status_code == 500
    assert "private detail" not in response.text
    assert api.process is process and not api.stop_requested
    assert any(record.exc_info for record in caplog.records)
    process.send_signal.side_effect = None
    assert client.post("/v1/stop").status_code == 200


def test_timeout_can_retry(api, client, process, monkeypatch, caplog):
    async def timeout(awaitable, timeout):
        awaitable.close()
        raise asyncio.TimeoutError()

    with monkeypatch.context() as patch:
        patch.setattr(api.asyncio, "wait_for", timeout)
        assert client.post("/v1/stop").status_code == 504
    assert api.process is process and api.stop_requested
    assert "Stop timed out" in caplog.text
    assert client.post("/v1/stop").status_code == 200
    assert process.send_signal.call_count == 2


def test_start_and_duplicate(api, client, monkeypatch, caplog):
    spawn = AsyncMock(return_value=Mock(pid=12345, returncode=None))
    monkeypatch.setattr(api.asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr(Path, "is_file", lambda path: True)
    assert client.post("/v1/run?scenario=demo").status_code in (200, 202)
    assert client.get("/v1/status").json()["pid"] == 12345
    assert client.post("/v1/run?scenario=demo").status_code in (200, 409)
    assert spawn.await_count == 1
    assert "started" in caplog.text


def test_start_failure_can_retry(api, client, monkeypatch, caplog):
    spawn = AsyncMock(side_effect=FileNotFoundError("private executable"))
    monkeypatch.setattr(api.asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr(Path, "is_file", lambda path: True)
    response = client.post("/v1/run?scenario=demo")
    assert response.status_code == 500
    assert "private executable" not in response.text
    assert api.process is None
    assert any(record.exc_info for record in caplog.records)
    spawn.side_effect = None
    spawn.return_value = Mock(pid=12345, returncode=None)
    assert client.post("/v1/run?scenario=demo").status_code in (200, 202)


def test_shutdown_stops_tracked_process(api, process):
    with TestClient(api.app):
        pass
    assert api.process is None
    process.wait.assert_awaited()
    process.send_signal.assert_called_once()


def test_stop_kills_unresponsive_group(api, process, monkeypatch):
    calls = 0

    async def wait_for(awaitable, timeout):
        nonlocal calls
        calls += 1
        if calls == 1:
            awaitable.close()
            raise asyncio.TimeoutError()
        return await awaitable

    monkeypatch.setattr(api.asyncio, "wait_for", wait_for)
    result = asyncio.run(api.stop())
    assert result["state"] == "STOPPED"
    assert api.process is None
    assert [call.args for call in process.send_signal.call_args_list] == [(process.pid, api.signal.SIGINT), (process.pid, api.signal.SIGKILL)]
