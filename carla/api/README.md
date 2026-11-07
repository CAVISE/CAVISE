# Internal process adapter

Run `python -m api` with one worker in the component container. This API is
private to the prepared compute node; do not expose its port through a public
proxy. OpenCDA owns external authentication and Manager registration.

`CAVISE_ADAPTER_STATE_DIR` selects a persistent private directory (default
`.adapter-state`). Start intent is committed to SQLite before process creation.
The adapter retains its process handle and owns a separate process group during
its lifetime. Status does not wait for the long stop operation. A stop timeout
is not completion and does not release occupancy.

After API restart with unresolved start intent, status returns `UNKNOWN` and
run/stop return 409. PID presence or absence is not sufficient to regain ownership.
This intentionally conservative recovery prevents duplicate processes or signals
to a reused PID. To recover manually, stop the entire component container, verify
that its process namespace has been destroyed, back up the state directory, and
remove its `occupancy.sqlite3` before recreating the container. Do not reset state
while any component process might still exist. No automatic task restart occurs.

Native OpenAPI is at `/openapi.json` and in `api/openapi.yaml`. Run isolated tests
from the component root with `PYTHONPATH=. python -m pytest api/tests -q`.
