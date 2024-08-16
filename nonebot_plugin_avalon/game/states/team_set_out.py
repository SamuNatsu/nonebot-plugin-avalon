import asyncio

from . import StateEnum
from ..game import Game
from ..role import RoleEnum
from ..round import ROUND_PROTECT
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")

from nonebot_plugin_alconna import (
  Alconna, AlconnaMatches, Args, Arparma, UniMessage, on_alconna
)
from nonebot_plugin_session import EventSession, SessionLevel
from nonebot_plugin_userinfo import UserInfo, EventUserInfo


# On enter
async def enter(self: Game, _: StateEnum) -> None:
  self.vote = {}

  # State-scope matcher handlers
  async def handle_success(
    session: EventSession,
    user_info: UserInfo = EventUserInfo(),
    result: Arparma = AlconnaMatches()
  ) -> None:
    # Private msg & Key matched & Is player
    if (
      session.level == SessionLevel.PRIVATE and
      result.main_args["key"] == self.key and
      session.id1 in self.players
    ):
      await self.on_msg(type="success", user_id=user_info.user_id)

  async def handle_fail(
    session: EventSession,
    user_info: UserInfo = EventUserInfo(),
    result: Arparma = AlconnaMatches()
  ) -> None:
    # Private msg & Key matched & Is player
    if (
      session.level == SessionLevel.PRIVATE and
      result.main_args["key"] == self.key and
      session.id1 in self.players
    ):
      await self.on_msg(type="fail", user_id=user_info.user_id)

  # Create matchers
  self.matchers["success"] = on_alconna(
    Alconna(".awl成功", Args["key", str]),
    handlers=[handle_success]
  )
  self.matchers["fail"] = on_alconna(
    Alconna(".awl失败", Args["key", str]),
    handlers=[handle_fail]
  )

  msg: UniMessage = (
    UniMessage
      .text(f"📣请队伍队员在机器人私信中秘密表决任务成功与否\n")
      .text(
        "🛡️当前轮次为保护轮，至少需要2个失败才能使任务失败\n"
        if (
          ROUND_PROTECT[len(self.players)] != None and
          ROUND_PROTECT[len(self.players)] == self.round + 1
        )
        else ""
      )
      .text("📃队员名单：")
  )
  for i in self.team:
    msg.at(i)

  await (
    msg
      .text(f"\n[.awl成功 {self.key}] 任务成功（仅私信）\n")
      .text(f"[.awl失败 {self.key}] 任务失败（仅私信）")
      .send(self.guild_target)
    )

# On message
async def msg(self: Game, type: str, user_id: str) -> None:
  if user_id not in self.team:
    await UniMessage.text("⚠️你不是队员").send(reply_to=True)
    return

  if user_id in self.vote:
    await (
      UniMessage
        .text(f"⚠️你已经表决了 {"[✅任务成功]" if self.vote[user_id] else "[❎任务失败]"}")
        .send(reply_to=True)
    )
    return

  if type == "success":
    self.vote[user_id] = True
    await asyncio.gather(
      UniMessage.text("✅你表决了任务成功").send(reply_to=True),
      UniMessage
        .text(f"📣[{self.players[user_id].name}] 完成了秘密表决\n")
        .text(f"⌛进度：{len(self.vote)}/{len(self.team)}")
        .send(self.guild_target)
    )

  if type == "fail":
    if self.players[user_id].role in { RoleEnum.MERLIN, RoleEnum.PERCIVAL, RoleEnum.SERVANT }:
      await (
        UniMessage
          .text(f"⚠️正义方只能表决任务成功")
          .send(reply_to=True)
      )
    else:
      self.vote[user_id] = False
      await asyncio.gather(
        UniMessage.text("❎你表决了任务失败").send(reply_to=True),
        UniMessage
          .text(f"📣[{self.players[user_id].name}] 完成了秘密表决")
          .send(self.guild_target)
      )

  if len(self.vote) == len(self.team):
    fail: int = len(list(filter(lambda x: not x, self.vote.values())))
    if (
      ROUND_PROTECT[len(self.players)] != None and
      ROUND_PROTECT[len(self.players)] == self.round + 1
    ):
      fail -= 1

    succs: int = len(list(filter(lambda x: x, self.vote.values())))
    fails: int = len(self.vote) - succs

    if fail > 0:
      self.round_states[self.round] = False
      await (
        UniMessage
          .text("❎任务失败了\n")
          .text(f"票形：{"🟩" * succs}{"🟥" * fails}")
          .send(self.guild_target)
      )
    else:
      self.round_states[self.round] = True
      await (
        UniMessage
          .text("✅任务成功了\n")
          .text(f"票形：{"🟩" * succs}{"🟥" * fails}")
          .send(self.guild_target)
      )

    await self.to_state(StateEnum.NEXT_LEADER)

# On exit
async def exit(self: Game, _: StateEnum) -> None:
  self.remove_matchers("success", "fail")

# Register state
Game.register_state(
  State(StateEnum.TEAM_SET_OUT, enter=enter, msg=msg, exit=exit)
)
