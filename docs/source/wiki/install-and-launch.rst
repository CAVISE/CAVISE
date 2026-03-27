Install And Launch
==================

Install CARLA on Windows
------------------------

1. Download **CARLA** for Windows from the official releases.
2. Optionally move the contents of ``AdditionalMaps_0.9.X`` into
   ``CARLA_0.9.X/WindowsNoEditor``.
3. In ``WindowsNoEditor``, create and activate a Python virtual environment.
   Ensure the Python version matches CARLA requirements.

.. code-block:: powershell

   python -m venv venv
   # or
   py -3.10 -m venv venv
   .\venv\Scripts\activate
   pip install carla==0.9.X numpy psutil py-cpuinfo pygame python-tr

4. Start CARLA from the main directory:

.. code-block:: powershell

   ./CarlaUE4.exe

5. Verify the Python API:

.. code-block:: powershell

   python .\PythonAPI\util\config.py --map Town06

6. CARLA is now ready. When running OpenCDA scenarios from inside the OpenCDA
   container using ``python opencda.py``, specify:

.. code-block:: text

   --carla-host host.docker.internal

Install Dependencies
--------------------

**WSL on Windows**

Ensure WSL is installed. The setup has been tested on WSL2 with Ubuntu
24.04.1 LTS. Docker must also be available inside WSL.

Ensure Python 3.10 or newer is installed, then clone the project and run:

.. code-block:: bash

   python3 -m venv venv
   source ./venv/bin/activate
   pip install -r requirements.txt

**Linux**

Ensure Python 3.10 or newer is installed, then run:

.. code-block:: bash

   python3 -m venv venv
   source ./venv/bin/activate
   pip3 install -r requirements.txt

Install Required Repositories
-----------------------------

Before running the setup script, ensure the base paths are configured:

.. code-block:: bash

   source paths.conf

**Install all repositories**

.. code-block:: bash

   ./setup.py

**Install a specific repository**

Clone only ``opencda``:

.. code-block:: bash

   ./setup.py opencda

Clone only ``artery``:

.. code-block:: bash

   ./setup.py artery

**Install with an explicit version**

You can skip the interactive prompt by specifying a branch or tag directly.

For ``opencda``:

.. code-block:: bash

   ./setup.py -o main

or

.. code-block:: bash

   ./setup.py --opencda-version v0.1.0

For ``artery``:

.. code-block:: bash

   ./setup.py -a develop

or

.. code-block:: bash

   ./setup.py --artery-version v0.1.0

**Install a specific repository with a specific version**

.. code-block:: bash

   ./setup.py opencda -o v0.1.0

.. code-block:: bash

   ./setup.py artery -a develop

**Install both with explicit versions**

.. code-block:: bash

   ./setup.py -o main -a develop

Build And Run The Simulator
---------------------------

**Using ``run.sh`` (Recommended)**

You do not need to manually build or run the CARLA container on Windows.

Build everything:

.. code-block:: bash

   ./run.sh build

Start everything:

.. code-block:: bash

   ./run.sh up

Run specific services:

.. code-block:: bash

   ./run.sh build <service-name>
   ./run.sh up <service-name>
   ./run.sh restart <service-name>
   ./run.sh down <service-name>

**Using Docker Compose**

Build and start all components:

.. code-block:: bash

   docker compose -f dc-configs/docker-compose.yml --env-file paths.conf build
   docker compose -f dc-configs/docker-compose.yml --env-file paths.conf up -d

Run specific services:

.. code-block:: bash

   docker compose -f dc-configs/docker-compose.yml --env-file paths.conf up -d <service-name>

Other commands:

.. code-block:: bash

   docker compose -f dc-configs/docker-compose.yml --env-file paths.conf restart <service-name>
   docker compose -f dc-configs/docker-compose.yml --env-file paths.conf down <service-name>

Run Individual Components
-------------------------

**CARLA on Windows**

Start CARLA:

.. code-block:: bash

   ./CarlaUE4.exe

Low-quality rendering:

.. code-block:: bash

   ./CarlaUE4.exe --quality-level=Low

Headless mode:

.. code-block:: bash

   ./CarlaUE4.exe -RenderOffScreen

Change map or weather:

.. code-block:: bash

   python .\PythonAPI\util\config.py --map Town06
   python .\PythonAPI\util\config.py --weather ClearNoon
