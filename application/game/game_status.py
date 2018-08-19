from enum import Enum


class GameStatus(Enum):
    SCHEDULED = "SCHEDULED"
    STARTING = "STARTING"
    ONGOING = "ONGOING"
    FINISHED = "FINISHED"
