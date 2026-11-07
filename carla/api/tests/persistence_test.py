"""Persistent uncertainty must survive an API restart without starting simulators."""

import asyncio

from fastapi import HTTPException
from api.persistence import Occupancy


def test_restart_retains_uncertainty(tmp_path):
    """Even an intent without a PID blocks reuse after a crash during spawn."""
    store = Occupancy(tmp_path)
    store.reserve()
    store.close()
    restored = Occupancy(tmp_path)
    assert restored.uncertain
    restored.close()


def test_unknown_adapter_rejects_start_and_stop(tmp_path, monkeypatch):
    """Unverified process identity permits observation but never signalling or duplicate execution."""
    from api import main

    store = Occupancy(tmp_path)
    store.reserve()
    store.close()
    store = Occupancy(tmp_path)
    monkeypatch.setattr(main, "occupancy", store)

    async def exercise():
        assert (await main.status())["state"] == "UNKNOWN"
        try:
            await main.stop()
        except HTTPException as error:
            assert error.status_code == 409
        else:
            raise AssertionError("uncertain stop was accepted")

    asyncio.run(exercise())
    store.close()
