from . import matchers as _

from nonebot.plugin import PluginMetadata, inherit_supported_adapters


# Plugin meta
__plugin_meta__: PluginMetadata = PluginMetadata(
  name="阿瓦隆",
  description="阿瓦隆游戏插件，支持 5~10 人游玩",
  usage="发送 .awl 获取插件信息",
  type="application",
  homepage="https://github.com/SamuNatsu/nonebot-plugin-avalon",
  supported_adapters=inherit_supported_adapters(
    "nonebot_plugin_alconna",
    "nonebot_plugin_apscheduler",
    "nonebot_plugin_session",
    "nonebot_plugin_userinfo"
  ),
)
