"""Durable occupancy guard for a dedicated internal simulator adapter."""

import os
import sqlite3
from pathlib import Path


class Occupancy:
    """Fail closed after API restart when exact process ownership is unavailable.

    A persisted start intent may outlive the API. Such an intent is never cleared
    by PID absence or reuse; an operator must verify container-level cleanup.
    """

    def __init__(self, directory: Path) -> None:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        directory.chmod(0o700)
        path = directory / "occupancy.sqlite3"
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        os.fchmod(descriptor, 0o600)
        os.close(descriptor)
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS execution (singleton INTEGER PRIMARY KEY, pid INTEGER)")
        self.uncertain = self.db.execute("SELECT 1 FROM execution").fetchone() is not None

    def reserve(self) -> None:
        """Commit intent before creating any subprocess."""
        with self.db:
            self.db.execute("INSERT INTO execution VALUES (1, NULL)")

    def started(self, pid: int) -> None:
        """Retain PID for diagnostics, never as proof of ownership after restart."""
        with self.db:
            self.db.execute("UPDATE execution SET pid = ?", (pid,))

    def clear(self) -> None:
        """Release occupancy only after confirmed cleanup or failed process creation."""
        with self.db:
            self.db.execute("DELETE FROM execution")

    def close(self) -> None:
        """Close the local connection without discarding unresolved intent."""
        self.db.close()
