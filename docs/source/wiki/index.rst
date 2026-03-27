Wiki
====

The wiki section consolidates operational notes that were previously stored in
the GitHub Wiki.

**Overview**

This repository contains the tools used in the development of the CAVISE team,
as well as our own developments, including **CAPI** and related integrations.

**History**

**OpenCDA** and **Artery** are two separate tools that can work and were
developed independently. In 2023 and 2024, the CAVISE team implemented a
protocol for interaction between these tools within the base scenario
*realistic_town06_cosim*. This protocol is called **CAPI**.

Both simulators use dedicated modules to interact with each other. In
**Artery**, this is the **CommunicationManager** class, part of the comms static
library, which provides network interaction with Artery in a separate thread,
synchronizes requests from several CAVs, and collects data from them. It is
used in the *realistic_town06_cosim* scenario.

In OpenCDA, **CommunicationManager** is part of CavWorld and is responsible for
interaction with **Artery**. Methods for serialization and deserialization of
data sent to and received from **Artery** are implemented there as well.

Compiling protobuf definitions into source code files is part of the
**Artery** compilation routine.

**Architecture**

.. image:: https://github.com/user-attachments/assets/f2ce445e-256e-4652-8dc8-e6cc4ce6a82a
   :alt: CAVISE architecture
   :class: align-center
