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

В директории `opencda/opencda/scenario_testing/config_yaml` создаем `<scenario_name>.yaml`. Подробнее про настройки yaml файла можно почитать тут - https://opencda-documentation.readthedocs.io/en/latest/md_files/yaml_define.html.

Содержимое <scenario_name>.yaml
"""""""""""""""""""""""""""""""

После добавления CCCP yaml файлы были немного усовершенствованны с добавлением нового заголовка `sumo-artery`. Используется следующим образом:

.. code-block:: yaml

    sumo:
        port: ~
        host: ~
        gui: true
        client_order: 1
        step_length: ${world.fixed_delta_seconds}

    sumo-artery:
        port: 8813
        host: artery # IP address artery docker container
        gui: true
        client_order: 2
        step_length: ${world.fixed_delta_seconds}


Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/scenario_testing/config_yaml/rsu_check.yaml?ref_type=heads

Assets
------

В директории `opencda/opencda/assets/` создаем папку в формате `<scenario_name>` и следующие 5 файлов:

<scenario_name>.sumocfg
""""""""""""""""""""""""""""""""""

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check.sumocfg?ref_type=heads

<scenario_name>.rou.xml
""""""""""""""""""""""""""""""

Файл содержит пути транспортных средств. Через flow задается поток, через trip задается путь только одной машины. Подробнее можно почитать здесь - https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html. Так же есть скрипт питоновский, который может сгенерировать рандомное количество машин через trip - https://sumo.dlr.de/docs/Tools/Trip.html. `from` и `to` обозначаются участки дорог где начинается поток и где заканчивается. Номера дорог можно получить, если открыть sumo и открыть .net.xml файл сценария,  правой кнопкой мыши по участку дороги выведет ее номер.

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check.rou.xml?ref_type=heads

<scenario_name>.net.xml
""""""""""""""""""""""""""""""""""

Файл, который сгенерирован для каждого города свой и который можно редактировать через sumo. Если карта устраивает, то просто копируем. 

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check.net.xml?ref_type=heads

Файлы для поддержки CCCP
"""""""""""""""""""""""

<scenario_name>.poly.xml
""""""""""""""""""""""""

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check.poly.xml?ref_type=heads


<scenario_name>_artery.sumocfg
""""""""""""""""""""""""""""""

Пример:
https://172.18.130.50:9443/cavise-982/opencda/-/blob/main/opencda/assets/rsu_check/rsu_check_artery.sumocfg?ref_type=heads

Artery
------

В директории `artery/scenarios/` создаем папку в формате `<scenario_name>`. Пример можно взять отсюда:
https://172.18.130.50:9443/cavise-982/artery/-/tree/main/scenarios/rsu_check?ref_type=heads

Файлы, которые должны быть такие же как и в assets Opencda: \n
<scenario_name>.net.xml, <scenario_name>.poly.xml, <scenario_name>.rou.xml, <scenario_name>.sumocfg

Нужно изменить следующие файлы:

omnetpp.ini
"""""""""""
Строчку:

.. code-block:: ini

    *.traci.launcher.sumocfg = "<scenario_name>.sumocfg"

artery/scenarios/CMakeLists.txt
"""""""""""""""""""""""""""""""

Добавить цель:

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
    print(spectator.get_transform())


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
