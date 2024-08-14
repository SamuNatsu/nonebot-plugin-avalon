from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Concatenate, TypeAlias


StateId: TypeAlias      = Any
EnterHandler: TypeAlias = Callable[
  Concatenate[Any, StateId, ...], Awaitable[None]
]
MsgHandler: TypeAlias   = Callable[Concatenate[Any, ...], Awaitable[None]]
ExitHandler: TypeAlias  = Callable[[Any, StateId], Awaitable[None]]


@dataclass(frozen=True)
class State:
  id:      StateId
  initial: bool                = False
  final:   bool                = False
  enter:   EnterHandler | None = None
  msg:     MsgHandler   | None = None
  exit:    ExitHandler  | None = None
