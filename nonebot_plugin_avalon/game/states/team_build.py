from . import StateEnum
from ..game import Game
from ..role import ROLE_SET
from ..round import ROUND_SET
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import (
  Alconna, AlconnaMatches, Args, Arparma, At, MultiVar, UniMessage, on_alconna
)

require("nonebot_plugin_session")
from nonebot_plugin_session import EventSession, SessionLevel


# On enter
async def enter(self: Game, _: StateEnum) -> None:
  async def handle_build(
    session: EventSession,
    result: Arparma = AlconnaMatches()
  ) -> None:
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 == self.leader
    ):
      await self.on_msg(users=[i.target for i in result.main_args["targets"]])

  self.matchers["build"] = on_alconna(
    Alconna(".awl组队", Args["targets", MultiVar(At)]),
    handlers=[handle_build]
  )

  await self.print_status()
  await (
    UniMessage
      .text(f"📣第{self.round + 1}轮任务开始，请队长进行队伍构建\n")
      .text(f"👑当前队长：{self.players[self.leader].name}\n")
      .text(f"⚠️本轮任务需要{ROLE_SET[len(self.players)][self.round]}人参与")
      .text("""[.awl组队 <@某人 @某人 ...>] 携带某些玩家组建队伍（仅队长）
[.awl状态] 查看当前游戏状态
[.awl玩家] 查看房间玩家列表
[.awl结束] 强制结束游戏（仅房主）""")
      .send(self.guild_target)
    )

# On message
async def msg(self: Game, users: list[str]) -> None:
  self.team = set(users)

  if len(self.team) != ROUND_SET[len(self.players)][self.round]:
    await (
      UniMessage
        .text("⚠️队伍人数不满足要求\n")
        .text(f"本轮需要{ROUND_SET[len(self.players)][self.round]}人\n")
        .text(f"队长选择了{len(users)}人")
        .send()
    )
    return

  # TODO
  await self.to_state(StateEnum.FORCE_END, reason="测试结束")

# On exit
async def exit(self: Game) -> None:
  self.matchers["build"].destroy()
  self.matchers.pop("build")

# Register state
Game.register_state(
  State(StateEnum.TEAM_BUILD, enter=enter, msg=msg, exit=exit)
)
