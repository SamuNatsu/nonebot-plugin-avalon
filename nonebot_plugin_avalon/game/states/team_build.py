from . import StateEnum
from ..game import Game
from ..round import ROUND_SET
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")

from nonebot_plugin_alconna import (
  Alconna, AlconnaMatches, Args, Arparma, At, MultiVar, UniMessage, on_alconna
)
from nonebot_plugin_session import EventSession, SessionLevel


# On enter
async def enter(self: Game, _: StateEnum) -> None:
  # State-scope matcher handlers
  async def handle_build(
    session: EventSession,
    result: Arparma = AlconnaMatches()
  ) -> None:
    # Group msg & Is room & Is leader
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 == self.leader
    ):
      await self.on_msg(users=[i.target for i in result.main_args["targets"]])

  # Create matchers
  self.matchers["build"] = on_alconna(
    Alconna(".awl组队", Args["targets", MultiVar(At)]),
    handlers=[handle_build]
  )

  await (
    UniMessage
      .text(f"📣第{self.round + 1}轮任务开始，请队长开始组队\n")
      .text(f"👑队长：").at(self.leader).text("\n")
      .text(f"⌛尝试组队次数：{self.build_tries}/5\n")
      .text(f"⚠️本轮任务需要{ROUND_SET[len(self.players)][self.round]}人参与\n")
      .text("[.awl组队 @某人 @某人 ...] 携带某些玩家组建队伍（仅队长）\n")
      .text("[.awl状态] 查看当前游戏状态\n")
      .text("[.awl玩家] 查看房间玩家列表")
      .send(self.guild_target)
    )

# On message
async def msg(self: Game, users: list[str]) -> None:
  self.team = set(filter(lambda x: x in self.players, users))

  if len(self.team) != ROUND_SET[len(self.players)][self.round]:
    await (
      UniMessage
        .text("⚠️队伍人数不满足要求\n")
        .text(f"本轮需要{ROUND_SET[len(self.players)][self.round]}人\n")
        .text(f"你选择了{len(self.team)}人")
        .send(reply_to=True)
    )
    return

  await self.to_state(StateEnum.TEAM_VOTE)

# On exit
async def exit(self: Game, _: StateEnum) -> None:
  self.remove_matchers("build")

# Register state
Game.register_state(
  State(StateEnum.TEAM_BUILD, enter=enter, msg=msg, exit=exit)
)
