from __future__ import annotations

import copy
import mmap
import struct
from dataclasses import dataclass
from typing import Any, List, Optional
from src.utils import dataclass_to_dict
from src.schemas import SharedMemoryTimeout, AC_STATUS, AC_SESSION_TYPE, AC_FLAG_TYPE


@dataclass
class Vector3f:
    x: float
    y: float
    z: float

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}, z: {self.z}"


@dataclass
class Wheels:
    front_left: float
    front_right: float
    rear_left: float
    rear_right: float

    def __str__(self) -> str:
        return f"FL: {self.front_left}\nFR: {self.front_right}\
            \nRL: {self.rear_left}\nRR: {self.rear_right}"


@dataclass
class ContactPoint:
    front_left: Vector3f
    front_right: Vector3f
    rear_left: Vector3f
    rear_right: Vector3f

    @staticmethod
    def from_list(points: List[List[float]]) -> Any:
        fl = Vector3f(*points[0])
        fr = Vector3f(*points[1])
        rl = Vector3f(*points[2])
        rr = Vector3f(*points[3])

        return ContactPoint(fl, fr, rl, rr)

    def __str__(self) -> str:
        return f"FL: {self.front_left},\nFR: {self.front_right},\
            \nRL: {self.rear_left},\nRR: {self.rear_right}"


@dataclass
class CarDamage:
    front: float
    rear: float
    left: float
    right: float
    center: float


@dataclass
class PhysicsMap:

    packed_id: int
    gas: float
    brake: float
    fuel: float
    gear: int
    rpm: int
    steer_angle: float
    speed_kmh: float
    velocity: Vector3f
    g_force: Vector3f  # same as accG

    wheel_slip: Wheels
    wheel_pressure: Wheels
    wheel_angular_s: Wheels
    tyre_core_temp: Wheels

    suspension_travel: Wheels

    drs: float
    tc: float
    heading: float
    pitch: float
    roll: float
    car_damage: CarDamage
    pit_limiter_on: bool
    abs: float

    autoshifter_on: bool
    turbo_boost: float

    air_temp: float
    road_temp: float
    local_angular_vel: Vector3f
    final_ff: float

    brake_temp: Wheels
    clutch: float

    is_ai_controlled: bool

    tyre_contact_point: ContactPoint
    tyre_contact_normal: ContactPoint
    tyre_contact_heading: ContactPoint

    brake_bias: float
    local_velocity: Vector3f

    @staticmethod
    def is_equal(a: PhysicsMap, b: PhysicsMap) -> bool:
        """
        Since I won't check every single attribute,
        comparing suspension_travel is a good alternative
        since there is always a bit of oscillation in the
        suspension when the car is possessed by the player.

        Parameters:
        a: PhysicsMap
        b: PhysicsMap

        Return:
        result: bool
        """
        return a.suspension_travel == b.suspension_travel

    def to_dict(self) -> dict:
        return dataclass_to_dict(self)


@dataclass
class GraphicsMap:
    packet_id: int
    status: AC_STATUS
    session_type: AC_SESSION_TYPE

    current_time_str: str
    last_time_str: str
    best_time_str: str
    split_str: str

    completed_laps: int
    position: int
    i_current_time: int
    i_last_time: int
    i_best_time: int

    session_time_left: float
    distance_traveled: float
    is_in_pit: bool
    current_sector_index: int
    last_sector_time: int
    number_of_laps: int

    tyre_compound: str

    replay_time_multiplier: float
    normalized_car_position: float
    car_coordinates: Vector3f

    penalty_time: float
    flag: AC_FLAG_TYPE
    ideal_line_on: bool

    # Since 1.5
    is_in_pit_lane: bool
    surface_grip: float

    # Since 1.13
    mandatory_pit_done: bool

    def to_dict(self) -> dict:
        return dataclass_to_dict(self)


