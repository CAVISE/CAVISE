
# Python file

В директории `opencda/opencda/scenario_testing/` создаем `<scenario_name>.py`. 
В скрипте заменить `<scenario_name>` на название сценария, а так же название города на нужные.

### Содержимое <scenario_name>.py только для OpenCDA
```python
# -*- coding: utf-8 -*-

# Author: Runsheng Xu <rxx3386@ucla.edu>

# License: TDG-Attribution-NonCommercial-NoDistrib

  

import os

  

import carla

  

import opencda.scenario_testing.utils.cosim_api as sim_api

import opencda.scenario_testing.utils.customized_map_api as map_api

from opencda.core.common.cav_world import CavWorld

from opencda.scenario_testing.evaluations.evaluate_manager import \

EvaluationManager

from opencda.scenario_testing.utils.yaml_utils import add_current_time

  

  

def run_scenario(opt, scenario_params):

try:

scenario_params = add_current_time(scenario_params)

  

# create CAV world

cav_world = CavWorld(opt.apply_ml)

  

# sumo conifg file path

current_path = os.path.dirname(os.path.realpath(__file__))

sumo_cfg = os.path.join(current_path,

'../assets/Town06_scenario_name')

  

# create co-simulation scenario manager

scenario_manager = \

sim_api.CoScenarioManager(scenario_params,

opt.apply_ml,

opt.version,

town='Town06',

cav_world=cav_world,

sumo_file_parent_path=sumo_cfg)

single_cav_list = \

scenario_manager.create_vehicle_manager(application=['single'],

map_helper=map_api.

spawn_helper_2lanefree)

  

# create evaluation manager

eval_manager = \

EvaluationManager(scenario_manager.cav_world,

script_name='scenario_name',

current_time=scenario_params['current_time'])

  

spectator = scenario_manager.world.get_spectator()

  

while True:

# simulation tick

scenario_manager.tick()

  

transform = single_cav_list[0].vehicle.get_transform()

spectator.set_transform(carla.Transform(transform.location +

carla.Location(z=50),

carla.Rotation(pitch=-90)))

  

for i, single_cav in enumerate(single_cav_list):

single_cav.update_info()

control = single_cav.run_step()

single_cav.vehicle.apply_control(control)

  

finally:

eval_manager.evaluate()

scenario_manager.close()

for v in single_cav_list:

v.destroy()
```

