from enum import Enum


class AC_EVENTS(Enum):
    AC_IDLE = 0
    AC_START_RACE = 1
    AC_PAUSE_RACE = 2
    AC_RESUME_RACE = 3
    AC_STOP_RACE = 4
    AC_REPLAY_EVENT = 5
    AC_UNKNOWN = 6

    def __str__(self) -> str:

        if self == AC_EVENTS.AC_IDLE:
            event = "idle"
        elif self == AC_EVENTS.AC_START_RACE:
            event = "start_race"
        elif self == AC_EVENTS.AC_PAUSE_RACE:
            event = "pause_race"
        elif self == AC_EVENTS.AC_RESUME_RACE:
            event = "resume_race"
        elif self == AC_EVENTS.AC_STOP_RACE:
            event = "stop_race"
        elif self == AC_EVENTS.AC_REPLAY_EVENT:
            event = "replay_race"
        elif self == AC_EVENTS.AC_UNKNOWN:
            event = "unknown"
        else:
            event = "unknown"
        return event


class SharedMemoryTimeout(Exception):
    pass


class AC_STATUS(Enum):
    AC_OFF = 0
    AC_REPLAY = 1
    AC_LIVE = 2
    AC_PAUSE = 3


class AC_SESSION_TYPE(Enum):
    AC_UNKNOW = -1
    AC_PRACTICE = 0
    AC_QUALIFY = 1
    AC_RACE = 2
    AC_HOTLAP = 3
    AC_TIME_ATTACK = 4
    AC_DRIFT = 5
    AC_DRAG = 6

    def __str__(self) -> str:

        if self == AC_SESSION_TYPE.AC_PRACTICE:
            string = "Practice"

        elif self == AC_SESSION_TYPE.AC_QUALIFY:
            string = "Qualify"

        elif self == AC_SESSION_TYPE.AC_RACE:
            string = "Race"

        elif self == AC_SESSION_TYPE.AC_HOTLAP:
            string = "Hotlap"

        elif self == AC_SESSION_TYPE.AC_TIME_ATTACK:
            string = "Time_Attack"

        elif self == AC_SESSION_TYPE.AC_DRIFT:
            string = "Drift"

        elif self == AC_SESSION_TYPE.AC_DRAG:
            string = "Drag"

        else:
            string = "Unknow"

        return string


class AC_FLAG_TYPE(Enum):
    AC_NO_FLAG = 0
    AC_BLUE_FLAG = 1
    AC_YELLOW_FLAG = 2
    AC_BLACK_FLAG = 3
    AC_WHITE_FLAG = 4
    AC_CHECKERED_FLAG = 5
    AC_PENALTY_FLAG = 6
