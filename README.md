# CAVISE Simulator

<p align="center">
  <img src="docs/images/CAVISE.png" alt="CAVISE — Connected & Automated Vehicle Simulation" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/CAVISE/CAVISE/releases"><img alt="Latest Release" src="https://img.shields.io/github/v/release/CAVISE/CAVISE?style=for-the-badge&amp;color=9BFFCE&amp;logo=github&amp;logoColor=D9E0EE&amp;labelColor=1E202B" /></a>
  <a href="https://github.com/CAVISE/CAVISE/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/CAVISE/CAVISE?style=for-the-badge&amp;color=9BFFCE&amp;logo=github&amp;logoColor=D9E0EE&amp;labelColor=1E202B" /></a>
  <a href="https://cavise.github.io/Documentation/"><img alt="Wiki &amp; documentation" src="https://img.shields.io/badge/Wiki-documentation-9BFFCE?style=for-the-badge&amp;logo=readthedocs&amp;logoColor=D9E0EE&amp;labelColor=1E202B" /></a>
  <a href="#quick-start"><img alt="Quick start" src="https://img.shields.io/badge/Quick-start-9BFFCE?style=for-the-badge&amp;logo=readthedocs&amp;logoColor=D9E0EE&amp;labelColor=1E202B" /></a>
  <a href="CONTRIBUTING.md"><img alt="Contributing" src="https://img.shields.io/badge/Contributing-guide-9BFFCE?style=for-the-badge&amp;logo=github&amp;logoColor=D9E0EE&amp;labelColor=1E202B" /></a>
  <a href="https://github.com/CAVISE/CAVISE/issues"><img alt="Report an issue" src="https://img.shields.io/badge/Report-an%20issue-9BFFCE?style=for-the-badge&amp;logo=github&amp;logoColor=D9E0EE&amp;labelColor=1E202B" /></a>
</p>

CAVISE brings driving, traffic, network simulation and cooperative perception
into one environment for connected and automated vehicle experiments.
Use YAML scenarios to configure vehicles and roadside units, run simulations,
collect sensor data and evaluate cooperative driving and perception.

This repository manages the workspace, component checkout and Docker services.
The simulation code lives in the individual component repositories.

## What you can do

- Simulate vehicles, sensors and roadside units in CARLA.
- Synchronize CARLA with SUMO for traffic co-simulation.
- Model vehicle communication with Artery, connected to OpenCDA through CAPI.
- Run cooperative perception with OpenCOOD models.
- Evaluate attacks against cooperative perception with AdvCP.
- Record simulation data, visualize predictions and inspect evaluation results.

## Components