### Содержимое <scenario_name>.py для cccp
```python
#-*- coding: utf-8 -*-

#Author: Runsheng Xu [rxx3386@ucla.edu](mailto:rxx3386@ucla.edu)

#License: TDG-Attribution-NonCommercial-NoDistrib

  

import os

import zmq

import carla

  

import opencda.scenario_testing.utils.cosim_api as sim_api

import opencda.scenario_testing.utils.customized_map_api as map_api

  

from opencda.core.common.cav_world import CavWorld

from opencda.core.common.communication.serialize import MessageHandler

  

import protos.cavise.artery_pb2 as proto_artery

  

from opencda.scenario_testing.evaluations.evaluate_manager import EvaluationManager

from opencda.scenario_testing.utils.yaml_utils import add_current_time

  

from google.protobuf.json_format import MessageToJson

  
  

eval_manager = None

scenario_manager = None

single_cav_list = None

spectator = None

cav_world = None

  

OPENCDA_MESSAGE_LOCATION = os.environ.get('CAVISE_ROOT_DIR') + '/simdata/opencda/message.json'

ARTERY_MESSAGE_LOCATION = os.environ.get('CAVISE_ROOT_DIR') + '/simdata/artery/message.json'

  
  

def init(opt, scenario_params) -> None:

global eval_manager, scenario_manager, single_cav_list, spectator, cav_world

  

scenario_params = add_current_time(scenario_params)

cav_world = CavWorld(opt.apply_ml, opt.with_cccp)

  

cavise_root = os.environ.get('CAVISE_ROOT_DIR')

if not cavise_root:

raise EnvironmentError('missing cavise root!')

sumo_cfg = f'{cavise_root}/opencda/opencda/scenario_testing/config_sumo/scenario_name'

scenario_manager = sim_api.CoScenarioManager(

scenario_params,

opt.apply_ml,

opt.version,

town='Town06',

cav_world=cav_world,

sumo_file_parent_path=sumo_cfg

)

  

single_cav_list = scenario_manager.create_vehicle_manager(

application=['single'],

map_helper=map_api.

spawn_helper_2lanefree

)

  

eval_manager = EvaluationManager(

scenario_manager.cav_world,

script_name='scenario-name.py',

current_time=scenario_params['current_time']

)

  

spectator = scenario_manager.world.get_spectator()

  
  

def finalize() -> None:

global eval_manager, scenario_manager, single_cav_list

  

if eval_manager is not None:

eval_manager.evaluate()

if scenario_manager is not None:

scenario_manager.close()

if single_cav_list is not None:

for v in single_cav_list:

v.destroy()

  
  

def run() -> None:

global eval_manager, scenario_manager, single_cav_list, spectator

  

# this sim requires communication manager

if cav_world.comms_manager is None:

raise AttributeError("This sim requires communication manager")

cav_world.comms_manager.create_socket(zmq.PAIR, 'connect')

  

message_handler = MessageHandler()

while True:

scenario_manager.tick()

transform = single_cav_list[0].vehicle.get_transform()

spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50), carla.Rotation(pitch=-90)))

  

for _, single_cav in enumerate(single_cav_list):

single_cav.update_info()

message_handler.set_cav_data(single_cav.cav_data)

# be verbose!

json_output = MessageToJson(message_handler.opencda_message, including_default_value_fields=True, preserving_proto_field_name=True)

with open(OPENCDA_MESSAGE_LOCATION, 'w') as json_file:

json_file.write(json_output)

out_message = message_handler.serialize_to_string()

cav_world.comms_manager.send_message(out_message)

in_message = cav_world.comms_manager.receive_message()

v2x_info = MessageHandler.deserialize_from_string(in_message)

  

# be verbose!

parsed = proto_artery.Artery_message()

parsed.ParseFromString(in_message)

json_output = MessageToJson(parsed, including_default_value_fields=True, preserving_proto_field_name=True)

with open(ARTERY_MESSAGE_LOCATION, 'w') as json_file:

json_file.write(json_output)

for _, single_cav in enumerate(single_cav_list):

cav_list = []

if len(v2x_info) > 0:

cav_list = v2x_info[str(int(single_cav.vid.replace('-', ''), 16))]['cav_list']

else:

print('Data has been lost!')

single_cav.update_info_v2x(cav_list=cav_list)

control = single_cav.run_step()

single_cav.vehicle.apply_control(control)

  
  

def run_scenario(opt, scenario_params) -> None:

global eval_manager, scenario_manager, single_cav_list, spectator

  

raised_error = None

try:

init(opt, scenario_params)

run()

except Exception as error:

raised_error = error

finally:

finalize()

if raised_error is not None:

raise raised_error
```

# Yaml file
В директории `opencda/opencda/scenario_testing/config_yaml` создаем `<scenario_name>.yaml`. Подробнее про настройки yaml файла можно почитать тут - https://opencda-documentation.readthedocs.io/en/latest/md_files/yaml_define.html.

