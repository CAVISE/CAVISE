Problems and Solutions
======================

**CARLA Error: "Town06 is not found"**

Ensure the city has changed in CARLA, then retry the scenario.

**OpenCDA Error: "No module named 'opencood.utils.box_overlaps'"**

.. code-block:: bash

   cd OpenCOOD
   python opencood/utils/setup.py build_ext --inplace

**Display Errors in Artery**

If you see:

.. code-block:: text

   qt.qpa.xcb: could not connect to display :0

run on the host:

.. code-block:: bash

   xhost +local:docker
