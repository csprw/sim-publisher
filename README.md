# Simulator MQTT / UDP publisher

Simple utility tool that listens to wave shared memory, and publishes all info over UDP. 

## Installation

### Option 1: executable

Download the executable [here](https://drive.google.com/drive/folders/1FMsF_-S9ynNMQGosLA4iAWDcLVHeGb5K?usp=drive_link). 


### Option 2: source code

```
# python 3.12
pip install -r requirements.txt
python -m src.server
```

## Usage


1. Add the right IP of server in [config.yaml](config.yaml).
2. Start the app
3. Listen to the ports defined in [config.yaml](config.yaml). 


## MQTT topics
MQTT publishes to `ac/events` when game state changes. Telemetry is published to `ac/telemetry`.

Example `ac/events`:
```
{
    "message_type": "event_change",
    "event": "pause_race",
    "static_info": {
        "sm_version": "1.7",
        "ac_version": "1.16.4",
        "number_of_session": 1,
        "num_cars": 1,
        "car_model": "ferrari_312t",
        "track": "monza",
        "player_name": "some-name",
        "player_surname": "some-name",
        "player_nick": "some-name",
        "sector_count": 3,
        "max_torque": 261.0,
        "max_power": 306365.28125,
        "max_rpm": 12100,
        "max_fuel": 200.0,
        "suspension_max_travel": (
            0.09000000357627869,
            0.09000000357627869,
            0.10500000417232513,
            0.10500000417232513,
        ),
        "tyre_radius": (
            0.2540000081062317,
            0.2540000081062317,
            0.33000001311302185,
            0.33000001311302185,
        ),
        "max_turbo_boost": 0.0,
        "penalty_enabled": True,
        "aid_fuel_rate": 0.0,
        "aid_tyre_rate": 1.0,
        "aid_mechanical_damage": 0.0,
        "allow_tyre_blankets": 1,
        "aid_stability": 0.0,
        "aid_auto_clutch": True,
        "aid_auto_blip": 1,
        "has_drs": 0,
        "has_ers": 0,
        "has_kers": 0,
        "ker_max_joules": 0.0,
        "engine_brake_settings_count": 0,
        "ers_power_controller_count": 0,
        "track_sp_line_length": 5758.66064453125,
        "track_configuration": "",
        "ers_max_j": 0.0,
        "is_timed_race": 0,
        "has_extra_lap": 0,
        "car_skin": "0_racing_12",
        "reversed_grid_positions": 0,
        "pit_window_start": 0,
        "pit_window_end": 0,
        "air_temp": 12.0,
        "road_temp": 10.0,
        "water_temp": None,
        "tyre_compound": "Hard GP70 (H)",
    },
}

```



Example `ac/telemetry`:
```
{
    "message_type": "telemetry",
    "graphics_info": {
        "packed_id": 166167,
        "status": "AC_LIVE",
        "session_type": "AC_HOTLAP",
        "current_time_str": "3:11:742",
        "last_time_str": "-:--:---",
        "best_time_str": "-:--:---",
        "last_sector_time_str": 0,
        "completed_lap": 0,
        "position": 1,
        .... etc
    },
    "physics_info": {
        "packed_id": 63613,
        "gas": 0.0,
        "brake": 1.0,
        "fuel": 60.0,
        "gear": 1,
        "rpm": 3750,
        "steer_angle": 0.0,
        "speed_kmh": 0.0033547338098287582,
        "velocity": {
            "x": 8.778694609645754e-05,
            "y": -0.00015470662037841976,
            "z": 0.0013805956114083529,
        },
        ....etc
    },
}
```


## DataClass

Descriptions


## AC_map

| Field    | Type                        | Description                                                                                 |
| -------- | --------------------------- | ------------------------------------------------------------------------------------------- |
| Physics  | [PhysicsMap](#physicsmap)   | Real-time car physics data updated at each physics tick.                                   |
| Graphics | [GraphicsMap](#graphicsmap) | Visual/UI-related data updated at each graphics tick.                                       |
| Static   | [StaticsMap](#staticsmap)   | Session and vehicle data that remain static once loaded.                                    |

## PhysicsMap

| Field                | Type                  | Description                                                                 |
|----------------------|-----------------------|-----------------------------------------------------------------------------|
| packed_id            | int                   | Step ID of the physics update.                                              |
| gas                  | float                 | Gas pedal input (0.0 to 1.0).                                               |
| brake                | float                 | Brake input (0.0 to 1.0).                                                   |
| fuel                 | float                 | Remaining fuel in liters.                                                  |
| gear                 | int                   | Current gear.                                                              |
| rpm                  | int                   | Engine RPM.                                                                |
| steer_angle          | float                 | Steering input.                                                            |
| speed_kmh            | float                 | Car speed in km/h.                                                         |
| velocity             | [Vector3f](#vector3f) | Global velocity vector.                                                    |
| g_force              | [Vector3f](#vector3f) | Acceleration vector (G-force) in global space.                             |
| wheel_slip           | [Wheels](#wheels)     | Tyre slip per wheel.                                                       |
| wheel_pressure       | [Wheels](#wheels)     | Tyre pressure per wheel.                                                   |
| wheel_angular_s      | [Wheels](#wheels)     | Wheel angular speed (rad/s).                                               |
| tyre_core_temp       | [Wheels](#wheels)     | Tyre core temperature.                                                     |
| suspension_travel    | [Wheels](#wheels)     | Suspension travel.                                                         |
| drs                  | float                 | Drag reduction system level.                                               |
| tc                   | float                 | Traction control activity.                                                 |
| heading              | float                 | Yaw angle.                                                                 |
| pitch                | float                 | Pitch angle.                                                               |
| roll                 | float                 | Roll angle.                                                                |
| car_damage           | [CarDamage](#cardamage) | Car damage on all sides.                                                   |
| pit_limiter_on       | bool                  | Is pit limiter active.                                                     |
| abs                  | float                 | ABS activity.                                                              |
| autoshifter_on       | bool                  | Is automatic shifting enabled.                                             |
| turbo_boost          | float                 | Turbo boost level.                                                         |
| air_temp             | float                 | Ambient temperature.                                                       |
| road_temp            | float                 | Track surface temperature.                                                 |
| local_angular_vel    | [Vector3f](#vector3f) | Angular velocity in local car coordinates.                                 |
| final_ff             | float                 | Final force feedback output.                                               |
| brake_temp           | [Wheels](#wheels)     | Brake temperature per wheel.                                               |
| clutch               | float                 | Clutch input.                                                              |
| is_ai_controlled     | bool                  | Whether AI controls the car.                                               |
| tyre_contact_point   | [ContactPoint](#contactpoint) | Tyre contact points in world space.                                        |
| tyre_contact_normal  | [ContactPoint](#contactpoint) | Tyre contact normals.                                                      |
| tyre_contact_heading | [ContactPoint](#contactpoint) | Tyre contact heading directions.                                           |
| brake_bias           | float                 | Front brake bias.                                                          |
| local_velocity       | [Vector3f](#vector3f) | Car velocity in local coordinates.                                         |

## GraphicsMap

| Field                    | Type                  | Description                                               |
|--------------------------|-----------------------|-----------------------------------------------------------|
| packet_id                | int                   | Step ID of the graphics update.                          |
| status                   | [AC_STATUS](#ac_status) | Game status.                                              |
| session_type             | [AC_SESSION_TYPE](#ac_session_type) | Current session type.                                |
| current_time_str         | string                | Current lap time string.                                 |
| last_time_str            | string                | Last lap time string.                                    |
| best_time_str            | string                | Best lap time string.                                    |
| split_str                | string                | Current split time string.                               |
| completed_laps           | int                   | Completed lap count.                                     |
| position                 | int                   | Current race position.                                   |
| i_current_time           | int                   | Current lap time in ms.                                  |
| i_last_time              | int                   | Last lap time in ms.                                     |
| i_best_time              | int                   | Best lap time in ms.                                     |
| session_time_left        | float                 | Remaining session time.                                  |
| distance_traveled        | float                 | Distance driven in meters.                               |
| is_in_pit                | bool                  | Is the car in the pit box.                               |
| current_sector_index     | int                   | Current sector index (0, 1, 2).                           |
| last_sector_time         | int                   | Time of the last completed sector in ms.                 |
| number_of_laps           | int                   | Number of laps completed (end of session only).          |
| tyre_compound            | string                | Current tyre compound.                                   |
| replay_time_multiplier   | float                 | Replay speed multiplier.                                 |
| normalized_car_position  | float                 | Spline-based position around the track (0.0 to 1.0).     |
| car_coordinates          | [Vector3f](#vector3f) | Car position in world space.                             |
| penalty_time             | float                 | Time penalty to serve.                                   |
| flag                     | [AC_FLAG_TYPE](#ac_flag_type) | Current flag condition.                             |
| ideal_line_on            | bool                  | Is ideal line visual aid enabled.                        |
| is_in_pit_lane           | bool                  | Is the car within the pit lane.                          |
| surface_grip             | float                 | Grip multiplier for the surface.                         |
| mandatory_pit_done       | bool                  | Whether the mandatory pit stop has been completed.       |

## StaticsMap

| Field                      | Type        | Description                                      |
|----------------------------|-------------|--------------------------------------------------|
| sm_version                 | string      | Shared memory version.                          |
| ac_version                 | string      | AC version.                                     |
| number_of_session          | int         | Number of sessions.                              |
| num_cars                   | int         | Total number of cars.                            |
| car_model                  | string      | Player's car model.                              |
| track                      | string      | Track name.                                      |
| player_name                | string      | Player’s first name.                             |
| player_surname             | string      | Player’s surname.                                |
| player_nick                | string      | Player’s nickname.                               |
| sector_count               | int         | Number of track sectors.                         |
| max_torque                 | float       | Maximum engine torque.                           |
| max_power                  | float       | Maximum engine power.                            |
| max_rpm                    | int         | Maximum RPM.                                     |
| max_fuel                   | float       | Max fuel tank capacity.                          |
| suspension_max_travel      | List[float] | Suspension max travel per wheel.                 |
| tyre_radius                | List[float] | Radius of each tyre.                             |
| max_turbo_boost            | float       | Maximum turbo boost.                             |
| penalty_enabled            | bool        | Whether penalties are active.                    |
| aid_fuel_rate              | float       | Fuel consumption multiplier.                     |
| aid_tyre_rate              | float       | Tyre wear multiplier.                            |
| aid_mechanical_damage      | float       | Mechanical damage multiplier.                    |
| allow_tyre_blankets        | int         | Whether tyre blankets are allowed.               |
| aid_stability              | float       | Stability control level.                         |
| aid_auto_clutch            | bool        | Auto clutch enabled.                             |
| aid_auto_blip              | int         | Auto throttle blip enabled.                      |
| has_drs                    | int         | Car supports DRS.                                |
| has_ers                    | int         | Car supports ERS.                                |
| has_kers                   | int         | Car supports KERS.                               |
| ker_max_joules             | float       | KERS max joules.                                 |
| engine_brake_settings_count| int         | Number of engine braking settings.               |
| ers_power_controller_count | int         | Number of ERS power controller levels.           |
| track_sp_line_length       | float       | Track spline line length.                        |
| track_configuration        | string      | Specific track layout.                           |
| ers_max_j                  | float       | Max ERS Joules.                                  |
| is_timed_race              | int         | Is the race time-limited.                        |
| has_extra_lap              | int         | Whether there is an extra lap after the timer.   |
| car_skin                   | string      | Skin (livery) name.                              |
| reversed_grid_positions    | int         | Reversed grid position count.                    |
| pit_window_start           | int         | Start of pit window (ms).                        |
| pit_window_end             | int         | End of pit window (ms).                          |

### Wheels

| Field       | Type  | Description      | Comment |
| ----------- | ----- | ---------------- | ------- |
| front_left  | float | Front left tyre  |         |
| front_right | float | Front right tyre |         |
| rear_left   | float | Rear left tyre   |         |
| rear_right  | float | Rear right tyre  |         |

### CarDamage

| Field  | Type  | Description                    | Comment                                                        |
| ------ | ----- | ------------------------------ | -------------------------------------------------------------- |
| front  | float | Damage at the front of the car | from 0.0 to idfk (multiply by 0.284 to get the time in second) |
| rear   | float | Damage at the rear of the car  | from 0.0 to idfk (multiply by 0.284 to get the time in second) |
| left   | float | Damage at the left of the car  | from 0.0 to idfk (multiply by 0.284 to get the time in second) |
| right  | float | Damage at the right of the car | from 0.0 to idfk (multiply by 0.284 to get the time in second) |
| center | float | Total damage of the car        | from 0.0 to idfk (multiply by 0.284 to get the time in second) |

### Vector3f

| Field | Type  |
| ----- | ----- |
| x     | float |
| y     | float |
| z     | float |

### ContactPoint

| Field       | Type                  |
| ----------- | --------------------- |
| front_left  | [Vector3f](#vector3f) |
| front_right | [Vector3f](#vector3f) |
| rear_left   | [Vector3f](#vector3f) |
| rear_right  | [Vector3f](#vector3f) |

## additional information

### Enums

#### AC_STATUS

| Name       | Value |
| ---------- | ----- |
| AC_OFF    | 0     |
| AC_REPLAY | 1     |
| AC_LIVE   | 2     |
| AC_PAUSE  | 3     |

#### AC_SESSION_TYPE

| Name                | Value |
| ------------------- | ----- |
| AC_UNKNOW          | -1    |
| AC_PRACTICE        | 0     |
| AC_QUALIFY         | 1     |
| AC_RACE            | 2     |
| AC_HOTLAP          | 3     |
| AC_TIME_ATTACK     | 4     |
| AC_DRIFT           | 5     |
| AC_DRAG            | 6     |


#### AC_FLAG_TYPE

| Name               | Value |
| ------------------ | ----- |
| AC_NO_FLAG        | 0     |
| AC_BLUE_FLAG      | 1     |
| AC_YELLOW_FLAG    | 2     |
| AC_BLACK_FLAG     | 3     |
| AC_WHITE_FLAG     | 4     |
| AC_CHECKERED_FLAG | 5     |
| AC_PENALTY_FLAG   | 6     |



### Car Model

#### GT3

| Name                                | Kunos ID                     |
| ----------------------------------- | ---------------------------- |
| Aston Martin Vantage V12 GT3 2013   | amr_v12_vantage_gt3          |
| Audi R8 LMS 2015                    | audi_r8_lms                  |
| Bentley Continental GT3 2015        | bentley_continental_gt3_2016 |
| Bentley Continental GT3 2018        | bentley_continental_gt3_2018 |
| BMW M6 GT3 2017                     | bmw_m6_gt3                   |
| Emil Frey Jaguar G3 2012            | jaguar_g3                    |
| Ferrari 488 GT3 2018                | ferrari_488_gt3              |
| Honda NSX GT3 2017                  | honda_nsx_gt3                |
| Lamborghini Gallardo G3 Reiter 2017 | lamborghini_gallardo_rex     |
| Lamborghini Huracan GT3 2015        | lamborghini_huracan_gt3      |
| Lexus RCF GT3 2016                  | lexus_rc_f_gt3               |
| McLaren 650S GT3 2015               | mclaren_650s_gt3             |
| Mercedes AMG GT3 2015               | mercedes_amg_gt3             |
| Nissan GTR Nismo GT3 2015           | nissan_gt_r_gt3_2017         |
| Nissan GTR Nismo GT3 2018           | nissan_gt_r_gt3_2018         |
| Porsche 991 GT3 R 2018              | porsche_991_gt3_r            |
| Aston Martin V8 Vantage GT3 2019    | amr_v8_vantage_gt3           |
| Audi R8 LMS Evo 2019                | audi_r8_lms_evo              |
| Honda NSX GT3 Evo 2019              | honda_nsx_gt3_evo            |
| Lamborghini Huracan GT3 EVO 2019    | lamborghini_huracan_gt3_evo  |
| McLaren 720S GT3 2019               | mclaren_720s_gt3             |
| Porsche 911 II GT3 R 2019           | porsche_991ii_gt3_r          |
| Ferrari 488 GT3 Evo 2020            | ferrari_488_gt3_evo          |
| Mercedes AMG GT3 Evo 2020           | mercedes_amg_gt3_evo         |
| BMW M4 GT3 2021                     | bmw_m4_gt3                   |
| Audi R8 LMS Evo II 2022             | audi_r8_lms_evo_ii           |

#### GT4

| Name                              | Kunos ID                  |
| --------------------------------- | ------------------------- |
| Alpine A110 GT4 2018              | alpine_a110_gt4           |
| Aston Martin Vantage AMR GT4 2018 | amr_v8_vantage_gt4        |
| Audi R8 LMS GT4 2016              | audi_r8_gt4               |
| BMW M4 GT4 2018                   | bmw_m4_gt4                |
| Chevrolet Camaro GT4 R 2017       | chevrolet_camaro_gt4r     |
| Ginetta G55 GT4 2012              | ginetta_g55_gt4           |
| Ktm Xbow GT4 2016                 | ktm_xbow_gt4              |
| Maserati Gran Turismo MC GT4 2016 | maserati_mc_gt4           |
| McLaren 570s GT4 2016             | mclaren_570s_gt4          |
| Mercedes AMG GT4 2016             | mercedes_amg_gt4          |
| Porsche 718 Cayman GT4 MR 2019    | porsche_718_cayman_gt4_mr |

#### TC

| Name            | Kunos ID         |
| --------------- | ---------------- |
| BMW M2 Cup 2020 | bmw_m2_cs_racing |

#### Cup cars

| Name                             | Kunos ID                    |
| -------------------------------- | --------------------------- |
| Porsche9 91 II GT3 Cup 2017      | porsche_991ii_gt3_cup       |
| Lamborghini Huracan ST 2015      | lamborghini_huracan_st      |
| Ferrari 488 Challenge Evo 2020   | ferrari_488_challenge_evo   |
| Lamborghini Huracan ST Evo2 2021 | lamborghini_huracan_st_evo2 |
| Porsche 992 GT3 Cup 2021         | porsche_992_gt3_cup         |
