from . import StateEnum
from ..game import Game
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")

from nonebot_plugin_alconna import UniMessage


# On enter
async def enter(self: Game, from_state: StateEnum) -> None:
  if from_state == StateEnum.TEAM_VOTE:
    self.build_tries += 1
    if self.build_tries > 5:
      await self.to_state(StateEnum.GAME_END, win=False, reason="连续5次组队失败")
      return

    self.leader = self.players_order[
      (self.players_order.index(self.leader) + 1) % len(self.players)
    ]

    await (
      UniMessage
        .text("⚠️组队失败，按照玩家顺位交换队长再次尝试组队\n")
        .send(self.guild_target)
    )
    await self.to_state(StateEnum.TEAM_BUILD)

  if from_state == StateEnum.TEAM_SET_OUT:
    self.build_tries = 1
    self.leader = self.players_order[
      (self.players_order.index(self.leader) + 1) % len(self.players)
    ]
    self.round += 1

    succs: int = len(list(filter(lambda x: x == True, self.round_states)))
    fails: int = self.round - succs

    if succs >= 3:
      await self.to_state(StateEnum.ASSASSINATE, final=True)
    elif fails >= 3:
      await self.to_state(StateEnum.GAME_END, win=False, reason="总计3次任务失败")
    else:
      await self.to_state(StateEnum.TEAM_BUILD)

# Register state
Game.register_state(State(StateEnum.NEXT_LEADER, enter=enter))
