import copy
import random

from . import StateEnum
from ..game import Game
from ..role import ROLE_NAME, ROLE_SET, ROLE_SET_NAME, RoleEnum
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import Target, UniMessage, on_alconna

require("nonebot_plugin_session")
from nonebot_plugin_session import EventSession, SessionLevel


# On enter
async def enter(self: Game, _: StateEnum) -> None:
  async def handle_status(session: EventSession) -> None:
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id
    ):
      await self.print_status()

  self.matchers["status"] = on_alconna(".awl状态", handlers=[handle_status])

  await (
    UniMessage
      .text(f"📣阿瓦隆{len(self.players)}人局开始\n\n")
      .text(ROLE_SET_NAME[len(self.players)])
      .send(self.guild_target)
  )

  roles: list[RoleEnum] = copy.deepcopy(ROLE_SET[len(self.players)])
  random.shuffle(roles)

  merlin_info: list[str] = []
  percival_info: list[str] = []
  evil_info: dict[str, RoleEnum] = {}

  for pl in self.players.values():
    self.players_order.append(pl.user_id)

    role: RoleEnum = roles.pop()
    pl.role = role

    if role in { RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.OBERON, RoleEnum.LACHEY }:
      merlin_info.append(pl.user_id)
    if role in { RoleEnum.MERLIN, RoleEnum.MORGANA }:
      percival_info.append(pl.user_id)
    if role in { RoleEnum.MORDRED, RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.LACHEY }:
      evil_info[pl.user_id] = role

  random.shuffle(self.players_order)
  random.shuffle(merlin_info)
  random.shuffle(percival_info)
  self.leader = self.players_order[0]

  await self.print_player_order()

  for pl in self.players.values():
    await (
      UniMessage
        .text(f"💡你的身份是：{ROLE_NAME[pl.role]}")
        .send(
          Target(pl.user_id, private=True, self_id=self.guild_target.self_id)
        )
    )

    if pl.role == RoleEnum.MERLIN:
      await (
        UniMessage
          .text("📃邪恶方名单：\n")
          .text(
            "\n".join([f"{self.players[i].name}({i})" for i in merlin_info])
          )
          .send(
            Target(pl.user_id, private=True, self_id=self.guild_target.self_id)
          )
      )
    elif pl.role == RoleEnum.PERCIVAL:
      await (
        UniMessage
          .text("📃TA们可能是梅林：\n")
          .text(
            "\n".join([f"{self.players[i].name}({i})" for i in percival_info])
          )
          .send(
            Target(pl.user_id, private=True, self_id=self.guild_target.self_id)
          )
      )
    elif pl.role in { RoleEnum.MORDRED, RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.LACHEY }:
      await (
        UniMessage
          .text("📃TA们是你的队友：\n")
          .text(
            "\n".join(
              [
                f"{self.players[i].name}{ROLE_NAME[j]}({i})"
                for i, j in evil_info.items()
              ]
            )
          )
          .send(
            Target(pl.user_id, private=True, self_id=self.guild_target.self_id)
          )
      )

  await self.to_state(StateEnum.TEAM_BUILD)

# Register state
Game.register_state(State(StateEnum.INITIALIZE, enter=enter))