@dataclass
class StaticsMap:

    sm_version: str
    ac_version: str
    number_of_session: int
    num_cars: int
    car_model: str
    track: str
    player_name: str
    player_surname: str
    player_nick: str
    sector_count: int
    max_torque: float
    max_power: float
    max_rpm: int
    max_fuel: float
    suspension_max_travel: List[float]
    tyre_radius: List[float]
    max_turbo_boost: float

    penalty_enabled: bool
    aid_fuel_rate: float
    aid_tyre_rate: float
    aid_mechanical_damage: float
    allow_tyre_blankets: int
    aid_stability: float
    aid_auto_clutch: bool
    aid_auto_blip: int
    has_drs: int
    has_ers: int
    has_kers: int
    ker_max_joules: float
    engine_brake_settings_count: int
    ers_power_controller_count: int

    # since 1.7.1
    track_sp_line_length: float
    track_configuration: str

    # since 1.10.2
    ers_max_j: float

    # since 1.13
    is_timed_race: int
    has_extra_lap: int
    car_skin: str
    reversed_grid_positions: int
    pit_window_start: int
    pit_window_end: int

    def to_dict(self) -> dict:
        return dataclass_to_dict(self)


@dataclass
class AC_map:

    Physics: PhysicsMap
    Graphics: GraphicsMap
    Static: StaticsMap

    def to_dict(self) -> dict:
        return dataclass_to_dict(self)


class acSM(mmap.mmap):

    def __init__(self, *args, **kwargs):
        super().__init__()

    def unpack_value(self, value_type: str, padding=0) -> float:
        bytes = self.read(4 + padding)
        format = f"={value_type}{padding}x"
        return struct.unpack(format, bytes)[0]

    def unpack_array(self, value_type: str, count: int, padding=0) -> tuple:

        if value_type in ("i", "f"):
            format = f"={count}{value_type}{padding}x"
            bytes = self.read(4 * count + padding)
            value = struct.unpack(format, bytes)

        else:
            value = self.read(2 * count + padding)

        return value

    def unpack_array2D(self, value_type: str, count: int, subCount: int) -> tuple:
        data = []
        for _ in range(count):
            data.append(self.unpack_array(value_type, subCount))
        return tuple(data)

    def unpack_string(self, count, padding=0) -> str:
        string_bytes = self.read(2 * count + padding)
        return string_bytes.decode("utf-16", errors="ignore")


