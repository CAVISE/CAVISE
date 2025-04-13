Scenario Creation
=================

Python file
-----------

В директории `opencda/opencda/scenario_testing/` создаем `<scenario_name>.py`. 
В скрипте заменить `<scenario_name>` на название сценария, а так же название города на нужные.


Содержимое <scenario_name>.py

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/scenario_testing/rsu_check.py?ref_type=heads

Yaml file
---------

Yaml файл содержит настройки сценария со стороны carla, то есть информация и настройки машин и rsu генерируемых ей.

В директории `opencda/opencda/scenario_testing/config_yaml` создаем `<scenario_name>.yaml`. Они довольно стандартные, так что можно брать файл из примера и дорабатывать. Подробнее про настройки yaml файла можно почитать тут - https://opencda-documentation.readthedocs.io/en/latest/md_files/yaml_define.html.

Для подключения в сценарий sumo в yaml файл нужно добавить универсальный блок из листинга ниже и файлы для настройки sumo, о них написано в следующем блоке:

.. code-block:: yaml

    sumo:
        port: 3000
        host: sumo
        gui: true
        client_order: 2
        step_length: ${world.fixed_delta_seconds}


Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/scenario_testing/config_yaml/rsu_check.yaml?ref_type=heads

Assets
------

Все настройки sumo хранятся в директории sumo/assets/. Создаем в ней папку в формате <scenario_name> и в ней следующие файлы:

<scenario_name>.sumocfg
""""""""""""""""""""""""""""""""""
Основной файл сценария, в котором указываются основные настройки и подключаются файлы с остальными настройками(.rou.xml, .net.xml и т.д.).

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check.sumocfg?ref_type=heads

<scenario_name>.rou.xml
""""""""""""""""""""""""""""""

Файл содержит пути транспортных средств. Через flow задается поток, через trip задается путь только одной машины. Подробнее можно почитать здесь - https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html. Так же есть питоновский скрипт, который может сгенерировать рандомное количество машин через trip - https://sumo.dlr.de/docs/Tools/Trip.html. `from` и `to` обозначаются участки дорог, где начинается поток и где заканчивается. Номера дорог можно получить, если открыть .net.xml файл сценария через sumo и кликнуть правой кнопкой мыши по участку дороги, тогда будет выведен ее номер(что-то формата “-39.0.00” или “27_3").

**Важно:** Если сценарий запускается с использованием sumo, то все время работы сценария должна существовать хотя бы одна машина или поток, иначе сценарий мгновенно завершится. Если для запуска понадобится “фиктивная” машина, то можно использовать код на подобии такого, он создаем машину которая стоит на месте 100000 тиков(нужно заменить поля edges и lane):
lane):

.. code-block:: xml

    <vehicle id="stopped_car" type="vType_0" depart="0">
        <route edges="27 26"/>
            <stop lane="27_3" startPos="0" endPos="5" duration="100000"/>
    </vehicle>

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check.rou.xml?ref_type=heads

<scenario_name>.net.xml
""""""""""""""""""""""""""""""""""

Файл, который содержит информацию о дорожной сети в формате sumo, для каждой карты он генерируется отдельно. Если в другом сценарии уже есть нужная карта, то просто копируем ее. Если нужной карты нет, то нужно ее сгенерировать: :ref:`gen-net-xml`

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check.net.xml?ref_type=heads

Файлы для поддержки CAPI
"""""""""""""""""""""""""

Если в сценарии предполагается использование artery, то нужно создать еще один обязательный и один опциональный файлы:

<scenario_name>_artery.sumocfg
""""""""""""""""""""""""""""""

Файл аналогичен стандартному .sumocfg, за исключением поля num-clients, которое в этому случае равно 2.

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check_artery.sumocfg?ref_type=heads

<scenario_name>.poly.xml
""""""""""""""""""""""""

Опциональный файл. В нем описываются зоны на карте разных типов, напимер здания, деревья и т.д.(Все что может как то помешать распространению сигнала). Данные из него используются в artery для более точной симуляции распространения сигнала. Для карты Town06, можно взять его из примера, для остальных карт придется создавать вручную через netedit(:ref:`gen-poly-xml`).

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check.poly.xml?ref_type=heads


Artery
------

Настройки artery храняися в директории `artery/scenarios/`, создаем в ней папку в формате `<scenario_name>`. Пример можно взять отсюда:
https://172.18.130.50:9443/cavise-982/artery/-/tree/main/scenarios/rsu_check?ref_type=heads

Файлы в этой папке идентичны с файлами настройки sumo:
<scenario_name>.net.xml, <scenario_name>.poly.xml, <scenario_name>.rou.xml, <scenario_name>.sumocfg(который для артери)

Но к ним нужно добавить несколько дополнительных:

