from ..game import Game

from arclet.alconna import Alconna, Args, Arparma
from nonebot import require

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import AlconnaMatcher, AlconnaMatches, At, on_alconna

require("nonebot_plugin_session")
from nonebot_plugin_session import EventSession

require("nonebot_plugin_userinfo")
from nonebot_plugin_userinfo import EventUserInfo, UserInfo


# Wait start
join: AlconnaMatcher = on_alconna(".awl加入")
leave: AlconnaMatcher = on_alconna(".awl退出")
players: AlconnaMatcher = on_alconna(".awl玩家")
kick: AlconnaMatcher = on_alconna(Alconna(".awl踢人", Args["target", At]))
start: AlconnaMatcher = on_alconna(".awl开始")
exit: AlconnaMatcher = on_alconna(".awl结束")

@join.handle()
async def handle_join(
  session: EventSession,
  user_info: UserInfo = EventUserInfo()
) -> None:
  if session.id2 not in Game.instances:
    return
  g: Game = Game.instances[session.id2]

  if not g.is_state(Game.s_wait_start):
    return

  await g.on_msg(type="join", user_info=user_info)

@leave.handle()
async def handle_leave(
  session: EventSession,
  user_info: UserInfo = EventUserInfo()
) -> None:
  if session.id2 not in Game.instances:
    return
  g: Game = Game.instances[session.id2]

  if not g.is_state(Game.s_wait_start):
    return

  await g.on_msg(type="leave", user_info=user_info)

@players.handle()
async def handle_players(session: EventSession) -> None:
  if session.id2 not in Game.instances:
    return
  g: Game = Game.instances[session.id2]

  await g.print_players()

@kick.handle()
async def handle_kick(
  session: EventSession,
  result: Arparma = AlconnaMatches()
) -> None:
  if session.id2 not in Game.instances:
    return
  g: Game = Game.instances[session.id2]

  if session.id1 != g.host_id or not g.is_state(Game.s_wait_start):
    return

  await g.on_msg(
    type="kick",
    user_info=UserInfo(user_id=result.args["target"].target, user_name="")
  )

@start.handle()
async def handle_start(
  session: EventSession,
  user_info: UserInfo = EventUserInfo()
) -> None:
  if session.id2 not in Game.instances:
    return
  g: Game = Game.instances[session.id2]

  if session.id1 != g.host_id or not g.is_state(Game.s_wait_start):
    return

  await g.on_msg(type="start", user_info=user_info)

@exit.handle()
async def handle_exit(session: EventSession) -> None:
  if session.id2 not in Game.instances:
    return
  g: Game = Game.instances[session.id2]

  if session.id1 != g.host_id:
    return

  await g.to_state(Game.s_force_end, reason="房主强制结束")