| Component | Role |
| --- | --- |
| [CARLA](https://carla.org/) | 3D world, vehicle physics and sensors. |
| [OpenCDA](https://github.com/CAVISE/OpenCDA) | Scenario orchestration, driving behavior, agent services and evaluation. |
| [SUMO](https://github.com/CAVISE/sumo) | Traffic simulation and assets for CARLA–SUMO co-simulation. |
| [Artery](https://github.com/CAVISE/artery) | Network simulation. CAPI exchanges data between Artery and OpenCDA. |
| [OpenCOOD](https://github.com/CAVISE/opencood) | Cooperative-perception models and multi-agent inference. |
| [Models](https://github.com/CAVISE/models) | Model checkpoints and AdvCP runtime assets, downloaded when needed. |
| [Scenario Manager](https://github.com/CAVISE/scenario-manager) | Web interface for preparing scenario configurations. |

## Quick start

This example runs a CARLA-only Town06 scenario with the minimal OpenCDA image.
For GPU and display setup, follow the
[installation guide in the wiki](https://cavise.github.io/Documentation/wiki/install-and-launch.html)
before building the containers.

### 1. Prepare the workspace

You need Git, Python 3.12, Docker with Compose v2, and an NVIDIA GPU with
container GPU access configured. On Linux, use NVIDIA Container Toolkit.
On Windows, use Docker Desktop with WSL2 integration and run the Bash commands
inside your WSL2 Linux distribution. CARLA runs on the Windows host.

Run these commands in a Linux or WSL2 terminal:

```bash
git clone https://github.com/CAVISE/CAVISE.git
cd CAVISE
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python setup.py
```

The setup script prompts you to choose a branch or tag for each component.
It clones OpenCDA, OpenCOOD, SUMO, Artery and Scenario Manager into the workspace.
Existing component directories are left unchanged. To see the options for
selecting repositories and versions, run `python setup.py --help`.

Run all `./run.sh` commands from the CAVISE repository root.

### 2. Start CARLA and OpenCDA

Choose the instructions for your operating system.
Starting the containers prepares the environment. Start CARLA separately as
shown below, then leave its terminal running while you launch the scenario.

<details open>
<summary><strong>Linux</strong></summary>

Build and start the containers:

```bash
./run.sh build carla opencda-minimal
./run.sh up carla opencda-minimal
```

Enter the CARLA container and start the server:

```bash
docker exec -it carla bash
./CarlaUE4.sh -quality-level=Low
```

In another host terminal, enter OpenCDA and run the scenario after CARLA is ready:

```bash
docker exec -it opencda bash
python opencda.py -t v2xp_datadump_town06_carla --carla-host carla --ticks 200
```

</details>

<details>
<summary><strong>Windows / WSL2</strong></summary>

Build and start OpenCDA from the CAVISE root in WSL2:

```bash
./run.sh build opencda-minimal
./run.sh up opencda-minimal
```

Install the Windows distribution of CARLA **0.9.16** as described in the wiki.
In PowerShell, open the extracted CARLA directory and start the server:

```powershell
.\CarlaUE4.exe -quality-level=Low
```

After CARLA is ready, use another WSL2 terminal to enter OpenCDA and run the scenario:

```bash
docker exec -it opencda bash
python opencda.py -t v2xp_datadump_town06_carla --carla-host host.docker.internal --ticks 200
```

</details>

The runner loads `opencda/opencda/scenario_testing/config_yaml/v2xp_datadump_town06_carla.yaml`.
The `-t` argument omits the `.yaml` extension, and `--ticks 200` limits the run
to 200 simulation steps. This first run uses simulator ground truth for perception
and does not require model checkpoints.

### 3. Inspect results and stop

Evaluation output is written to `opencda/simulation_output/evaluation_outputs/`
on the host. Add `--record` to the scenario command when you want CARLA recordings
and sensor data under `opencda/simulation_output/data_dumping/`.

To stop the Linux containers, run this from the CAVISE root in a host terminal:

```bash
./run.sh stop carla opencda-minimal
```

On Windows, stop CARLA in its PowerShell terminal and stop OpenCDA from WSL2:

```bash
./run.sh stop opencda-minimal
```

## Choose an OpenCDA image

Use the same target name with `./run.sh build` and `./run.sh up`.
Each target maps to the single `opencda` container.

| Target | Included features |
| --- | --- |
| `opencda-minimal` | Core OpenCDA for CARLA scenarios. |
| `opencda-protobuf` | Core OpenCDA and protobuf support for communication with Artery. |
| `opencda-coperception` | Core OpenCDA and OpenCOOD for models without custom CUDA extensions. |
| `opencda-cuda` | Core OpenCDA and OpenCOOD with custom CUDA extensions. |
| `opencda` | Full image with OpenCOOD, custom CUDA extensions and protobuf support. |

All targets use a CUDA runtime and require GPU access. For example, to prepare
cooperative perception with a model that does not need custom CUDA extensions:

```bash
./run.sh build opencda-coperception
./run.sh up opencda-coperception
```

## Documentation and next steps

The **[CAVISE wiki](https://cavise.github.io/Documentation/)** contains the full
guides for installation, scenario creation, CARLA–SUMO co-simulation, Artery,
cooperative perception, AdvCP attacks, model assets and troubleshooting.

For development setup, validation and pull requests, see
[CONTRIBUTING.md](CONTRIBUTING.md).