### Содержимое <scenario_name>.yaml
```yaml
description: |-

Copyright 2021 <UCLA Mobility Lab>

Author: Runsheng Xu <rxx3386@ucla.edu>

Content: This is the template scenario testing configuration file that other scenarios could directly refer

  

# define carla simulation setting

world:

sync_mode: true

client_port: 2000

fixed_delta_seconds: 0.05

seed: 11 # seed for numpy and random

weather:

sun_altitude_angle: 15 # 90 is the midday and -90 is the midnight

cloudiness: 0 # 0 is the clean sky and 100 is the thickest cloud

precipitation: 0 # rain, 100 is the heaviest rain

precipitation_deposits: 0 # Determines the creation of puddles. Values range from 0 to 100, being 0 none at all and 100 a road completely capped with water.

wind_intensity: 0 # it will influence the rain

fog_density: 0 # fog thickness, 100 is the largest

fog_distance: 0 # Fog start distance. Values range from 0 to infinite.

fog_falloff: 0 # Density of the fog (as in specific mass) from 0 to infinity. The bigger the value, the more dense and heavy it will be, and the fog will reach smaller heights

wetness: 0

  

# Basic parameters of the vehicles

vehicle_base:

sensing: # include perception and localization

perception:

activate: false # when not activated, objects positions will be retrieved from server directly

camera:

visualize: 0 # how many camera images need to be visualized. 0 means no visualization for camera

num: 4 # how many cameras are mounted on the vehicle. Maximum 3(frontal, left and right cameras)

# relative positions (x,y,z,yaw) of the camera. len(positions) should be equal to camera num

positions:

- [2.5, 0, 1.0, 0]

- [0.0, 0.3, 1.8, 100]

- [0.0, -0.3, 1.8, -100]

- [-2.0, 0.0, 1.5, 180]

  

lidar: # lidar sensor configuration, check CARLA sensor reference for more details

visualize: false

channels: 32

range: 50

points_per_second: 100000

rotation_frequency: 20 # the simulation is 20 fps

upper_fov: 10.0

lower_fov: -30.0

dropoff_general_rate: 0.0

dropoff_intensity_limit: 1.0

dropoff_zero_intensity: 0.0

noise_stddev: 0.0

  

localization:

activate: false # when not activated, ego position will be retrieved from server directly

dt: ${world.fixed_delta_seconds} # used for kalman filter

gnss: # gnss sensor configuration

noise_alt_stddev: 0.001

noise_lat_stddev: 1.0e-6

noise_lon_stddev: 1.0e-6

heading_direction_stddev: 0.1 # degree

speed_stddev: 0.2

debug_helper:

show_animation: false # whether to show real-time trajectory plotting

x_scale: 1.0 # used to multiply with the x coordinate to make the error on x axis clearer

y_scale: 100.0 # used to multiply with the y coordinate to make the error on y axis clearer

  

map_manager:

pixels_per_meter: 2 # rasterization map resolution

raster_size: [224, 224] # the rasterize map size (pixel)

lane_sample_resolution: 0.1 # for every 0.1m, we draw a point of lane

visualize: false # whether to visualize the rasteraization map

activate: true # whether activate the map manager

  

safety_manager: # used to watch the safety status of the cav

print_message: false # whether to print the message if hazard happens

collision_sensor:

history_size: 30

col_thresh: 1

stuck_dector:

len_thresh: 500

speed_thresh: 0.5

offroad_dector: [ ]

traffic_light_detector: # whether the vehicle violate the traffic light

light_dist_thresh: 200

  

behavior:

max_speed: 30 # maximum speed, km/h

tailgate_speed: 121 # when a vehicles needs to be close to another vehicle asap

speed_lim_dist: 3 # max_speed - speed_lim_dist = target speed

speed_decrease: 15 # used in car following mode to decrease speed for distance keeping

safety_time: 4 # ttc safety thresholding for decreasing speed

emergency_param: 0.4 # used to identify whether a emergency stop needed

ignore_traffic_light: true # whether to ignore traffic light

overtake_allowed: true # whether overtake allowed, typically false for platoon leader

collision_time_ahead: 1.5 # used for collision checking

overtake_counter_recover: 35 # the vehicle can not do another overtake during next certain steps

sample_resolution: 4.5 # the unit distance between two adjacent waypoints in meter

local_planner: # trajectory planning related

buffer_size: 12 # waypoint buffer size

trajectory_update_freq: 15 # used to control trajectory points updating frequency

waypoint_update_freq: 9 # used to control waypoint updating frequency

min_dist: 3 # used to pop out the waypoints too close to current location

trajectory_dt: 0.20 # for every dt seconds, we sample a trajectory point from the trajectory path as next goal state

debug: false # whether to draw future/history waypoints

debug_trajectory: false # whether to draw the trajectory points and path

  

controller:

type: pid_controller # this has to be exactly the same name as the controller py file

args:

lat:

k_p: 0.75

k_d: 0.02

k_i: 0.4

lon:

k_p: 0.37

k_d: 0.024

k_i: 0.032

dynamic: false # whether use dynamic pid setting

dt: ${world.fixed_delta_seconds} # this should be equal to your simulation time-step

max_brake: 10.0

max_throttle: 1.0

max_steering: 0.3

v2x: # communication related

enabled: true

communication_range: 100

  
  

# define the background traffic control by carla

# carla_traffic_manager:

# sync_mode: true # has to be same as the world setting

# global_distance: 5 # the minimum distance in meters that vehicles have to keep with the rest

# # Sets the difference the vehicle's intended speed and its current speed limit.

# # Carla default speed is 30 km/h, so -100 represents 60 km/h,

# # and 20 represents 24 km/h

# global_speed_perc: -100

# set_osm_mode: true # Enables or disables the OSM mode.

# auto_lane_change: false

# ignore_lights_percentage: 0 # whether set the traffic ignore traffic lights

# random: false # whether to random select vehicles' color and model

# vehicle_list: [] # define in each scenario. If set to ~, then the vehicles be spawned in a certain range

# # Used only when vehicle_list is ~

# # x_min, x_max, y_min, y_max, x_step, y_step, vehicle_num

# range: []

  

# define sumo simulation setting for traffic generation

sumo:

port: ~

host: ~

gui: true

client_order: 1

step_length: ${world.fixed_delta_seconds}

  
  

# define tne scenario in each specific scenario

# scenario:

# single_cav_list: []

# platoon_list: []

  

scenario:

single_cav_list: # this is for merging vehicle or single cav without v2x

- name: cav1

spawn_position: [14.84, 387.91, 1.05, 0, -103.06, 0]

destination: [-2.51, 278.08, 1.05]

v2x:

communication_range: 45

- name: cav2

spawn_position: [5.63, 269.11, 1.05, 0, -90, 0]

destination: [-5.06, 376.50, 1.05]

v2x:

communication_range: 45

- name: cav3

spawn_position: [7.22, 167.93, 1.05, 0, -90, 0]

destination: [-6.43, 407.37, 1.05]

v2x:

communication_range: 45

- name: cav4

spawn_position: [2.36, 69.83, 1.05, 0, -90, 0]

destination: [8.52, 282.45, 1.05]

v2x:

communication_range: 45
```


