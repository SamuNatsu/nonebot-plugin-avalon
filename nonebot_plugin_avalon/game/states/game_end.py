from . import StateEnum
from ..game import Game
from ..role import ROLE_NAME
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")

from nonebot_plugin_alconna import UniMessage


# On enter
async def enter(self: Game, _: StateEnum, win: bool, reason: str) -> None:
  self.clean_up()

  msg: UniMessage = (
    UniMessage
      .text("🔵正义方获胜\n" if win else "🔴邪恶方获胜\n")
      .text(reason + "\n")
      .text("📃玩家身份名单：\n")
  )

  for pl in self.players.values():
    msg.text(ROLE_NAME[pl.role]).at(pl.user_id).text("\n")

  await msg.text("🎮感谢各位的游玩")

# Register state
Game.register_state(State(StateEnum.GAME_END, final=True, enter=enter))
