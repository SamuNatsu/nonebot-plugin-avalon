import copy
import random

from .role import ROLE_NAME, ROLE_SET, ROLE_SET_NAME, RoleEnum
from .state_machine import State, StateMachine

from datetime import UTC, datetime, timedelta
from enum import Enum, auto, unique
from nonebot import require
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
  s_initialize: State   = State(id=StateEnum.INITIALIZE, enter="e_initialize")
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
  player_order: list[str]
  player_role: dict[str, RoleEnum]
  leader: str

  # Constructor
  def __init__(self, bot_id: str, host_id: str, guild_id: str) -> None:
    super().__init__()

    self.bot_id = bot_id
    self.host_id = host_id
    self.guild_id = guild_id
    self.players = { host_id }
    self.player_order = []
    self.player_role = {}
    self.leader = ""

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
    await (
      UniMessage
        .text("📣本群组阿瓦隆房间已由房主 [").at(self.host_id).text("] 开启\n")
        .text("⚠️为了保证游戏的正常工作，请玩家添加本机器人为好友\n")
        .text("""[.awl加入] 加入房间
[.awl退出] 退出房间
[.awl玩家] 查看房间玩家列表
[.awl踢人 <@某人>] 踢出房间（仅房主）
[.awl开始] 开始游戏（仅房主）
[.awl结束] 强制结束游戏（仅房主）""")
        .send(Target(self.guild_id, self_id=self.bot_id))
      )

  async def e_initialize(self, last_state: str | None) -> None:
    await (
      UniMessage
        .text(f"📣阿瓦隆{len(self.players)}人局开始\n\n")
        .text(ROLE_SET_NAME[len(self.players)])
        .send(Target(self.guild_id, self_id=self.bot_id))
    )

    roles: list[RoleEnum] = copy.deepcopy(ROLE_SET[len(self.players)])
    random.shuffle(roles)

    merlin_info: list[str] = []
    percival_info: list[str] = []
    evil_info: dict[str, RoleEnum] = {}

    for pl in self.players:
      self.player_order.append(pl)

      role: RoleEnum = roles.pop()
      self.player_role[pl] = role
      if role in { RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.OBERON, RoleEnum.LACHEY }:
        merlin_info.append(pl)
      if role in { RoleEnum.MERLIN, RoleEnum.MORGANA }:
        percival_info.append(pl)
      if role in { RoleEnum.MORDRED, RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.LACHEY }:
        evil_info[pl] = role

    random.shuffle(self.player_order)
    random.shuffle(merlin_info)
    random.shuffle(percival_info)
    self.leader = self.player_order[0]

    await self.print_player_order()

    for pl, role in self.player_role.items():
      await (
        UniMessage
          .text(f"💡你的身份是：{ROLE_NAME[role]}")
          .send(Target(pl, private=True, self_id=self.bot_id))
      )

      if role == RoleEnum.MERLIN:
        pass
      elif role == RoleEnum.PERCIVAL:
        pass
      elif role in { RoleEnum.MORDRED, RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.LACHEY }:
        pass

  async def e_force_end(self, last_state: str | None, reason: str) -> None:
    if scheduler.get_job(self.guild_id) != None:
      scheduler.remove_job(self.guild_id)
    Game.instances.pop(self.guild_id)

    await (
      UniMessage
        .text("❌游戏强制结束\n")
        .text(f"⚠️理由：{reason}")
        .send(Target(self.guild_id, self_id=self.bot_id))
    )

  # Message events
  async def m_wait_start(self, type: str, user_id: str) -> None:
    if type == "join" and user_id not in self.players:
      self.players.add(user_id)
      await (
        UniMessage
          .text("📣玩家 [").at(user_id).text("] 加入了房间\n")
          .text(f"💡房间人数：{len(self.players)}")
          .send()
      )

    elif type == "leave" and user_id in self.players:
      self.players.remove(user_id)
      await (
        UniMessage
          .text("📣玩家 [").at(user_id).text("] 离开了房间\n")
          .text(f"💡房间人数：{len(self.players)}")
          .send()
      )

    elif type == "kick" and user_id in self.players:
      self.players.remove(user_id)
      await (
        UniMessage
          .text("📣玩家 [").at(user_id).text("] 被踢出房间\n")
          .text(f"💡房间人数：{len(self.players)}")
          .send()
      )

    else:
      if len(self.players) < 5 or len(self.players) > 10:
        await (
          UniMessage
            .text("⚠️游戏人数不满足5~10人，不能开始游戏\n")
            .text(f"💡房间人数：{len(self.players)}")
            .send()
        )
      else:
        await self.to_state(Game.s_initialize)

  # Exit events

  # Utils
  async def print_players(self) -> None:
    msg: UniMessage = UniMessage.text(f"【阿瓦隆玩家列表：{len(self.players)}人】")
    for pl in self.players:
      msg.text("\n").at(pl)

    await msg.send(Target(self.guild_id, self_id=self.bot_id))

  async def print_player_order(self) -> None:
    msg: UniMessage = UniMessage.text("▶️当前玩家顺位：")
    for pl in self.player_order:
      msg.text("\n").at(pl)
    msg.text("\n\n👑当前队长：").at(self.leader)

    await msg.send(Target(self.guild_id, self_id=self.bot_id))