# Assets

## Только для OpenCDA
В директории `opencda/opencda/assets/` создаем папку в формате `<Town_name>_<scenario_name>` (если сценарий только для OpenCDA) и следующие 3 файла:


### <Town_name><scenario_name>.sumocfg
```xml
<?xml version='1.0' encoding='UTF-8'?>

<configuration>

<input>

<net-file value="<Town_name><scenario_name>.net.xml"/>

<route-files value="<Town_name><scenario_name>
			 .xml"/>

</input>

<num-clients value="1"/>

</configuration>
```

### <Town_name><scenario_name>.xml

Файл содержит пути транспортных средств. Через flow задается поток, через trip задается путь только одной машины. Подробнее можно почитать здесь - https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html. Так же есть скрипт питоновский, который может сгенерировать рандомное количество машин через trip - https://sumo.dlr.de/docs/Tools/Trip.html. `from` и `to` обозначаются участки дорог где начинается поток и где заканчивается. Номера дорог можно получить, если открыть sumo и открыть .net.xml файл сценария,  правой кнопкой мыши по участку дороги выведет ее номер.

```xml
<?xml version='1.0' encoding='UTF-8'?>

<!--generated on 2020-03-04 18:25:00 by create_sumo_vtypes.py-->

  
  
  

<routes>

<vType id="vType_0" minGap="2.00" speedFactor="normc(1.00,0.00)" vClass="passenger" carFollowModel="IDMM" tau="0.4"/>

<vType id="DEFAULT_VEHTYPE" minGap="2.50" tau="1.0" color="255,255,255" Class="passenger" accel="0.5"/>

<flow id="flow_0" begin="0.00" departLane="3" arrivalSpeed="60" departSpeed="random" departPos="random" from="-50.0.00" to="-52.0.00" end="4800.00" vehsPerHour="700.00" type="DEFAULT_VEHTYPE"/>

<flow id="flow_1" begin="0.00" departLane="4" arrivalSpeed="60" departSpeed="random" departPos="random" from="-50.0.00" to="-52.0.00" end="4800.00" vehsPerHour="700.00" type="DEFAULT_VEHTYPE"/>

<flow id="flow_2" begin="0.00" departLane="5" arrivalSpeed="60" departSpeed="random" departPos="random" from="-50.0.00" to="-52.0.00" end="4800.00" vehsPerHour="700.00" type="DEFAULT_VEHTYPE"/>

  

<flow id="flow_3" begin="0.00" departLane="3" arrivalSpeed="60" departSpeed="random" departPos="random" from="-13.0.00" to="-15.0.00" end="4800.00" vehsPerHour="700.00" type="DEFAULT_VEHTYPE"/>

<flow id="flow_4" begin="0.00" departLane="4" arrivalSpeed="60" departSpeed="random" departPos="random" from="-13.0.00" to="-15.0.00" end="4800.00" vehsPerHour="700.00" type="DEFAULT_VEHTYPE"/>

<flow id="flow_5" begin="0.00" departLane="5" arrivalSpeed="60" departSpeed="random" departPos="random" from="-13.0.00" to="-15.0.00" end="4800.00" vehsPerHour="700.00" type="DEFAULT_VEHTYPE"/>

  

<flow id="flow_6" begin="0.00" departLane="4" arrivalSpeed="60" departSpeed="random" departPos="random" from="-19.0.00" to="-39.0.00" end="4800.00" vehsPerHour="700.00" type="DEFAULT_VEHTYPE"/>

<flow id="flow_7" begin="0.00" departLane="5" arrivalSpeed="60" departSpeed="random" departPos="random" from="-19.0.00" to="-39.0.00" end="4800.00" vehsPerHour="700.00" type="DEFAULT_VEHTYPE"/>

</routes>
```

