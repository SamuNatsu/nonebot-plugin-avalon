<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-avalon

_✨ 阿瓦隆游戏插件 ✨_

<a href="./LICENSE"><img src="https://img.shields.io/github/license/SamuNatsu/nonebot-plugin-avalon.svg" alt="license"></a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-avalon"><img src="https://img.shields.io/pypi/v/nonebot-plugin-avalon.svg" alt="pypi"></a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 介绍

插件实现了阿瓦隆基本版的所有功能

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-avalon

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-avalon

</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-avalon

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-avalon

</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-avalon

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-avalon"]

</details>

## ⚙️ 配置

该插件无需配置

## 🎉 使用

### 指令表

|     指令     |  权限  | 需要@ |   范围   |          说明          |
| :----------: | :----: | :---: | :------: | :--------------------: |
|    `.awl`    | 所有人 |  否   | 所有聊天 |      打开插件帮助      |
|  `.awl玩法`  | 所有人 |  否   | 所有聊天 | 查看阿瓦隆在线玩法信息 |
|  `.awl角色`  | 所有人 |  否   | 所有聊天 | 查看阿瓦隆游戏角色信息 |
| `.awl新游戏` | 所有人 |  否   |   群聊   |  在当前群组中开启游戏  |

_更多命令会在游戏过程中介绍和出现_