def read_physic_map(physic_map: acSM) -> PhysicsMap:
    physic_map.seek(0)
    temp = {
        "packetID": physic_map.unpack_value("i"),
        "gas": physic_map.unpack_value("f"),
        "brake": physic_map.unpack_value("f"),
        "fuel": physic_map.unpack_value("f"),
        "gear": physic_map.unpack_value("i"),
        "rpm": physic_map.unpack_value("i"),
        "steerAngle": physic_map.unpack_value("f"),
        "speedKmh": physic_map.unpack_value("f"),
        "velocity": physic_map.unpack_array("f", 3),
        "accG": physic_map.unpack_array("f", 3),
        "wheelSlip": physic_map.unpack_array("f", 4),
        "wheelLoad": physic_map.unpack_array("f", 4),
        "wheelsPressure": physic_map.unpack_array("f", 4),
        "wheelAngularSpeed": physic_map.unpack_array("f", 4),
        "tyreWear": physic_map.unpack_array("f", 4),
        "tyreDirtyLevel": physic_map.unpack_array("f", 4),
        "tyreCoreTemperature": physic_map.unpack_array("f", 4),
        "camberRAD": physic_map.unpack_array("f", 4),
        "suspensionTravel": physic_map.unpack_array("f", 4),
        "drs": physic_map.unpack_value("f"),
        "tc": physic_map.unpack_value("f"),
        "heading": physic_map.unpack_value("f"),
        "pitch": physic_map.unpack_value("f"),
        "roll": physic_map.unpack_value("f"),
        "cgHeight": physic_map.unpack_value("f"),
        "carDamage": physic_map.unpack_array("f", 5),
        "numberOfTyresOut": physic_map.unpack_value("i"),
        "pitLimiterOn": physic_map.unpack_value("i"),
        "abs": physic_map.unpack_value("f"),
        "kersCharge": physic_map.unpack_value("f"),
        "kersInput": physic_map.unpack_value("f"),
        "autoshifterOn": physic_map.unpack_value("i"),
        "rideHeight": physic_map.unpack_array("f", 2),
        "turboBoost": physic_map.unpack_value("f"),
        "ballast": physic_map.unpack_value("f"),
        "airDensity": physic_map.unpack_value("f"),
        "airTemp": physic_map.unpack_value("f"),
        "roadTemp": physic_map.unpack_value("f"),
        "localAngularVel": physic_map.unpack_array("f", 3),
        "FinalFF": physic_map.unpack_value("f"),
        "performanceMeter": physic_map.unpack_value("f"),
        "engineBrake": physic_map.unpack_value("i"),
        "ersRecoveryLevel": physic_map.unpack_value("i"),
        "ersPowerLevel": physic_map.unpack_value("i"),
        "ersHeatCharging": physic_map.unpack_value("i"),
        "ersIsCharging": physic_map.unpack_value("i"),
        "kersCurrentKJ": physic_map.unpack_value("f"),
        "drsAvailable": physic_map.unpack_value("i"),
        "drsEnabled": physic_map.unpack_value("i"),
        "brakeTemp": physic_map.unpack_array("f", 4),
        "clutch": physic_map.unpack_value("f"),
        "tyreTempI": physic_map.unpack_array("f", 4),
        "tyreTempM": physic_map.unpack_array("f", 4),
        "tyreTempO": physic_map.unpack_array("f", 4),
        "isAIControlled": physic_map.unpack_value("i"),
        "tyreContactPoint": physic_map.unpack_array2D("f", 4, 3),
        "tyreContactNormal": physic_map.unpack_array2D("f", 4, 3),
        "tyreContactHeading": physic_map.unpack_array2D("f", 4, 3),
        "brakeBias": physic_map.unpack_value("f"),
        "localVelocity": physic_map.unpack_array("f", 3),
    }

    return PhysicsMap(
        temp["packetID"],
        temp["gas"],
        temp["brake"],
        temp["fuel"],
        temp["gear"],
        temp["rpm"],
        temp["steerAngle"],
        temp["speedKmh"],
        Vector3f(*temp["velocity"]),
        Vector3f(*temp["accG"]),
        Wheels(*temp["wheelSlip"]),
        Wheels(*temp["wheelsPressure"]),
        Wheels(*temp["wheelAngularSpeed"]),
        Wheels(*temp["tyreCoreTemperature"]),
        Wheels(*temp["suspensionTravel"]),
        temp["drs"],
        temp["tc"],
        temp["heading"],
        temp["pitch"],
        temp["roll"],
        CarDamage(*temp["carDamage"]),
        bool(temp["pitLimiterOn"]),
        temp["abs"],
        bool(temp["autoshifterOn"]),
        temp["turboBoost"],
        temp["airTemp"],
        temp["roadTemp"],
        Vector3f(*temp["localAngularVel"]),
        temp["FinalFF"],
        Wheels(*temp["brakeTemp"]),
        temp["clutch"],
        bool(temp["isAIControlled"]),
        ContactPoint.from_list(temp["tyreContactPoint"]),
        ContactPoint.from_list(temp["tyreContactNormal"]),
        ContactPoint.from_list(temp["tyreContactHeading"]),
        temp["brakeBias"],
        Vector3f(*temp["localVelocity"]),
    )


