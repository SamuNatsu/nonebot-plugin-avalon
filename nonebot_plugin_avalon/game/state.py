from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Concatenate, ParamSpec, TypeAlias


P = ParamSpec('P')

StateId: TypeAlias      = Any
EnterHandler: TypeAlias = Callable[
  Concatenate[Any, StateId, P], Awaitable[None]
]
MsgHandler: TypeAlias   = Callable[Concatenate[Any, P], Awaitable[None]]
ExitHandler: TypeAlias  = Callable[[Any, StateId], Awaitable[None]]


@dataclass(frozen=True)
class State:
  id:      StateId
  initial: bool                = False
  final:   bool                = False
  enter:   EnterHandler | None = None
  msg:     MsgHandler   | None = None
  exit:    ExitHandler  | None = None
