from . import StateEnum
from ..game import Game
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import (
  Alconna, AlconnaMatches, Args, Arparma, At, UniMessage, on_alconna
)

require("nonebot_plugin_session")
from nonebot_plugin_session import EventSession, SessionLevel

require("nonebot_plugin_userinfo")
from nonebot_plugin_userinfo import UserInfo, EventUserInfo


# On enter
async def enter(self: Game, _: StateEnum) -> None:
  await (
    UniMessage
      .text(f"📣本群组阿瓦隆房间已由房主 [{self.players[self.host_id].name}] 开启\n")
      .text("⚠️请玩家私信机器人加入房间，并保持临时会话活动\n")
      .text(f"""[.awl加入 {self.guild_target.id}] 加入房间（仅私信）
[.awl退出] 退出房间
[.awl玩家] 查看房间玩家列表
[.awl踢人 <@某人>] 踢出房间（仅房主）
[.awl开始] 开始游戏（仅房主）
[.awl结束] 强制结束游戏（仅房主）""")
      .send(self.guild_target)
    )

  async def handle_join(
    session: EventSession,
    user_info: UserInfo = EventUserInfo(),
    result: Arparma = AlconnaMatches()
  ) -> None:
    if (
      session.level == SessionLevel.PRIVATE and
      result.main_args["guild"] == self.guild_target.id
    ):
      await self.on_msg(type="join", user_info=user_info)

  async def handle_leave(
    session: EventSession,
    user_info: UserInfo = EventUserInfo()
  ) -> None:
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id
    ):
      await self.on_msg(type="leave", user_info=user_info)

  async def handle_kick(
    session: EventSession,
    result: Arparma = AlconnaMatches()
  ) -> None:
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 == self.host_id
    ):
      await self.on_msg(
        type="kick",
        user_info=UserInfo(user_id=result.main_args["target"].target, user_name="")
      )

  async def handle_start(
    session: EventSession,
    user_info: UserInfo = EventUserInfo()
  ) -> None:
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 == self.host_id
    ):
      await self.on_msg(type="start", user_info=user_info)

  self.matchers["join"] = on_alconna(
    Alconna(".awl加入", Args["guild", str]),
    handlers=[handle_join]
  )
  self.matchers["leave"] = on_alconna(".awl退出", handlers=[handle_leave])
  self.matchers["kick"] = on_alconna(
    Alconna(".awl踢人", Args["target", At]),
    handlers=[handle_kick]
  )
  self.matchers["start"] = on_alconna(".awl开始", handlers=[handle_start])

# On message
async def msg(self: Game, type: str, user_info: UserInfo) -> None:
  pl: Game.Player = Game.Player(user_info)

  if type == "join" and pl.user_id not in self.players:
    self.players[pl.user_id] = pl
    await (
      UniMessage
        .text("📣玩家 [").at(pl.user_id).text("] 加入了房间\n")
        .text(f"💡房间人数：{len(self.players)}人")
        .send(self.guild_target)
    )

  elif type == "leave" and pl.user_id in self.players:
    if pl.user_id == self.host_id:
      await (
        UniMessage
          .text("⚠️房主不能离开房间，若想离开请使用 [.awl结束] 强制结束游戏，然后让其他人重开房间")
          .send(self.guild_target)
      )
    else:
      self.players.pop(pl.user_id)
      await (
        UniMessage
          .text("📣玩家 [").at(pl.user_id).text("] 离开了房间\n")
          .text(f"💡房间人数：{len(self.players)}人")
          .send(self.guild_target)
      )

  elif type == "kick" and pl.user_id in self.players:
    if pl.user_id == self.host_id:
      await (
        UniMessage
          .text("⚠️房主不能将自己踢出房间，若想离开请使用 [.awl结束] 强制结束游戏，然后让其他人重开房间")
          .send(self.guild_target)
      )
    else:
      self.players.pop(pl.user_id)
      await (
        UniMessage
          .text("📣玩家 [").at(pl.user_id).text("] 被踢出房间\n")
          .text(f"💡房间人数：{len(self.players)}人")
          .send(self.guild_target)
      )

  else:
    if len(self.players) < 5 or len(self.players) > 10:
      await (
        UniMessage
          .text("⚠️游戏人数不满足5~10人，不能开始游戏\n")
          .text(f"💡房间人数：{len(self.players)}人")
          .send(self.guild_target)
      )
    else:
      await self.to_state(StateEnum.INITIALIZE)

# On exit
async def exit(self: Game, _: StateEnum) -> None:
  for i in ["join", "leave", "kick", "start"]:
    self.matchers[i].destroy()
    self.matchers.pop(i)

# Register state
Game.register_state(
  State(StateEnum.WAIT_START, initial=True, enter=enter, msg=msg, exit=exit)
)