omnetpp.ini
"""""""""""

Стандартный для всех сценариев. Нужно поменять только строку `*.traci.launcher.sumocfg = "<sumoconfig_name>.sumocfg"`:

.. code-block:: ini

    [General]
    network = artery.inet.World
    scheduler-class = artery::AsioScheduler

    **.scalar-recording = false
    **.vector-recording = false

    *.traci.core.version = -1
    *.traci.launcher.typename = "PosixLauncher"
    *.traci.launcher.sumocfg = "<sumoconfig_name>.sumocfg"
    *.traci.launcher.sumo = "sumo-gui"
    *.traci.launcher.port = 8813

    *.node[*].wlan[*].typename = "VanetNic"
    *.node[*].wlan[*].radio.channelNumber = 180
    *.node[*].wlan[*].radio.carrierFrequency = 5.9 GHz
    *.node[*].wlan[*].radio.transmitter.power = 200 mW

    *.node[*].middleware.updateInterval = 0.1s
    *.node[*].middleware.datetime = "2013-06-01 12:35:00"

    *.node[*].middleware.services = xmldoc("services.xml")

    [Config separated-sumo]
    *.traci.launcher.typename = "ConnectLauncher"
    *.traci.launcher.hostname = "sumo"
    *.traci.launcher.port = 3000
    *.traci.launcher.clientId = 1

services.xml
"""""""""""""""""""""""""""""""

Стандартный для всех сценариев, копируем из rsu_check.

artery/scenarios/CMakeLists.txt
"""""""""""""""""""""""""""""""

Для того, чтобы иместь возможность запускать сценарий нужно добавить его в CMakeLists.txt. Добавляется стандартно изменяем только имя сценария:

.. code-block:: cmake

    add_opp_run(<scenario_name> WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/<scenario_name> NED_FOLDERS ${CMAKE_SOURCE_DIR}/src/cavise)

Как получать координаты для yaml файлов
---------------------------------------

После того как запустили карлу `cd /carla && ./CarlaUE4.sh &disown`, сначала поменяем город на нужный:

.. code-block:: bash

    /home/carla/PythonAPI/util/config.py --map Town06


В opencda созданы два скрипта get_position.py и set_position.py в директории `opencda/opencda/scenario_testing/utils`. Координату z лучше оставлять как есть на 1.05. Четвертый и шестой параметр оставляем по нулям.

get_position.py
"""""""""""""""

Скрипт, который выводит местоположение наблюдателя, порт соответственно надо заменить на тот, который в карле.

.. code-block:: python

    import carla  
    import random  
    
    client = carla.Client('carla', 2000)  
    world = client.get_world()  
    
    spectator = world.get_spectator()
    location = spectator.get_transform().location
    rotation = spectator.get_transform().rotation
    print(f'Location: {location.x:.2f}, {location.y:.2f}, {location.z:.2f},')
    print(f'Rotation: {rotation.pitch:.2f}, {rotation.yaw:.2f}, {rotation.roll:.2f}')


set_position.py
"""""""""""""""

Иногда полезно узнать, где находятся те или иные координаты. Запускаем скрипт, пишем координаты через запятую и готово.

.. code-block:: python

    import carla  
    import random  
    
    client = carla.Client('carla', 2000)  
    world = client.get_world()  
    
    spectator = world.get_spectator()  
    
    x, y, z = map(float, input().split(","))  
    location = carla.Location(x=x, y=y, z=z)  
    rotation = carla.Rotation(pitch=0, yaw=-180, roll=0)  
    spectator.set_transform(carla.Transform(location, rotation))

.. _gen-net-xml:

Генерация .net.xml файлов для карты Carla
-----------------------------------------

**Проблема**: в нашем проекте нет корректно работающих со всем функционалом .net.xml файлов карт, кроме Town06.

**Решение**: Карла предоставляет специальный скрипт генерирующий полностью рабочие .net.xml файлы для карт в формате xodr (оффициальный гайд: https://carla.readthedocs.io/en/latest/adv_sumo/#create-the-sumo-net)

В нашем контейнера carla xodr файлы всех карт расположены по пути `CarlaUE4/Content/Carla/Maps/OpenDrive/`. Для запуска скрипта в контейнер необходимо дополнительно установить библотеки eclipse-sumo и lxml и добавить переменную `SUMO_HOME.` 

Установка зависимостей и добавление переменной `SUMO_HOME`:

.. code-block:: bash

    carla@ed06e934540b:~$ pip install eclipse-sumo lxml
    carla@ed06e934540b:~$ pip show eclipse-sumo
    Name: eclipse-sumo
    Version: 1.22.0
    Summary: A microscopic, multi-modal traffic simulation package
    Home-page: https://sumo.dlr.de/
    Author: DLR and contributors
    Author-email: sumo@dlr.de
    License: EPL-2.0
    Location: /home/carla/.pyenv/versions/3.10.11/lib/python3.10/site-packages
    Requires: 
    Required-by: 
    carla@ed06e934540b:~$ export SUMO_HOME=/home/carla/.pyenv/versions/3.10.11/lib/python3.10/site-packages/sumo/

Далее можно запускать скрипт, он располагается по пути `Co-Simulation/Sumo/util/netconvert_carla.py`:

.. code-block:: bash

    python Co-Simulation/Sumo/util/netconvert_carla.py CarlaUE4/Content/Carla/Maps/OpenDrive/Town04.xodr --output mounted/Town04_1.net.xml

.. _gen-poly-xml:

Создание .poly.xml
------------------

Сначала надо создать шаблонный файл и подключить его в .sumoconfig фалй добавив строку `<additional-files value="scneario_name.poly.xml"/>`:

.. code-block:: xml

    <additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">
    </additional>


Далее открываем сценарий в netedit(Ctrl+M или File→Load sumo config) и переходим в режим редактирования полигонов(Polygon mode).

.. image:: images/toolbar.png

В настройках ставим галочки в полях fill и Close shape, также можно сразу поменять id, цвет и тип.

.. image:: images/poly_settings.png

Далее нажимаем Enter/Start drawing и на карте выделяем зону, после чего снова нажимаем Enter/Stop drawing. Добавляем таким образом все необходимые зоны и сохраняем файл.

.. image:: images/without_building.png

.. image:: images/with_building.png