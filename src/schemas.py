from enum import Enum


class ACC_EVENTS(Enum):
    ACC_IDLE = 0
    ACC_START_RACE = 1
    ACC_PAUSE_RACE = 2
    ACC_RESUME_RACE = 3
    ACC_STOP_RACE = 4
    ACC_REPLAY_EVENT = 5

    def __str__(self) -> str:

        if self == ACC_EVENTS.ACC_IDLE:
            event = "idle"
        elif self == ACC_EVENTS.ACC_START_RACE:
            event = "start_race"
        elif self == ACC_EVENTS.ACC_PAUSE_RACE:
            event = "pause_race"
        elif self == ACC_EVENTS.ACC_RESUME_RACE:
            event = "resume_race"
        elif self == ACC_EVENTS.ACC_STOP_RACE:
            event = "stop_race"
        elif self == ACC_EVENTS.ACC_REPLAY_EVENT:
            event = "replay_race"
        else:
            event = "unknown"
        return event
