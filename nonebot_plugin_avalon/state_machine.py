import inspect

from typing import Any


class State:
  id: Any
  enter: str | None
  msg: str | None
  exit: str | None
  final: bool

  def __init__(
    self,
    *,
    id: Any, enter: str | None = None,
    msg: str | None = None,
    exit: str | None = None,
    final: bool = False
  ) -> None:
    self.id = id
    self.enter = enter
    self.msg = msg
    self.exit = exit
    self.final = final


class StateMachine:
  current_state: State | None

  def __init__(self) -> None:
    self.current_state = None

  def _is_halted(self) -> bool:
    return self.current_state != None and self.current_state.final

  async def _exec_action(self, name: str, **kwargs) -> None:
    if not hasattr(self, name):
      raise NotImplementedError(name)

    method: Any = getattr(self, name)
    if not inspect.ismethod(method):
      raise TypeError(name)

    if inspect.iscoroutinefunction(method):
      await method(**kwargs)
    else:
      method(**kwargs)

  def is_state(self, *args) -> bool:
    return (
      self.current_state.id in args if self.current_state != None else False
    )

  async def to_state(self, next_state: State, **kwargs) -> None:
    if self._is_halted():
      return

    if self.current_state != None and self.current_state.exit != None:
      await self._exec_action(
        self.current_state.exit,
        next_state=next_state.id
      )

    if next_state.enter != None:
      await self._exec_action(
        next_state.enter,
        last_state=(
          self.current_state.id if self.current_state != None else None
        ),
        **kwargs
      )

    self.current_state = next_state

  async def on_msg(self, **kwargs) -> None:
    if self._is_halted():
      return

    if self.current_state != None and self.current_state.msg != None:
      await self._exec_action(self.current_state.msg, **kwargs)
