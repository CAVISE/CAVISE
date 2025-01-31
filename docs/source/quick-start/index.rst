========
Overview
========

В монорепозитории собраны инструменты, использующиеся в разработке
команды DRL-FL, а также собственно наши наработки - CAPI и другие. 

----------------
Как это работает
----------------

**Opencda** и **Artery** - это два отдельных инструмента, которые могут работать 
и разрабатывались отдельно, однако за 2024 & 2023 годы командой DRL&FL был реализован
протокол взаимодействия этих инструментов в рамках базового сценария *realistic_town06_cosim*
и называется он CAPI.

Оба симулятора используют свои модули для совместного взаимодействия, в **Artery** это класс
**CommunicationManager** (часть статической библиотеки comms), который обеспечивает сетевое
взаимодействие с artery в отдельном потоке, синхронизирует запросы от нескольких cav и собирает
с них данные. Он находиться только в одном сценарии - *realistic_town06_cosim*.

В OpenCDA **CommunicationManager** входит в часть CavWorld и по сути является только лишь одной из компонент,
которая отвечает за взаимодействие с **Artery**. Также реализованы методы сериализации и десериализации данных,
отправляемых и получаемых от **Artery**.

Компиляция protobuf в файлы исходного кода входит в рутину компиляции **Artery**.

-------------------
Как с этим работать
-------------------

Локально собирать может понадобиться только **Artery** для корректной работы подсветки синтаксиса.
Для этого нужно выполнить эти команды:

.. code-block:: bash

    source configure.sh
    cd artery/
    source ./tools/setup/configure.sh
    ./tools/setup/build.py -b -c --config Debug --link

Для запуска всего нужно собрать compose, лучше (безотказней) собирать сервисы по одиночке.
Пример команд:

.. code-block:: bash

    docker compose build artery

Аналогично **OpenCDA**:

.. code-block:: bash

    docker compose build opencda

Также контейнерам можно указывать различные настройки при билде (в compose).

Порядок запуска: carla, artery, opencda. У сервисов есть маленькие health-check на то, что сервис
находиться в сети (пингуется).

Начать стоит с **Artery**. Дело в том, что контейнер собирает свою **Artery** в образе, 
но для удобства симуляции имеет смысл динамически создать mountpoint на дерево исходных файлов
в рабочей директории, чтобы быстро и дешево пересобирать **Artery**, а так же, самое главное -
скомпилировать protobuf файлы для совместного доступа к ним с **OpenCDA**.

из корня:

.. code-block:: bash

    sudo docker run --privileged --gpus all --network=host --name artery -e DISPLAY=$DISPLAY -v /usr/share/vulkan/icd.d:/usr/share/vulkan/icd.d -v .:/cavise -it artery:edge /bin/bash

В контейнере:

.. code-block:: bash

    cd /cavise/artery
    ./tools/setup/configure.sh --build-dir $CONTAINER_ROOT_DIR/$CONTAINER_BUILD_DIR/$BUILD_CONFIG
    ./tools/setup/build.py -c -b --config $BUILD_CONFIG --dir $CONTAINER_BUILD_DIR

Запуск:

.. code-block:: bash

    cd $CONTAINER_ROOT_DIR/$CONTAINER_BUILD_DIR/$BUILD_CONFIG
    cmake --build . --target run_realistic_town06_cosim

Теперь **OpenCDA**, тут все проще:

.. code-block:: bash

    xhost +local:docker
    sudo docker run --privileged --network=host --name opencda -e DISPLAY=$DISPLAY -v /usr/share/vulkan/icd.d:/usr/share/vulkan/icd.d -v .:/cavise -it opencda:edge /bin/bash

В контейнере:

.. code-block:: bash

    ./setup.sh # один раз
    cd /carla
    ./CarlaUE4.sh &disown
    cd /cavise/opencda

Идем запускаем artery, потом:

.. code-block:: bash

    python opencda.py -t realistic_town06_cosim -v 0.9.12 --apply_ml --with_capi

Результаты находятся в *simdata*.