from . import StateEnum
from ..game import Game
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import UniMessage


# On enter
async def enter(self: Game, _: StateEnum, reason: str) -> None:
  self.clean_up()
  await (
    UniMessage
      .text("❌游戏强制结束\n")
      .text(f"⚠️理由：{reason}")
      .send(self.guild_target)
  )

# Register state
Game.register_state(State(StateEnum.FORCE_END, final=True, enter=enter))
