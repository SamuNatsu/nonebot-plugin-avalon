from ..game import Game
from ..role import ROLE_NAME, ROLE_HELP, RoleEnum

from importlib import metadata
from nonebot import require

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import AlconnaMatcher, UniMessage, on_alconna

require("nonebot_plugin_session")
from nonebot_plugin_session import EventSession


# Helper contents
INFO_TXT: str = f"""【阿瓦隆插件 v{metadata.version("nonebot-plugin-avalon")}】
[.awl] 查看本信息
[.awl简介] 查看游戏简介
[.awl角色] 查看游戏角色帮助
[.awl新游戏] 作为房主在当前群组开启新游戏

插件仓库；https://github.com/SamuNatsu/nonebot-plugin-avalon"""

INTRO_TXT: str = """【阿瓦隆游戏简介】
阿瓦隆是亚瑟王传奇中的圣地，正义与邪恶将围绕阿瓦隆展开斗争。
亚瑟王手下的圆桌骑士派西维尔需要率队完成三次艰巨的任务，然而在众多的人选中隐藏着邪恶的力量。
他需要挑选出绝对忠诚的伙伴，帮助他完成任务。

阿瓦隆是一款适合 5~10 人游玩的语言类社交游戏。
玩家需要分为正义方和邪恶方两个阵营共同完成 5 轮任务，并在任务中完成各自阵营的目标以获取胜利。

（游戏具体玩法请自行搜索学习）"""

ROLE_TXT: str = "【阿瓦隆角色帮助】\n" + "\n".join(
  map(lambda x: f"{ROLE_NAME[x]}：{ROLE_HELP[x]}", RoleEnum)
)

# Info
info: AlconnaMatcher = on_alconna(".awl")

@info.handle()
async def handle_info() -> None:
  await info.finish(INFO_TXT)

# Intro
intro: AlconnaMatcher = on_alconna(".awl简介")

@intro.handle()
async def handle_intro() -> None:
  await intro.finish(INTRO_TXT)

# Role
role: AlconnaMatcher = on_alconna(".awl角色")

@role.handle()
async def handle_role() -> None:
  await role.finish(ROLE_TXT)

# New game
new_game: AlconnaMatcher = on_alconna(".awl新游戏")

@new_game.handle()
async def handle_new_game(session: EventSession) -> None:
  if session.id2 in Game.instances:
    await UniMessage.text(
      "本群组有阿瓦隆游戏正在进行，请：\n1.等待游戏结束或\n2.让房主 "
    ).at(Game.instances[session.id2].host_id).text(
      " 执行命令 [.awl结束] 或\n3.等待游戏 2 小时自动强制结束"
    ).finish()

  g: Game = Game(session.bot_id, session.id1, session.id2)
  Game.instances[session.id2] = g

  await g.to_state(Game.s_wait_start)