def read_graphics_map(graphic_map: acSM) -> GraphicsMap:
    graphic_map.seek(0)
    temp = {
        "packetID": graphic_map.unpack_value("i"),
        "status": AC_STATUS(graphic_map.unpack_value("i")),
        "session": AC_SESSION_TYPE(graphic_map.unpack_value("i")),
        "currentTime": graphic_map.unpack_string(15),
        "lastTime": graphic_map.unpack_string(15),
        "bestTime": graphic_map.unpack_string(15),
        "split": graphic_map.unpack_string(15),
        "completedLaps": graphic_map.unpack_value("i"),
        "position": graphic_map.unpack_value("i"),
        "iCurrentTime": graphic_map.unpack_value("i"),
        "iLastTime": graphic_map.unpack_value("i"),
        "iBestTime": graphic_map.unpack_value("i"),
        "sessionTimeLeft": graphic_map.unpack_value("f"),
        "distanceTraveled": graphic_map.unpack_value("f"),
        "isInPit": graphic_map.unpack_value("i"),
        "currentSectorIndex": graphic_map.unpack_value("i"),
        "lastSectorTime": graphic_map.unpack_value("i"),
        "numberOfLaps": graphic_map.unpack_value("i"),
        # TyreCompound (33 chars). Usually need padding=2 if it's UTF-16
        "tyreCompound": graphic_map.unpack_string(33, padding=2),
        "replayTimeMultiplier": graphic_map.unpack_value("f"),
        "normalizedCarPosition": graphic_map.unpack_value("f"),
        # CarCoordinates (3 floats)
        "carCoordinates": graphic_map.unpack_array("f", 3),
        "penaltyTime": graphic_map.unpack_value("f"),
        "flag": AC_FLAG_TYPE(graphic_map.unpack_value("i")),
        "idealLineOn": graphic_map.unpack_value("i"),
        # (since 1.5) IsInPitLane, SurfaceGrip
        "isInPitLane": graphic_map.unpack_value("i"),
        "surfaceGrip": graphic_map.unpack_value("f"),
        # (since 1.13) MandatoryPitDone
        "mandatoryPitDone": graphic_map.unpack_value("i"),
    }

    return GraphicsMap(
        packet_id=temp["packetID"],
        status=temp["status"],
        session_type=temp["session"],
        current_time_str=temp["currentTime"],
        last_time_str=temp["lastTime"],
        best_time_str=temp["bestTime"],
        split_str=temp["split"],
        completed_laps=temp["completedLaps"],
        position=temp["position"],
        i_current_time=temp["iCurrentTime"],
        i_last_time=temp["iLastTime"],
        i_best_time=temp["iBestTime"],
        session_time_left=temp["sessionTimeLeft"],
        distance_traveled=temp["distanceTraveled"],
        is_in_pit=bool(temp["isInPit"]),
        current_sector_index=temp["currentSectorIndex"],
        last_sector_time=temp["lastSectorTime"],
        number_of_laps=temp["numberOfLaps"],
        tyre_compound=temp["tyreCompound"],
        replay_time_multiplier=temp["replayTimeMultiplier"],
        normalized_car_position=temp["normalizedCarPosition"],
        car_coordinates=Vector3f(*temp["carCoordinates"]),
        penalty_time=temp["penaltyTime"],
        flag=temp["flag"],
        ideal_line_on=bool(temp["idealLineOn"]),
        is_in_pit_lane=bool(temp["isInPitLane"]),
        surface_grip=temp["surfaceGrip"],
        mandatory_pit_done=bool(temp["mandatoryPitDone"]),
    )


def read_static_map(static_map: acSM) -> StaticsMap:
    static_map.seek(0)

    temp = {
        "smVersion": static_map.unpack_string(15),
        "acVersion": static_map.unpack_string(15),
        "numberOfSessions": static_map.unpack_value("i"),
        "numCars": static_map.unpack_value("i"),
        "carModel": static_map.unpack_string(33),
        "track": static_map.unpack_string(33),
        "playerName": static_map.unpack_string(33),
        "playerSurname": static_map.unpack_string(33),
        "playerNick": static_map.unpack_string(33, 2),
        "sectorCount": static_map.unpack_value("i"),
        "maxTorque": static_map.unpack_value("f"),
        "maxPower": static_map.unpack_value("f"),
        "maxRpm": static_map.unpack_value("i"),
        "maxFuel": static_map.unpack_value("f"),
        "suspensionMaxTravel": static_map.unpack_array("f", 4),
        "tyreRadius": static_map.unpack_array("f", 4),
        "maxTurboBoost": static_map.unpack_value("f"),
        "deprecated_1": static_map.unpack_value("f"),
        "deprecated_2": static_map.unpack_value("f"),
        "penaltiesEnabled": static_map.unpack_value("i"),
        "aidFuelRate": static_map.unpack_value("f"),
        "aidTireRate": static_map.unpack_value("f"),
        "aidMechanicalDamage": static_map.unpack_value("f"),
        "AllowTyreBlankets": static_map.unpack_value("i"),
        "aidStability": static_map.unpack_value("f"),
        "aidAutoClutch": static_map.unpack_value("i"),
        "aidAutoBlip": static_map.unpack_value("i"),
        "hasDRS": static_map.unpack_value("i"),
        "hasERS": static_map.unpack_value("i"),
        "hasKERS": static_map.unpack_value("i"),
        "kersMaxJ": static_map.unpack_value("f"),
        "engineBrakeSettingsCount": static_map.unpack_value("i"),
        "ersPowerControllerCount": static_map.unpack_value("i"),
        "trackSplineLength": static_map.unpack_value("f"),
        "trackConfiguration": static_map.unpack_string(15, 2),
        "ersMaxJ": static_map.unpack_value("f"),
        "isTimedRace": static_map.unpack_value("i"),
        "hasExtraLap": static_map.unpack_value("i"),
        "carSkin": static_map.unpack_string(33, 2),
        "reversedGridPositions": static_map.unpack_value("i"),
        "PitWindowStart": static_map.unpack_value("i"),
        "PitWindowEnd": static_map.unpack_value("i"),
    }
    return StaticsMap(
        sm_version=temp["smVersion"],
        ac_version=temp["acVersion"],
        number_of_session=temp["numberOfSessions"],
        num_cars=temp["numCars"],
        car_model=temp["carModel"],
        track=temp["track"],
        player_name=temp["playerName"],
        player_surname=temp["playerSurname"],
        player_nick=temp["playerNick"],
        sector_count=temp["sectorCount"],
        max_torque=temp["maxTorque"],
        max_power=temp["maxPower"],
        max_rpm=temp["maxRpm"],
        max_fuel=temp["maxFuel"],
        # For these two, consider updating your dataclass if you want them as lists
        suspension_max_travel=temp["suspensionMaxTravel"],
        tyre_radius=temp["tyreRadius"],
        max_turbo_boost=temp["maxTurboBoost"],
        penalty_enabled=bool(temp["penaltiesEnabled"]),
        aid_fuel_rate=temp["aidFuelRate"],
        aid_tyre_rate=temp["aidTireRate"],
        aid_mechanical_damage=temp["aidMechanicalDamage"],
        allow_tyre_blankets=temp["AllowTyreBlankets"],
        aid_stability=temp["aidStability"],
        aid_auto_clutch=bool(temp["aidAutoClutch"]),
        aid_auto_blip=temp["aidAutoBlip"],
        has_drs=temp["hasDRS"],
        has_ers=temp["hasERS"],
        has_kers=temp["hasKERS"],
        ker_max_joules=temp["kersMaxJ"],
        engine_brake_settings_count=temp["engineBrakeSettingsCount"],
        ers_power_controller_count=temp["ersPowerControllerCount"],
        # track_sp_line_length in the dataclass is an int; cast if you want to preserve that type
        track_sp_line_length=temp["trackSplineLength"],
        track_configuration=temp["trackConfiguration"],
        ers_max_j=temp["ersMaxJ"],
        is_timed_race=temp["isTimedRace"],
        has_extra_lap=temp["hasExtraLap"],
        car_skin=temp["carSkin"],
        reversed_grid_positions=temp["reversedGridPositions"],
        pit_window_start=temp["PitWindowStart"],
        pit_window_end=temp["PitWindowEnd"],
    )


