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

require("nonebot_plugin_session")
from nonebot_plugin_session import EventSession

require("nonebot_plugin_userinfo")
from nonebot_plugin_userinfo import UserInfo


# Player class
class Player:
  id: str
  name: str
  role: RoleEnum | None

  def __init__(self, user_info: UserInfo) -> None:
    self.id = user_info.user_id
    self.name = (
      user_info.user_remark or user_info.user_displayname or user_info.user_name
    )
    self.role = None

# Game state enum
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

# Game state machine
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
  guild_id: str
  host_id: str
  players: dict[str, Player]
  players_order: list[str]
  leader: str

  # Constructor
  def __init__(self, session: EventSession, host_info: UserInfo) -> None:
    super().__init__()

    self.bot_id = session.bot_id
    self.guild_id = session.id2
    self.host_id = host_info.user_id
    self.players = { host_info.user_id: Player(host_info) }
    self.players_order = []
    self.leader = ""

    scheduler.add_job(
      self.to_state,
      args=[Game.s_force_end],
      kwargs={ "reason": "游戏超时" },
      id=self.guild_id,
      trigger="date",
      run_date=datetime.now(UTC) + timedelta(hours=2)
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

    for pl in self.players.values():
      self.players_order.append(pl.id)

      role: RoleEnum = roles.pop()
      pl.role = role

      if role in { RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.OBERON, RoleEnum.LACHEY }:
        merlin_info.append(pl.id)
      if role in { RoleEnum.MERLIN, RoleEnum.MORGANA }:
        percival_info.append(pl.id)
      if role in { RoleEnum.MORDRED, RoleEnum.MORGANA, RoleEnum.ASSASSIN, RoleEnum.LACHEY }:
        evil_info[pl.id] = role

    random.shuffle(self.players_order)
    random.shuffle(merlin_info)
    random.shuffle(percival_info)
    self.leader = self.players_order[0]

    await self.print_player_order()

    for pl in self.players.values():
      await (
        UniMessage
          .text(f"💡你的身份是：{ROLE_NAME[pl.role]}")
          .send(Target(pl.id, private=True, self_id=self.bot_id))
      )

      if pl.role == RoleEnum.MERLIN:
        await (
          UniMessage
            .text("📃邪恶方名单：\n")
            .text(
              "\n".join([f"{self.players[i].name}({i})" for i in merlin_info])
            )
            .send(Target(pl.id, private=True, self_id=self.bot_id))
        )
      elif pl.role == RoleEnum.PERCIVAL:
        await (
          UniMessage
            .text("📃TA们可能是梅林：\n")
            .text(
              "\n".join([f"{self.players[i].name}({i})" for i in percival_info])
            )
            .send(Target(pl.id, private=True, self_id=self.bot_id))
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
        )

    # TODO
    await (
      UniMessage
        .text("📣TBC...")
        .send(Target(self.guild_id, self_id=self.bot_id))
    )
    await self.to_state(Game.s_force_end, reason="感谢参与测试")

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
  async def m_wait_start(self, type: str, user_info: UserInfo) -> None:
    pl: Player = Player(user_info)

    if type == "join" and pl.id not in self.players:
      self.players[pl.id] = pl
      await (
        UniMessage
          .text(f"📣玩家 [{pl.name}] 加入了房间\n")
          .text(f"💡房间人数：{len(self.players)}")
          .send()
      )

    elif type == "leave" and pl.id in self.players:
      self.players.pop(pl.id)
      await (
        UniMessage
          .text(f"📣玩家 [{pl.name}] 离开了房间\n")
          .text(f"💡房间人数：{len(self.players)}")
          .send()
      )

    elif type == "kick" and pl.id in self.players:
      self.players.pop(pl.id)
      await (
        UniMessage
          .text("📣玩家 [").at(pl.id).text("] 被踢出房间\n")
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
    msg: UniMessage = UniMessage.text(f"🎮当前玩家列表：{len(self.players)}人")
    for pl in self.players.values():
      msg.text(f"\n{pl.name}")

    await msg.send(Target(self.guild_id, self_id=self.bot_id))

  async def print_player_order(self) -> None:
    msg: UniMessage = UniMessage.text("▶️当前玩家顺位：")
    for plid in self.players_order:
      msg.text(f"\n{self.players[plid].name}")
    msg.text(f"\n\n👑当前队长：{self.players[self.leader].name}")

    await msg.send(Target(self.guild_id, self_id=self.bot_id))
