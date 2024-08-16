import traceback

from .state import State, StateId

from abc import abstractmethod
from nonebot.log import logger


class StateMachine:
  # Class variables
  _initial_state: StateId | None = None
  _states: dict[StateId, State] = {}

  # Instance variables
  _current_state: StateId

  # Class methods
  @classmethod
  def register_state(cls, state: State):
    cls._states[state.id] = state

    if state.initial:
      if cls._initial_state != None:
        raise ValueError("a state machine can ONLY has ONE initial state")
      else:
        cls._initial_state = state.id

  # Abstract methods
  @abstractmethod
  async def exception_handler(self, e: Exception) -> None:
    raise NotImplemented

  # Instance methods
  def __init__(self) -> None:
    if self._initial_state == None:
      raise ValueError("a state machine MUST has an initial state")

    self._current_state = self._initial_state

  async def startup(self, **kwargs) -> None:
    current_state: State = self.get_current_state()

    if current_state.enter != None:
      try:
        await current_state.enter(self, current_state.id, **kwargs)
      except Exception as e:
        logger.error(traceback.format_exc())
        await self.exception_handler(e)
        return

  def get_current_state(self) -> State:
    return self._states[self._current_state]

  def is_state(self, *args) -> bool:
    return self._current_state in args

  async def to_state(self, id: StateId, **kwargs) -> None:
    current_state: State = self.get_current_state()

    if current_state.final:
      return

    if current_state.exit != None:
      try:
        await current_state.exit(self, id)
      except Exception as e:
        logger.error(traceback.format_exc())
        await self.exception_handler(e)
        return

    last_state: StateId = self._current_state
    self._current_state = id
    current_state = self.get_current_state()

    if current_state.enter != None:
      try:
        await current_state.enter(self, last_state, **kwargs)
      except Exception as e:
        logger.error(traceback.format_exc())
        await self.exception_handler(e)

  async def on_msg(self, **kwargs) -> None:
    current_state: State = self.get_current_state()

    if current_state.final:
      return

    if current_state.msg != None:
      try:
        await current_state.msg(self, **kwargs)
      except Exception as e:
        logger.error(traceback.format_exc())
        await self.exception_handler(e)
        return
