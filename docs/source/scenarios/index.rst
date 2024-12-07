Scenario Creation
=================

Python file
-----------

В директории `opencda/opencda/scenario_testing/` создаем `<scenario_name>.py`. 
В скрипте заменить `<scenario_name>` на название сценария, а так же название города на нужные.


Содержимое <scenario_name>.py только для OpenCDA
""""""""""""""""""""""""""""""""""""""""""""""""

Пример:
https://github.com/ucla-mobility/OpenCDA/blob/main/opencda/scenario_testing/single_town06_cosim.py

Содержимое <scenario_name>.py для cccp
""""""""""""""""""""""""""""""""""""""

Пример:
https://github.com/CAVISE/OpenCDA/blob/d74d6c73fcc6f2883cc4583e5d3f23b419a169cb/opencda/scenario_testing/realistic_town06_cosim.py

Yaml file
---------

В директории `opencda/opencda/scenario_testing/config_yaml` создаем `<scenario_name>.yaml`. Подробнее про настройки yaml файла можно почитать тут - https://opencda-documentation.readthedocs.io/en/latest/md_files/yaml_define.html.

Содержимое <scenario_name>.yaml
"""""""""""""""""""""""""""""""

Пример:
https://github.com/CAVISE/OpenCDA/blob/d74d6c73fcc6f2883cc4583e5d3f23b419a169cb/opencda/scenario_testing/config_yaml/intersections.yaml

Assets
------

Только для OpenCDA
""""""""""""""""""

В директории `opencda/opencda/assets/` создаем папку в формате `<Town_name>_<scenario_name>` (если сценарий только для OpenCDA) и следующие 3 файла:

<Town_name><scenario_name>.sumocfg
""""""""""""""""""""""""""""""""""

Пример:
https://github.com/CAVISE/OpenCDA/blob/d74d6c73fcc6f2883cc4583e5d3f23b419a169cb/opencda/assets/Town06_intersections/Town06_intersections.sumocfg

<Town_name><scenario_name>.xml
""""""""""""""""""""""""""""""

Файл содержит пути транспортных средств. Через flow задается поток, через trip задается путь только одной машины. Подробнее можно почитать здесь - https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html. Так же есть скрипт питоновский, который может сгенерировать рандомное количество машин через trip - https://sumo.dlr.de/docs/Tools/Trip.html. `from` и `to` обозначаются участки дорог где начинается поток и где заканчивается. Номера дорог можно получить, если открыть sumo и открыть .net.xml файл сценария,  правой кнопкой мыши по участку дороги выведет ее номер.

Пример:
https://github.com/CAVISE/OpenCDA/blob/d74d6c73fcc6f2883cc4583e5d3f23b419a169cb/opencda/assets/Town06_intersections/Town06_intersections.xml

<Town_name><scenario_name>.net.xml
""""""""""""""""""""""""""""""""""

Файл, который сгенерирован для каждого города свой и который можно редактировать через sumo. Если карта устраивает, то просто копируем. 

Пример:
https://github.com/CAVISE/OpenCDA/blob/d74d6c73fcc6f2883cc4583e5d3f23b419a169cb/opencda/assets/Town06_intersections/Town06_intersections.net.xml

Для cccp
--------

В директории `opencda/opencda/scenario_testing/config_sumo` создаем папку в формате `<scenario_name>` (если сценарий только для OpenCDA) и следующие 4 файла:

<scenario_name>.net.xml
"""""""""""""""""""""""

Он по аналогии со сценариями только для OpenCDA, в основном копировать только и его можно редачить в sumo.

<scenario_name>.poly.xml
""""""""""""""""""""""""

Файл отмечающий различные зоны, которые используются в Artery. Тоже только копировать.

<scenario_name>.rou.xml
"""""""""""""""""""""""

Он по аналогии со сценариями только для OpenCDA.

<scenario_name>.sumocfg
"""""""""""""""""""""""

Пример:
https://github.com/CAVISE/OpenCDA/blob/d74d6c73fcc6f2883cc4583e5d3f23b419a169cb/opencda/scenario_testing/config_sumo/realistic_town06_cosim/realistic_town06_cosim.sumocfg

Как получать координаты для yaml файлов
---------------------------------------

После того как запустили карлу `cd /carla && ./CarlaUE4.sh &disown`, сначала поменяем город на нужный:

.. code-block:: bash

    /carla/PythonAPI/util/config.py --map Town06


Если пишет, что нет модуля карла то:

.. code-block:: bash

    pyenv global 3.7.17

В opencda созданы два скрипта get_position.py и set_position.py в директории `opencda/opencda/scenario_testing/utils`. Координату z лучше оставлять как есть на 1.05. Четвертый и шестой параметр оставляем по нулям.

get_position.py
"""""""""""""""

Скрипт, который выводит местоположение наблюдателя, порт соответственно надо заменить на тот, который в карле.

.. code-block:: python

    import carla  
    import random  
    
    client = carla.Client('localhost', 2000)  
    world = client.get_world()  
    
    spectator = world.get_spectator()  
    print(spectator.get_transform())


set_position.py
"""""""""""""""

Иногда полезно узнать, где находятся те или иные координаты. Запускаем скрипт, пишем координаты через запятую и готово.

.. code-block:: python

    import carla  
    import random  
    
    client = carla.Client('localhost', 2000)  
    world = client.get_world()  
    
    spectator = world.get_spectator()  
    
    x, y, z = map(float, input().split(","))  
    location = carla.Location(x=x, y=y, z=z)  
    rotation = carla.Rotation(pitch=0, yaw=-180, roll=0)  
    spectator.set_transform(carla.Transform(location, rotation))

