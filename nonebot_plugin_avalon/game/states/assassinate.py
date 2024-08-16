from . import StateEnum
from ..game import Game
from ..role import RoleEnum
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")

from nonebot_plugin_alconna import (
  Alconna, AlconnaMatches, Args, Arparma, At, UniMessage, on_alconna
)
from nonebot_plugin_session import EventSession, SessionLevel


# On enter
async def enter(self: Game, _: StateEnum, final: bool) -> None:
  self.remove_matchers("assassinate")

  # State-scope matcher handlers
  async def handle_assassinate(
    session: EventSession,
    result: Arparma = AlconnaMatches()
  ) -> None:
    # Group msg & Is room & Is player & Is assassin
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 in self.players and
      session.id1 == self.assassin_id
    ):
      await self.on_msg(final=final, target=result.main_args["target"].target)

  # Create matchers
  self.matchers["assassinate"] = on_alconna(
    Alconna(".awl刺杀", Args["target", At]),
    handlers=[handle_assassinate]
  )

  if final:
    await (
      UniMessage
        .text(f"🗡️进入最终刺杀阶段，请刺客 [{self.players[self.assassin_id].name}] 发起刺杀\n")
        .text("⚠️若成功刺杀梅林，则邪恶方翻盘获胜，否则正义方获胜\n")
        .text(f"[.awl刺杀 @某人] 指定刺杀对象（仅刺客）")
        .send(self.guild_target)
    )
  else:
    await (
      UniMessage
        .text(f"🗡️刺客 [{self.players[self.assassin_id].name}] 发起了刺杀\n")
        .text("⚠️若成功刺杀梅林，则邪恶方直接获胜，否则正义方直接获胜\n")
        .text(f"[.awl刺杀 @某人] 指定刺杀对象（仅刺客）")
        .send(self.guild_target)
    )

# On message
async def msg(self: Game, final: bool, target: str) -> None:
  if target not in self.players:
    await UniMessage.text("⚠️刺杀对象不是玩家").send(reply_to=True)
    return

  if self.players[target].role == RoleEnum.MERLIN:
    await self.to_state(StateEnum.GAME_END, win=False, reason="成功刺杀梅林")
  else:
    await self.to_state(
      StateEnum.GAME_END,
      win=True,
      reason="完成3轮任务并且梅林躲过了刺杀" if final else "梅林躲过了刺杀"
    )

# On exit
async def exit(self: Game, _: StateEnum) -> None:
  self.remove_matchers("assassinate")

# Register state
Game.register_state(
  State(StateEnum.ASSASSINATE, enter=enter, msg=msg, exit=exit)
)
