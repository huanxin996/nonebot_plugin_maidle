from nonebot.plugin import PluginMetadata,inherit_supported_adapters
from nonebot import require
require("nonebot_plugin_alconna")


__plugin_meta__ = PluginMetadata(
    name="舞萌猜歌",
    description="基于NoneBot2的舞萌猜歌插件，支持多平台",
    usage=(
        "功能介绍：\n"
        "- 猜歌"
        "技术支持：\n"
        "基于  nonebot-plugin-alconna来处理命令和消息发送\n"
        "感谢以上插件作者以及 NoneBot2"
    ),
    type="application",
    homepage="https://github.com/huanxin996/nonebot_plugin_maidle",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

from .commands import *