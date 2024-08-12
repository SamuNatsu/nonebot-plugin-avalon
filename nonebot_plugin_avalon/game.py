from .state_machine import State, StateMachine

from datetime import UTC, datetime, timedelta
from enum import Enum, auto, unique
from nonebot import require
from nonebot.log import logger
from typing import Self

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import Target, UniMessage

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler


@unique
class StateEnum(Enum):
  WAIT_START   = auto()
  INITIALIZE   = auto()
  TEAM_BUILD   = auto()
  TEAM_VOTE    = auto()
  TEAM_SET_OUT = auto()
  TEAM_REJECT  = auto()
  NEXT_LEADER  = auto()
  ASSASSINATE  = auto()
  BLUE_WIN     = auto()
  RED_WIN      = auto()
  FORCE_END    = auto()

class Game(StateMachine):
  # Instances
  instances: dict[str, Self] = {}

  # States
  s_wait_start: State   = State(
    id=StateEnum.WAIT_START,
    enter="e_wait_start",
    msg="m_wait_start"
  )
  s_initialize: State   = State(id=StateEnum.INITIALIZE)
  s_team_build: State   = State(id=StateEnum.TEAM_BUILD)
  s_team_vote: State    = State(id=StateEnum.TEAM_VOTE)
  s_team_set_out: State = State(id=StateEnum.TEAM_SET_OUT)
  s_team_reject: State  = State(id=StateEnum.TEAM_REJECT)
  s_next_leader: State  = State(id=StateEnum.NEXT_LEADER)
  s_assassinate: State  = State(id=StateEnum.ASSASSINATE)
  s_blue_win: State     = State(id=StateEnum.BLUE_WIN, final=True)
  s_red_win: State      = State(id=StateEnum.RED_WIN, final=True)
  s_force_end: State    = State(
    id=StateEnum.FORCE_END,
    enter="e_force_end",
    final=True
  )

  # Members
  bot_id: str
  host_id: str
  guild_id: str
  players: set[str]

  # Constructor
  def __init__(self, bot_id: str, host_id: str, guild_id: str) -> None:
    super().__init__()

    self.bot_id = bot_id
    self.host_id = host_id
    self.guild_id = guild_id
    self.players = set()

    async def timeout() -> None:
      await self.to_state(Game.s_force_end, reason="游戏超时")
    scheduler.add_job(
      timeout,
      "date",
      run_date=datetime.now(UTC) + timedelta(hours=2),
      id=self.guild_id
    )

  # Enter events
  async def e_wait_start(self, last_state: str | None) -> None:
    await UniMessage.text(
      "本群组阿瓦隆游戏房间已由房主 "
    ).at(self.host_id).text(""" 开启
[.awl加入] 加入房间
[.awl退出] 退出房间
[.awl玩家] 查看房间玩家列表
[.awl踢人 <@某人>] 踢出房间（仅房主）
[.awl开始] 开始游戏（仅房主）
[.awl结束] 强制结束游戏（仅房主）""").send()

  async def e_force_end(self, last_state: str | None, reason: str) -> None:
    if scheduler.get_job(self.guild_id) != None:
      scheduler.remove_job(self.guild_id)
    Game.instances.pop(self.guild_id)

    await UniMessage.text(
      f"【阿瓦隆游戏强制结束】\n理由：{reason}"
    ).send(Target(self.guild_id, self_id=self.bot_id))

  # Message events
  async def m_wait_start(self, type: str, user_id: str) -> None:
    if type == "join" and user_id not in self.players:
      self.players.add(user_id)
      await UniMessage.text(
        f"【阿瓦隆房间：{len(self.players)}人】\n新玩家 "
      ).at(user_id).text(" 加入").send()
    elif type == "leave" and user_id in self.players:
      self.players.remove(user_id)
      await UniMessage.text(
        f"【阿瓦隆房间：{len(self.players)}人】\n玩家 "
      ).at(user_id).text(" 离开").send()
    elif type == "kick" and user_id in self.players:
      self.players.remove(user_id)
      await UniMessage.text(
        f"【阿瓦隆房间：{len(self.players)}人】\n玩家 "
      ).at(user_id).text(" 被踢出").send()
    else:
      await self.print_players()
      await self.to_state(Game.s_force_end, "等待插件继续更新")

  # Exit events

  # Utils
  async def print_players(self) -> None:
    msg: UniMessage = UniMessage.text("【阿瓦隆房间玩家列表】")
    for pl in self.players:
      msg.text("\n").at(pl)
    await msg.send(Target(self.guild_id, self_id=self.bot_id))