class acSharedMemory:

    def __init__(self) -> None:

        self.physicSM = acSM(
            -1, 800, tagname="Local\\acpmf_physics", access=mmap.ACCESS_WRITE
        )
        self.graphicSM = acSM(
            -1, 1588, tagname="Local\\acpmf_graphics", access=mmap.ACCESS_WRITE
        )
        self.staticSM = acSM(
            -1, 784, tagname="Local\\acpmf_static", access=mmap.ACCESS_WRITE
        )

        self.physics_old = None
        self.last_physicsID = 0

    def read_shared_memory(self) -> Optional[AC_map]:

        physics = read_physic_map(self.physicSM)
        graphics = read_graphics_map(self.graphicSM)
        statics = read_static_map(self.staticSM)

        if physics.packed_id == self.last_physicsID or (
            self.physics_old is not None
            and PhysicsMap.is_equal(self.physics_old, physics)
        ):
            return None

        else:
            self.physics_old = copy.deepcopy(physics)
            return AC_map(physics, graphics, statics)

    def get_shared_memory_data(self) -> AC_map:

        # try 1000 time to get the data, else raise exception
        for i in range(1000):

            data = self.read_shared_memory()
            if data is not None:
                return data

        else:
            raise SharedMemoryTimeout("No data available to read")

    def close(self) -> None:
        print("[ASM_Reader]: Closing memory maps.")
        self.physicSM.close()
        self.graphicSM.close()
        self.staticSM.close()


def simple_test() -> None:

    asm = acSharedMemory()

    for i in range(1000):
        sm = asm.read_shared_memory()

        if sm is not None and i % 200 == 0:
            print("Physics:")
            print(f"Speed: {sm.Physics.speed_kmh}")

            print("Graphics:")
            print(f"Car coordinates: {sm.Graphics.car_coordinates}")

            print("Static: ")
            print(f"Max RPM: {sm.Static.max_rpm}")

    asm.close()


if __name__ == "__main__":
    simple_test()
