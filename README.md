<!-- markdownlint-disable MD033 -->

<div align="center">

# 🌟 NoneBot Plugin Maidle 舞萌猜歌插件 🌟

</div>

<p align="center">
  <a href="https://github.com/huanxin996/nonebot_plugin_maidle"><img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_hx-yinying/main/.venv/hx_img.png" width="200" height="200" alt="maidle"></a>
</p>

<div align="center">

✨ **一个基于NoneBot2的舞萌DX猜歌游戏插件** ✨  
该项目基于[maidle](https://github.com/Dale2003/maidle)
支持在QQ群中进行maimaiDX猜歌游戏，提供丰富的提示信息和多样的难度选择。

</div>

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/huanxin996/nonebot_plugin_maidle?style=social)](https://github.com/huanxin996/nonebot_plugin_maidle)
[![GitHub issues](https://img.shields.io/github/issues/huanxin996/nonebot_plugin_maidle)](https://github.com/huanxin996/nonebot_plugin_maidle/issues)
[![GitHub license](https://img.shields.io/github/license/huanxin996/nonebot_plugin_maidle)](https://github.com/huanxin996/nonebot_plugin_maidle/blob/main/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/nonebot-plugin-maidle)](https://pypi.org/project/nonebot-plugin-maidle/)
[![Python version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Release](https://img.shields.io/github/v/release/huanxin996/nonebot_plugin_maidle?include_prereleases)](https://github.com/huanxin996/nonebot_plugin_maidle/releases)
[![Downloads](https://img.shields.io/pypi/dm/nonebot-plugin-maidle)](https://pypi.org/project/nonebot-plugin-maidle/)
[![NoneBot](https://img.shields.io/badge/NoneBot-2.0-brightgreen)](https://v2.nonebot.dev/)

</div>

---

## 安装📦

请注意，歌曲的曲绘文件应该放在你的bot文件夹下的"Resource"/"static"/"mai"/"cover"内，示例：nonebot/Resource/static/mai/cover

同时命名应该为曲绘的ID，例如：12231.png

### 方式一：通过 pip 安装

```bash
pip install nonebot-plugin-maidle
```

### 方式二：通过 NB-CLI 安装

```bash
nb plugin install nonebot-plugin-maidle
```

### 方式三：通过 Git 安装

```bash
git clone https://github.com/huanxin996/nonebot_plugin_maidle.git
cd nonebot_plugin_maidle
pip install .
```

然后确保将插件添加到NoneBot的加载项中。
"nonebot_plugin_maidle"

---

## 📋 功能特性

- 多难度级别：支持无限制、13、13+、14、14+难度
- 丰富提示信息：ID、曲目类型、标题、艺术家、流派、版本、BPM、定数等
- 曲目别名支持：可以通过曲目ID或别名进行搜索和猜测
- 计时自动结束：游戏10分钟无活动将自动结束
- 多人游戏支持：群内任何人都可以参与猜测，共享10次猜测机会

---

## 🚀 如何使用？

### 📜 命令列表

以下是插件支持的命令及其功能：

#### **猜歌游戏**

- **`猜歌 [难度]`**  
  开始一场新的猜歌游戏。  
  **参数**：  
  - `难度`（可选）：游戏难度，可选值：`无限制`(默认)、`13`、`13+`、`14`、`14+`。

- **`猜歌 状态`**  
  查看当前游戏状态，包括难度、已猜次数、参与人数等信息。

- **`猜歌 帮助`**  
  显示游戏帮助信息。

#### **搜索与猜测**

- **`猜 [歌曲ID或别名或标题]`**  
  提交对曲目的猜测。  
  **参数**：  
  - `歌曲ID`（必需）：曲目ID或别名。  
  **别名**：`guess`、`选`、`猜测`

#### **游戏控制**

- **`结束猜歌`**  
  手动结束当前游戏并公布答案。  
  **别名**：`退出猜歌`、`结束游戏`、`quit`、`结束`

---

## 🎮 游戏规则

1. 群聊中任意成员发送「猜歌 [难度]」开始游戏
2. 系统会随机选择一首符合指定难度的舞萌DX曲目
3. 使用「猜 [歌曲ID或别名或标题]」提交猜测
4. 每次猜测后，系统会给出多种提示帮助缩小范围
5. 整个群共享10次猜测机会
6. 游戏成功或用完10次机会后结束
7. 10分钟无活动将自动结束游戏
8. 支持私聊中使用

---

## 🎵 示例提示信息

当你提交一次猜测后，系统会提供类似这样的提示：

```
===== 提示 =====
❌ ID: 855
✅ 类型: 原创
❌ 标题: GIGANTØMAKHIA
❌ 艺术家: Camellia
❌ 流派: 其他
❌ 版本: 早了 舞萌DX2022
❌ BPM: 低了 180
❌ 红谱定数: 低了 12.8
❌ 紫谱定数: 低了 14.2
❌ 紫谱谱师: MASAO.S
❌ 紫谱绝赞数量: 少了 2
================
```

表情符号含义：
- ✅ - 完全正确
- 🤔 - 接近正确（如同级别）
- ❌ - 不正确

---

## 🔗 相关链接

- [舞萌DX官方网站](https://maimai.sega.com/)
- [插件问题反馈](https://github.com/huanxin996/nonebot_plugin_maidle/issues)

## 📝 更新日志

### v0.0.1 (2025-04-25)

- 初始版本发布
- 支持基础猜歌功能和难度筛选
- 支持多平台（基于nonebot_plugin_alconna）
- 提供丰富的提示信息

## 🤝 贡献

欢迎提交 Pull Request 或 Issue！如有任何问题或建议，请提issue，我看到后会第一时间处理。

---

# 感谢 ✨

- [源网站](https://github.com/Dale2003/maidle)


<p align="center">✨ 感谢使用 NoneBot Plugin Maidle 插件！✨</p>

<!-- markdownlint-restore -->
