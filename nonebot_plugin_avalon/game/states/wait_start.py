from . import StateEnum
from ..game import Game
from ..state import State

from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")
require("nonebot_plugin_userinfo")

from nonebot_plugin_alconna import (
  Alconna, AlconnaMatches, Args, Arparma, At, UniMessage, on_alconna
)
from nonebot_plugin_session import EventSession, SessionLevel
from nonebot_plugin_userinfo import UserInfo, EventUserInfo


# On enter
async def enter(self: Game, _: StateEnum) -> None:
  await (
    UniMessage
      .text(f"📣本群组阿瓦隆房间已由房主 [{self.players[self.host_id].name}] 开启\n")
      .text("⚠️请玩家添加机器人好友以保证游戏正常进行\n")
      .text("[.awl加入] 加入房间\n")
      .text("[.awl退出] 退出房间\n")
      .text("[.awl踢人 @某人] 踢出房间（仅房主）\n")
      .text("[.awl开始] 开始游戏（仅房主）\n")
      .text("[.awl玩家] 查看房间玩家列表\n")
      .text("[.awl结束] 强制结束游戏（仅房主）")
      .send(self.guild_target)
    )

  # State-scope matcher handlers
  async def handle_join(
    session: EventSession,
    user_info: UserInfo = EventUserInfo()
  ) -> None:
    # Group msg & Is room
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id
    ):
      await self.on_msg(type="join", user_info=user_info)

  async def handle_leave(
    session: EventSession,
    user_info: UserInfo = EventUserInfo()
  ) -> None:
    # Group msg & Is room
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id
    ):
      await self.on_msg(type="leave", user_info=user_info)

  async def handle_kick(
    session: EventSession,
    result: Arparma = AlconnaMatches()
  ) -> None:
    # Group msg & Is room & Is host
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 == self.host_id
    ):
      await self.on_msg(
        type="kick",
        user_info=UserInfo(
          user_id=result.main_args["target"].target,
          user_name=""
        )
      )

  async def handle_start(
    session: EventSession,
    user_info: UserInfo = EventUserInfo()
  ) -> None:
    # Group msg & Is room & Is host
    if (
      session.level == SessionLevel.GROUP and
      session.id2 == self.guild_target.id and
      session.id1 == self.host_id
    ):
      await self.on_msg(type="start", user_info=user_info)

  # Create matchers
  self.matchers["join"] = on_alconna(".awl加入", handlers=[handle_join])
  self.matchers["leave"] = on_alconna(".awl退出", handlers=[handle_leave])
  self.matchers["kick"] = on_alconna(
    Alconna(".awl踢人", Args["target", At]),
    handlers=[handle_kick]
  )
  self.matchers["start"] = on_alconna(".awl开始", handlers=[handle_start])

# On message
async def msg(self: Game, type: str, user_info: UserInfo) -> None:
  pl: Game.Player = Game.Player(user_info)

  if type == "join":
    if pl.user_id in self.players:
      await UniMessage.text("⚠️你已经在该房间中了").send(reply_to=True)
    else:
      self.players[pl.user_id] = pl
      await (
        UniMessage
          .text(f"📣玩家 [{pl.name}] 加入了房间\n")
          .text(f"📊房间人数：{len(self.players)}人")
          .send(reply_to=True)
      )

  elif type == "leave":
    if pl.user_id in self.players:
      if pl.user_id == self.host_id:
        await (
          UniMessage
            .text("⚠️房主不能离开房间，若想离开请使用 [.awl结束] 强制结束游戏，然后让其他人重开房间")
            .send(reply_to=True)
        )
      else:
        await (
          UniMessage
            .text(f"📣玩家 [{pl.name}] 离开了房间\n")
            .text(f"📊房间人数：{len(self.players)}人")
            .send(reply_to=True)
        )
        self.players.pop(pl.user_id)
    else:
      await (
        UniMessage
          .text("⚠️你不在该房间中")
          .send(reply_to=True)
      )

  elif type == "kick":
    if pl.user_id in self.players:
      if pl.user_id == self.host_id:
        await (
          UniMessage
            .text("⚠️房主不能将自己踢出房间，若想离开请使用 [.awl结束] 强制结束游戏，然后让其他人重开房间")
            .send(reply_to=True)
        )
      else:
        self.players.pop(pl.user_id)
        await (
          UniMessage
            .text("📣玩家 [").at(pl.user_id).text("] 被踢出房间\n")
            .text(f"📊房间人数：{len(self.players)}人")
            .send(reply_to=True)
        )
    else:
      await (
        UniMessage
          .text("⚠️该玩家不在房间中")
          .send(reply_to=True)
      )

  elif type == "start":
    if len(self.players) < 5 or len(self.players) > 10:
      await (
        UniMessage
          .text("⚠️游戏人数不满足5~10人，不能开始游戏\n")
          .text(f"📊房间人数：{len(self.players)}人")
          .send(reply_to=True)
      )
    else:
      await self.to_state(StateEnum.INITIALIZE)

# On exit
async def exit(self: Game, _: StateEnum) -> None:
  self.remove_matchers("join", "leave", "kick", "start")

# Register state
Game.register_state(
  State(StateEnum.WAIT_START, initial=True, enter=enter, msg=msg, exit=exit)
)