### <Town_name><scenario_name>.net.xml

Файл, который сгенерирован для каждого города свой и который можно редактировать через sumo. Если карта устраивает, то просто копируем. Примера не будет, файл очень большой.

## Для cccp

В директории `opencda/opencda/scenario_testing/config_sumo` создаем папку в формате `<scenario_name>` (если сценарий только для OpenCDA) и следующие 4 файла:

### <scenario_name>.net.xml
\
Он по аналогии со сценариями только для OpenCDA, в основном копировать только и его можно редачить в sumo.

### <scenario_name>.poly.xml

Файл отмечающий различные зоны, которые используются в Artery. Тоже только копировать.

### <scenario_name>.rou.xml

Он по аналогии со сценариями только для OpenCDA.

### <scenario_name>.sumocfg

```xml
<?xml version='1.0' encoding='UTF-8'?>

<configuration>

<input>

<net-file value="<scenario_name>.net.xml"/>

<route-files value="<scenario_name>.rou.xml"/>

<additional-files value="<scenario_name>.poly.xml"/>

</input>

<time>

<step-length value="0.1"/>

</time>

<num-clients value="2"/>

</configuration>
```


# Как получать координаты для yaml файлов

После того как запустили карлу `cd /carla && ./CarlaUE4.sh &disown`, сначала поменяем город на нужный:
```bash
/carla/PythonAPI/util/config.py --map Town06
```

Если пишет, что нет модуля карла то:
```bash
pyenv global 3.7.17
```

Внутри контейнера создаем файлики get_position.py и set_position.py либо маунтим их туда дальше используем по назначению. Координату z лучше оставлять как есть на 1.05. Четвертый и шестой параметр оставляем по нулям.

### get_position.py

Скрипт, который выводит местоположение наблюдателя, порт соответственно надо заменить на тот, который в карле.
```python
import carla  
import random  
  
client = carla.Client('localhost', 2000)  
world = client.get_world()  
  
spectator = world.get_spectator()  
print(spectator.get_transform())
```

### set_position.py

Иногда полезно узнать, где находятся те или иные координаты. Запускаем скрипт, пишем координаты через запятую и готово.

```python
import carla  
import random  
  
client = carla.Client('localhost', 2000)  
world = client.get_world()  
  
spectator = world.get_spectator()  
  
x, y, z = map(float, input().split(","))  
location = carla.Location(x=x, y=y, z=z)  
rotation = carla.Rotation(pitch=0, yaw=-180, roll=0)  
spectator.set_transform(carla.Transform(location, rotation))
```

