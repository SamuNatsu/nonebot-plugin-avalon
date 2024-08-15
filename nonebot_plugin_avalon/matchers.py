from .game import Game
from .game.role import ROLE_NAME, ROLE_HELP, RoleEnum

from importlib import metadata
from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_session")
require("nonebot_plugin_userinfo")

from nonebot_plugin_alconna import AlconnaMatcher, UniMessage, on_alconna
from nonebot_plugin_session import EventSession,SessionLevel
from nonebot_plugin_userinfo import EventUserInfo, UserInfo


# Helper contents
INFO_TXT: str = f"""【阿瓦隆插件 v{metadata.version("nonebot-plugin-avalon")}】
[.awl] 查看本信息
[.awl玩法] 查看游戏玩法
[.awl角色] 查看游戏角色帮助
[.awl新游戏] 作为房主在当前群组开启新游戏

插件仓库：https://github.com/SamuNatsu/nonebot-plugin-avalon"""

INTRO_TXT: str = """【阿瓦隆游戏玩法】
视频教学：https://www.bilibili.com/video/BV1Ym4y1Q7Gq

文字教学：https://github.com/SamuNatsu/nonebot-plugin-avalon/blob/main/TUTORIAL.md"""

ROLE_TXT: str = "【阿瓦隆角色帮助】\n" + "\n".join(
  map(lambda x: f"{ROLE_NAME[x]}：{ROLE_HELP[x]}", RoleEnum)
)

# Info
async def handle_info() -> None:
  await info.finish(INFO_TXT)

info: AlconnaMatcher = on_alconna(".awl", handlers=[handle_info])

# Intro
async def handle_intro() -> None:
  await intro.finish(INTRO_TXT)

intro: AlconnaMatcher = on_alconna(".awl玩法", handlers=[handle_intro])

# Role
async def handle_role() -> None:
  await role.finish(ROLE_TXT)

role: AlconnaMatcher = on_alconna(".awl角色", handlers=[handle_role])

# New game
async def handle_new_game(
  session: EventSession,
  user_info: UserInfo = EventUserInfo()
) -> None:
  # Must in group
  if session.level != SessionLevel.GROUP:
    await UniMessage.text("⚠️请在群组中创建新游戏").finish(reply_to=True)

  # Already has instance
  if session.id2 in Game.instances:
    await (
      UniMessage
        .text("⚠️本群组有阿瓦隆游戏正在进行，请：\n")
        .text("1.等待游戏结束或\n")
        .text("2.让房主 [")
        .at(Game.instances[session.id2].host_id)
        .text("] 执行命令 [.awl结束] 或\n")
        .text("3.等待游戏 2 小时自动强制结束")
        .finish(reply_to=True)
    )

  # Create instance
  Game.instances[session.id2] = Game(session, user_info)
  await Game.instances[session.id2].startup()

new_game: AlconnaMatcher = on_alconna(".awl新游戏", handlers=[handle_new_game])
