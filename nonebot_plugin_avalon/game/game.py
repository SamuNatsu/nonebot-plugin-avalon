import secrets

from .role import ROLE_SET_NAME, RoleEnum
from .round import ROUND_PROTECT, ROUND_SET
from .state_machine import StateMachine
from .states import StateEnum

from dataclasses import dataclass
from datetime import UTC, datetime
from nonebot import require
from typing import Self

require("nonebot_plugin_alconna")
require("nonebot_plugin_apscheduler")
require("nonebot_plugin_session")
require("nonebot_plugin_userinfo")

from nonebot_plugin_alconna import AlconnaMatcher, Target, UniMessage, on_alconna
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_session import EventSession, SessionLevel
from nonebot_plugin_userinfo import UserInfo


class Game(StateMachine):
  @dataclass
  class Player:
    user_id: str
    name: str
    role: RoleEnum | None = None

    def __init__(self, user_info: UserInfo) -> None:
      self.user_id = user_info.user_id
      self.name = (
        user_info.user_remark or
        user_info.user_displayname or
        user_info.user_name
      )

  # Class variables
  instances: dict[str, Self] = {}

  # Instance variables
  assassin_id: str
  build_tries: int
  create_time: datetime
  host_id: str
  key: str
  leader: str
  guild_target: Target
  matchers: dict[str, AlconnaMatcher]
  players: dict[str, Player]
  players_order: list[str]
  round: int
  round_states: list[bool | None]
  team: set[str]
  vote: dict[str, bool]

  # Instance methods
  def __init__(self, session: EventSession, user_info: UserInfo) -> None:
    super().__init__()

    self.assassin_id = ""
    self.build_tries = 1
    self.create_time = datetime.now(UTC)
    self.host_id = session.id1
    self.key = secrets.token_hex(3)
    self.leader = ""
    self.guild_target = Target(session.id2, self_id=session.bot_id)
    self.matchers = {}
    self.players = { session.id1: Game.Player(user_info) }
    self.players_order = []
    self.round = 0
    self.round_states = [None, None, None, None, None]
    self.team = set()
    self.vote = {}

    async def handle_players(session: EventSession) -> None:
      if (
        session.level == SessionLevel.GROUP and
        session.id2 == self.guild_target.id
      ):
        if self.is_state(StateEnum.WAIT_START):
          await self.print_players()
        else:
          await self.print_player_order()

    async def handle_exit(session: EventSession) -> None:
      if (
        session.level == SessionLevel.GROUP and
        session.id2 == self.guild_target.id and
        session.id1 == self.host_id
      ):
        await self.to_state(StateEnum.FORCE_END, reason="房主强制结束")

    self.matchers["players"] = on_alconna(".awl玩家", handlers=[handle_players])
    self.matchers["exit"] = on_alconna(".awl结束", handlers=[handle_exit])

  def clean_up(self) -> None:
    for i in self.matchers.values():
      i.destroy()
    self.matchers.clear()

    if scheduler.get_job(self.guild_target.id) != None:
      scheduler.remove_job(self.guild_target.id)

    Game.instances.pop(self.guild_target.id)

  # Exception handler
  async def exception_handler(self, e: Exception) -> None:
    await (
      UniMessage
        .text("❌插件运行时错误\n")
        .text(e)
        .send(self.guild_target)
    )
    await self.to_state(StateEnum.FORCE_END, reason="插件报错")

  # Utils methods
  def remove_matchers(self, *args) -> None:
    for i in args:
      if i in self.matchers:
        self.matchers[i].destroy()
        self.matchers.pop(i)

  async def print_players(self) -> None:
    msg: UniMessage = UniMessage.text(f"🎮玩家列表：{len(self.players)}人")
    for pl in self.players.values():
      msg.text(f"\n{pl.name}")
    await msg.send(self.guild_target)

  async def print_player_order(self) -> None:
    msg: UniMessage = (
      UniMessage
        .text(f"👑队长：{self.players[self.leader].name}\n")
        .text("🔃玩家顺位：")
    )
    for plid in self.players_order:
      msg.text(f"\n{self.players[plid].name}")
    await msg.send(self.guild_target)

  async def reply_status(self) -> None:
    await (
      UniMessage
        .text(f"🕒轮次：{self.round + 1}\n")
        .text(
          f"❓任务情况：{
            "".join(
              [
                "⬜" if i == None else "🟩" if i else "🟥"
                for i in self.round_states
              ]
            )
          }\n"
        )
        .text(f"⌛尝试组队次数：{self.build_tries}/5\n")
        .text(f"📊各任务要求人数：{"/".join(map(str, ROUND_SET[len(self.players)]))}\n")
        .text(f"🛡️保护轮：{ROUND_PROTECT[len(self.players)] or "无"}\n")
        .text(f"⚙️角色组成：\n{ROLE_SET_NAME[len(self.players)]}")
        .send(reply_to=True)
    )
