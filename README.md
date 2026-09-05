# CAVISE Simulator

## Overview

This repository contains the tools used in the development
of the CAVISE team, as well as our own developments - **CAPI** and others.

## History

**Opencda** and **Artery** are two separate tools that can work
and were developed separately, however, in 2023 & 2024, the CAVISE team implemented
a protocol for the interaction of these tools within the framework of the basic scenario *realistic_town06_cosim*
and it is called CAPI.

Both simulators use their modules to interact together, in **Artery** this is a class
**CommunicationManager** (part of the comms static library), which provides network
interaction with artery in a separate thread, synchronizes requests from several cavs and collects
data from them. It is located in only one scenario - *realistic_town06_cosim*.

In OpenCDA, **CommunicationManager** is part of CavWorld and is essentially just one of the components
responsible for interacting with **Artery**. Methods of serialization and deserialization of data
sent and received from **Artery** are also implemented.

Compiling protobuf to source code files is part of the **Artery** compilation routine.

## Info

We also have a [Wiki](https://cavise.github.io/Documentation/index.html) that describes the architecture, simulator launch guide, Problems and Solutions, additional scripts, and more.

## Repository setup

Install the setup dependencies and clone all simulator repositories:

```bash
python3 -m pip install -r requirements.txt
./setup.py
```

OpenCOOD can also be cloned independently or together with OpenCDA. Pass a
branch or tag to avoid the interactive version prompt:

```bash
./setup.py opencood
./setup.py opencood --opencood-version main
./setup.py opencda opencood --opencda-version main --opencood-version main
```

The short version options are `-o` for OpenCDA and `-O` for OpenCOOD. The
`models` repository is not cloned by setup: OpenCDA downloads only the model or
AdvCP bundle requested by a simulation.
