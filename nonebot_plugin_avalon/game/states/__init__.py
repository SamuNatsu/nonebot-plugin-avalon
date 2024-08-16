from enum import Enum, auto, unique


@unique
class StateEnum(Enum):
  WAIT_START   = auto()
  INITIALIZE   = auto()
  TEAM_BUILD   = auto()
  TEAM_VOTE    = auto()
  TEAM_SET_OUT = auto()
  NEXT_LEADER  = auto()
  ASSASSINATE  = auto()
  GAME_END     = auto()
  FORCE_END    = auto()
