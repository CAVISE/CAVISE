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

We also have a [Wiki](https://github.com/CAVISE/CAVISE/wiki) that describes the architecture, simulator launch guide, troubleshooting, additional scripts, and more.
