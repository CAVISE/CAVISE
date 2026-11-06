import os
import asyncio
import signal
from enum import StrEnum
from fastapi import FastAPI, APIRouter, HTTPException


class QualityLevel(StrEnum):
    EPIC = "Epic"
    LOW = "Low"


API_VERSION = "v1"

app = FastAPI()
router = APIRouter(prefix=f"/{API_VERSION}")
process = None
process_lock = asyncio.Lock()
stop_requested = False
last_pid = None
last_returncode = None


def _group_exists(group_id: int) -> bool:
    """Treat live or inaccessible process groups as occupied."""
    try:
        os.killpg(group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


async def _wait_for_group(current: asyncio.subprocess.Process) -> None:
    """Wait for both the launcher and its process group to exit."""
    await current.wait()
    while _group_exists(current.pid):
        await asyncio.sleep(0.1)


@router.get("/status")
async def status() -> dict[str, str | int | None]:
    if process is None:
        state = "IDLE" if last_pid is None else "STOPPED"
        return {"state": state, "pid": last_pid, "returncode": last_returncode}
    if _group_exists(process.pid):
        state = "STOPPING" if stop_requested else "RUNNING"
    else:
        state = "STOPPED" if process.returncode == 0 else "FAILED"
    return {"state": state, "pid": process.pid, "returncode": process.returncode}


@router.post("/run")
async def run(render_off_screen: bool = True, quality_level: QualityLevel = QualityLevel.LOW) -> dict[str, str]:
    global process, stop_requested
    async with process_lock:
        if process is None or (process.returncode is not None and not _group_exists(process.pid)):
            cmd = [
                "/workspace/CarlaUE4.sh",
                f"--quality-level={quality_level}",
            ]
            if render_off_screen:
                cmd.append("-RenderOffScreen")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                start_new_session=True,
            )
            stop_requested = False
            return {"message": f"Start process {process}"}
        else:
            return {"message": f"Process {process} already in progress"}


@router.post("/stop")
async def stop() -> dict[str, str | int | None]:
    global process, stop_requested, last_pid, last_returncode
    async with process_lock:
        if process is None:
            return {"state": "IDLE" if last_pid is None else "STOPPED", "pid": last_pid, "returncode": last_returncode}

        current = process
        if not stop_requested:
            try:
                os.killpg(current.pid, signal.SIGINT)
            except ProcessLookupError:
                # An already exited process group needs no further signal.
                pass
            stop_requested = True

        try:
            await asyncio.wait_for(_wait_for_group(current), timeout=30)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="CARLA did not stop within 30 seconds",
            )

        last_pid = current.pid
        last_returncode = current.returncode
        process = None
        stop_requested = False
        return {"state": "IDLE" if last_pid is None else "STOPPED", "pid": last_pid, "returncode": last_returncode}


app.include_router(router)
