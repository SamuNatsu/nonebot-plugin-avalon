import nonebot

from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()

app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(Adapter)

try:
  nonebot.load_plugin("nonebot_plugin_avalon")
except Exception:
  pass

if __name__ == "__main__":
  nonebot.run(app="test:app")
