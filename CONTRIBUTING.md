# Contributing to CAVISE

Contributions to code, scenarios and documentation are welcome.
For a larger change, open an issue in the relevant repository first to discuss
the scope. Small fixes can go directly into a pull request.

## Choose the repository

CAVISE is a workspace of separate Git repositories. Submit a change to the
repository that owns the files:

| Change | Repository |
| --- | --- |
| Workspace setup, `run.sh`, shared Docker Compose configuration and root README | [CAVISE](https://github.com/CAVISE/CAVISE) |
| Scenario execution, driving behavior, services, attack integration and OpenCDA image | [OpenCDA](https://github.com/CAVISE/OpenCDA) |
| Cooperative-perception models and CUDA extensions | [OpenCOOD](https://github.com/CAVISE/opencood) |
| Network simulation and Artery integration | [Artery](https://github.com/CAVISE/artery) |
| SUMO container and traffic assets | [SUMO](https://github.com/CAVISE/sumo) |
| Checkpoint and AdvCP asset distribution | [Models](https://github.com/CAVISE/models) |
| Scenario editor | [Scenario Manager](https://github.com/CAVISE/scenario-manager) |
| Published wiki and documentation theme | [Documentation](https://github.com/CAVISE/Documentation) |

A commit in the root repository does not include changes inside the component
repositories. If a change spans components, open separate PRs and link them
with any required merge order.

## Set up the root repository

Use Python 3.12, matching the root CI environment. Run the following in a Linux
or WSL2 terminal. Docker must be available for the Dockerfile pre-commit hook.

```bash
git clone https://github.com/CAVISE/CAVISE.git
cd CAVISE
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
pre-commit install
```

For runtime changes, follow the [README quick start](README.md#quick-start)
and the [wiki installation guide](https://cavise.github.io/Documentation/wiki/install-and-launch.html)
to clone components and prepare GPU and display access.

If you contribute through a fork, create a fork of the repository on GitHub
and add it as a separate remote. Replace `YOUR_USERNAME` below:

```bash
git remote add fork https://github.com/YOUR_USERNAME/CAVISE.git
```

Keep `origin` pointing to `https://github.com/CAVISE/CAVISE.git` in this workflow.
The root `setup.py` derives component repository URLs from `origin`, so changing
it to your fork would make setup look for the components under your account.

## Make a focused change

Create a branch from an up-to-date `main`. Use a descriptive name such as
`feature/add-scenario-option`, `fix/container-startup` or `docs/update-launch-guide`.
For example:

```bash
git switch main
git pull --ff-only origin main
git switch -c docs/update-launch-guide
```

Keep the change focused on one problem. Update the relevant documentation when
commands, configuration or runtime behavior change. For commands in a guide,
state where they run: the host, WSL2, PowerShell or a named container.

Follow the conventions in the repository you are changing. Root Python formatting
and lint rules are defined in [pyproject.toml](pyproject.toml), and file checks
are defined in [.pre-commit-config.yaml](.pre-commit-config.yaml).

## Validate the change

Run the root file checks before opening a PR:

```bash
pre-commit run --all-files
git diff --check
```

Some hooks fix files automatically. Review those changes and rerun the checks.
For root Python changes, also run the checks used by
[the pull request workflow](.github/workflows/pull_request.yml):

```bash
python -m pip install mypy deadcode
ruff check .
ruff format --check --diff .
mypy .
deadcode .
```

Choose additional validation based on the files changed:

- **Shell scripts:** check syntax with `bash -n run.sh` and exercise the affected command.
- **Docker or runtime setup:** build the affected image and run a relevant scenario.
  Record the image target, operating system, scenario and command in the PR.
- **README or other Markdown:** preview the rendered document, open the links
  and verify command examples against the current scripts.
- **Component code:** run the checks documented in that component repository.

State which checks you ran and any checks you could not run. A simulation run
is useful for runtime changes. A text-only change can be validated by reviewing
the rendered document and its links.

## Open a pull request

Review your diff and commit only files belonging to the change. Use a short
commit title that names the area and result, following existing history, for
example `[docs] Update workspace setup instructions`.

After committing, push the branch to your fork:

```bash
git push -u fork docs/update-launch-guide
```

Open a PR against `main` in the repository that owns the change. Fill in the
provided PR template with the problem, resulting behavior, related issue when
one exists, changes and validation. Include screenshots for visible layout
changes and link any companion PRs. Mark checklist items according to what
you actually completed.

## Report a problem

Open an issue in the relevant repository and include the expected behavior,
actual behavior and steps to reproduce. For simulation or container problems,
include the operating system, GPU and driver, component revisions, image target,
scenario, exact launch command and relevant logs. Remove credentials and other
sensitive data from attached configuration and logs.
