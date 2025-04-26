from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot import require, on_command
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import on_alconna, Alconna, Args, Option, CommandMeta, Arparma
scheduler = require("nonebot_plugin_apscheduler").scheduler
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.exception import FinishedException
from typing import Dict, Any, List, Tuple
import re,time,random



from .utils import (
    MaidleGame, 
    PopularityManager,
    get_session_id, 
    get_random_emoji, 
    get_mood_emoji, 
    get_difficulty_emoji
)

popularity_manager = PopularityManager()

class GameInstance:
    def __init__(self, game: MaidleGame):
        self.game = game
        self.last_activity = time.time()
    
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = time.time()
    
    def is_inactive(self, timeout_seconds: int = 600) -> bool:
        """检查游戏是否超过指定时间未活动"""
        return time.time() - self.last_activity > timeout_seconds



game_instances: Dict[str, GameInstance] = {}

guess_cmd = on_alconna(
    Alconna(
        "猜测",
        Args["keyword?", str],
        meta=CommandMeta(
            description="提交猜测",
            usage="发送 猜 [歌曲ID]",
            example="猜 655"
        ),
        separators=[' ', '']
    ),
    aliases={"guess", "选", "猜"},
    use_cmd_sep=False,
    skip_for_unmatch=False,
    priority=2,
    block=True
)

maidle_cmd = on_alconna(
    Alconna(
        "maidle",
        Args["difficulty?", str],
        Option("帮助", help_text="查看帮助信息"),
        Option("状态", help_text="查看当前游戏状态"),
        meta=CommandMeta(
            description="舞萌猜歌游戏",
            usage="发送 猜歌 开始游戏",
            example="猜歌 13+"
        )
    ),
    aliases={"猜歌", "猜曲", "maimai猜歌"},
    priority=1,
    block=True
)

quit_cmd = on_alconna(
    Alconna(
        "结束猜歌",
        meta=CommandMeta(
            description="结束当前猜歌游戏",
            usage="发送 结束猜歌",
            example="结束猜歌"
        )
    ),
    aliases={"退出猜歌", "结束游戏"},
    priority=4
)


def get_game_instance(session_id: str) -> MaidleGame:
    """获取或创建会话的游戏实例"""
    if session_id not in game_instances:
        logger.info(f"为会话 {session_id} 创建新的游戏实例")
        game = MaidleGame()
        if not game.load_game_data():
            logger.error(f"会话 {session_id} 的游戏数据加载失败")
            raise ValueError("游戏数据加载失败，请检查日志")
        game_instances[session_id] = GameInstance(game)
        
    else:
        game_instances[session_id].update_activity()
    
    return game_instances[session_id].game

def update_game_activity(session_id: str) -> None:
    """更新会话游戏实例的最后活动时间"""
    if session_id in game_instances:
        game_instances[session_id].update_activity()
        logger.debug(f"更新会话 {session_id} 的游戏活动时间")

@scheduler.scheduled_job("interval", minutes=5)
async def clean_inactive_games():
    """每5分钟运行一次，清理超过10分钟未活动的游戏实例"""
    try:
        logger.info("开始检查并清理不活跃的游戏实例")
        to_remove = []
        for session_id, instance in game_instances.items():
            if instance.is_inactive(600):
                to_remove.append(session_id)
                logger.info(f"会话 {session_id} 的游戏超过10分钟未活动，将被清理")
        for session_id in to_remove:
            try:
                game = game_instances[session_id].game
                if game.is_playing:
                    logger.info(f"会话 {session_id} 的游戏超时结束，正确答案是: {game.target_music.get('id', '未知')}:{game.target_music.get('title', '未知')}")
                del game_instances[session_id]
                logger.info(f"已清理会话 {session_id} 的游戏实例")
            except Exception as e:
                logger.error(f"清理会话 {session_id} 的游戏实例时出错: {str(e)}")
        if to_remove:
            logger.info(f"本次清理了 {len(to_remove)} 个不活跃的游戏实例")
        else:
            logger.info("没有需要清理的游戏实例")
            
    except Exception as e:
        logger.error(f"游戏实例清理任务出错: {str(e)}")

def format_hints(hints: List[Dict[str, Any]]) -> str:
    """将提示信息格式化为字符串"""
    formatted = "===== 提示 =====\n"
    for hint in hints:
        if "text" in hint and isinstance(hint["text"], str):
            hint["text"] = hint["text"].replace("SD", "标准谱")
            hint["text"] = hint["text"].replace("sd", "标准谱")
        if hint["correct"]:
            prefix = f"{get_mood_emoji(is_correct=True)} "
        elif hint.get("same_level", False):
            prefix = f"{get_mood_emoji(is_close=True)} "
        else:
            prefix = f"{get_mood_emoji()} "
        
        formatted += f"{prefix}{hint['text']}\n"
    formatted += "================"
    return formatted

def get_session_info(event: Event) -> Tuple[str, str, bool]:
    """
    获取会话信息
    """
    is_group, session_id = get_session_id(event)
    user_id = event.get_user_id()
    return session_id, user_id, is_group

def format_activity_time(session_id: str) -> str:
    """格式化会话游戏实例的最后活动时间"""
    if session_id in game_instances:
        last_activity = game_instances[session_id].last_activity
        time_diff = int(time.time() - last_activity)
        
        if time_diff < 60:
            return f"{time_diff}秒前"
        elif time_diff < 3600:
            return f"{time_diff // 60}分钟前"
        else:
            return f"{time_diff // 3600}小时{(time_diff % 3600) // 60}分钟前"
    return "未知"

@maidle_cmd.handle()
async def handle_maidle(event: Event, matcher: Matcher, args: Arparma):
    session_id, user_id, is_group = get_session_info(event)
    logger.debug(f"{args.options}")
    if "状态" in args.options:
        try:
            game = get_game_instance(session_id)
            status = game.get_game_status()
            
            if not status["is_playing"]:
                await matcher.finish(UniMessage(f"{get_random_emoji()} 当前没有进行中的游戏。发送 猜歌 [难度] 来开始游戏。"))
            
            last_activity = format_activity_time(session_id)
            
            status_msg = (
                f"\n{get_random_emoji()} 【舞萌猜歌】当前状态 {get_random_emoji()}\n"
                f"难度: {status['difficulty']} {get_difficulty_emoji(status['difficulty'])}\n"
                f"已猜测次数: {status['guesses_count']}/10\n"
                f"参与人数: {status['players_count']} 👥\n"
                f"剩余机会: {status['remaining_chances']} ⏳\n"
                f"最后活动: {last_activity}\n"
            )
            
            if status["guesses_count"] > 0:
                status_msg += "\n已猜测歌曲:\n"
                for i, song in enumerate(status["guessed_songs"]):
                    status_msg += f"{i+1}. {song}\n"
            
            await matcher.finish(UniMessage(status_msg))
        except FinishedException:
            await matcher.finish()
        except Exception as e:
            logger.exception(f"获取游戏状态时出错: {str(e)}")
            await matcher.finish(UniMessage(f"获取游戏状态时出错: {str(e)}"))
    if "帮助" in args.options:
        help_text = (
            f"\n{get_random_emoji()} 【舞萌猜歌游戏】 {get_random_emoji()}\n"
            "玩法说明：系统会随机选择一首舞萌DX中的歌曲，群里所有人需要通过不断猜测来找出这首歌。\n"
            "每次猜测后，系统会给出提示，帮助你缩小范围。你们共有10次机会猜出正确答案。\n\n"
            "命令列表：\n"
            "- 猜歌 [难度]：开始游戏，可选难度有 unlimited(无限制)、13、13+、14、14+\n"
            "- 猜歌 状态：查看当前游戏状态\n"
            "- 猜 [歌曲ID或歌名]：提交猜测\n"
            "- 结束猜歌：结束当前游戏\n\n"
            "※ 游戏将在10分钟无活动后自动结束"
        )
        await matcher.finish(UniMessage(help_text))
    
    try:
        game = get_game_instance(session_id)
        if game.is_playing:
            await matcher.finish(UniMessage(f"{get_mood_emoji()} 当前群组已经有一个猜歌游戏在进行中！\n使用 搜索 [关键词] 来搜索曲目\n使用 猜 [歌曲ID] 来提交猜测\n使用 结束猜歌 来结束当前游戏"))
        difficulty = args.query("difficulty")
        if difficulty is None:
            difficulty = "无限制"
        else:
            difficulty = difficulty.lower()
        valid_difficulties = ["unlimited", "13", "13+", "14", "14+","无限制"]
        if difficulty not in valid_difficulties:
            await matcher.finish(UniMessage(f"{get_mood_emoji()} 无效的难度参数！可选值：{', '.join(valid_difficulties)}"))
        if game.start_game(difficulty):
            game.add_player(user_id)
            update_game_activity(session_id)
            session_type = "本群" if is_group else "私聊"
            difficulty_emoji = get_difficulty_emoji(difficulty)
            target_music = game.target_music
            random_tips = []
            # 1个提示: 80%, 2个提示: 15%, 3个提示: 5%
            tip_count = random.choices([1, 2, 3], weights=[75, 15, 5])[0]
            logger.debug(f"随机选择提供 {tip_count} 个提示")
            tip_types = [
                # (提示类型, 权重)
                #("genre", 30),        # 曲风
                #("artist", 25),       # 艺术家
                ("bpm", 5),          # BPM
                ("version", 25),      # 版本
                ("red_const", 10),    # 红谱定数
                ("purple_const", 10),  # 紫谱定数
                #("charter", 7),       # 谱师
                ("masbreak", 5)      # Break数
            ]
            
            # 随机选择不重复的提示类型
            selected_types = random.sample([t[0] for t in tip_types], k=min(tip_count, len(tip_types)))
            logger.debug(f"选择的提示类型: {selected_types}")
            
            if target_music:
                # 处理每种提示类型
                for tip_type in selected_types:
                    tip_text = ""
                    
                    if tip_type == "genre" and "genre" in target_music:
                        genre = target_music["genre"]
                        tip_text = f"🔍 提示：该曲目所属曲风为「{genre}」"
                    
                    elif tip_type == "artist" and "artist" in target_music:
                        artist = target_music["artist"]
                        tip_text = f"🔍 提示：该曲目艺术家为「{artist}」"
                    
                    elif tip_type == "bpm" and "bpm" in target_music and target_music["bpm"]:
                        bpm = target_music["bpm"]
                        tip_text = f"🔍 提示：该曲目BPM为 {bpm}"
                    
                    elif tip_type == "version" and "version" in target_music:
                        version = target_music["version"]
                        tip_text = f"🔍 提示：该曲目来自「{version}」版本"
                    
                    elif tip_type == "red_const" and "ds" in target_music and len(target_music["ds"]) >= 3:
                        red_const = target_music["ds"][2]
                        tip_text = f"🔍 提示：该曲目红谱定数为 {red_const}"
                    
                    elif tip_type == "purple_const" and "ds" in target_music and len(target_music["ds"]) >= 4:
                        purple_const = target_music["ds"][3]
                        tip_text = f"🔍 提示：该曲目紫谱定数为 {purple_const}"
                    
                    elif tip_type == "charter" and "mascharter" in target_music and target_music["mascharter"]:
                        charter = target_music["mascharter"]
                        tip_text = f"🔍 提示：该曲目Master谱面的谱师为「{charter}」"
                    
                    elif tip_type == "masbreak" and "masbreak" in target_music:
                        masbreak = target_music["masbreak"]
                        tip_text = f"🔍 提示：该曲目Master谱面的Break数为 {masbreak}"
                    if tip_text:
                        random_tips.append(tip_text)
            start_msg = (
                f"\n{get_random_emoji()} 【舞萌猜歌】游戏开始！ {get_random_emoji()}\n"
                f"难度：{difficulty} {difficulty_emoji}\n"
                f"{session_type}所有人共有10次机会猜出正确的曲目。\n"
                f"使用 猜 [歌曲ID或歌名] 来提交猜测。\n"
            )
            if random_tips:
                for tip in random_tips:
                    start_msg += f"{tip}\n"
            start_msg += (
                f"游戏将在10分钟无活动后自动结束。\n"
                f"祝你好运！ 🍀"
            )
            await matcher.finish(UniMessage(start_msg))
        else:
            await matcher.finish(UniMessage(f"{get_mood_emoji()} 游戏启动失败！可能没有符合难度 {difficulty} 的曲目。"))
    except FinishedException:
            pass
    except Exception as e:
        logger.exception(f"启动猜歌游戏时出错: {str(e)}")
        await matcher.finish(UniMessage(f"启动游戏时出错: {str(e)}"))

@guess_cmd.handle()
async def handle_guess(event: Event, matcher: Matcher, args: Arparma):
    session_id, user_id, is_group = get_session_info(event)
    raw_text = event.get_plaintext().strip()
    guess_text = None
    for prefix in ["猜", "guess", "选", "猜测"]:
        if raw_text.startswith(prefix) and len(raw_text) > len(prefix):
            guess_text = raw_text[len(prefix):].strip()
            logger.debug(f"检测到无空格猜测: {raw_text} -> {guess_text}")
            break
    if guess_text is None:
        guess_text = args.query("keyword")
        if guess_text:
            if re.match(r'^\d+$', guess_text) or re.match(r'^[a-zA-Z0-9]+$', guess_text):
                logger.debug(f"检测到ID猜测: {guess_text}")
            else:
                logger.debug(f"检测到别名猜测: {guess_text}")
        else:
            logger.debug("猜测内容为空")
    if not guess_text:
        await matcher.finish(UniMessage(f"{get_mood_emoji()} 请提供歌曲ID或歌曲名称！"))
    try:
        game = get_game_instance(session_id)
        if not game.is_playing:
            await matcher.finish(UniMessage(f"{get_mood_emoji()} 当前没有进行中的猜歌游戏！发送 猜歌 来开始游戏。"))
        if re.match(r'^\d+$', guess_text) or re.match(r'^[a-zA-Z0-9]+$', guess_text):
            logger.debug(f"直接使用ID猜测: {guess_text}")
            result = game.submit_guess(guess_text, user_id)
        else:
            logger.debug(f"尝试搜索匹配歌曲名称: {guess_text}")
            matches = game.search_matches(guess_text)
            if not matches:
                await matcher.finish(UniMessage(f"{get_mood_emoji()} 未找到与 '{guess_text}' 匹配的歌曲，请尝试使用更准确的名称或歌曲ID。"))
            else:
                sorted_matches = await popularity_manager.sort_matches_by_popularity(matches)
                best_match = sorted_matches[0]
                match_id = best_match["id"]
                match_title = best_match["title"]
                popularity = best_match.get("popularity", 0)
                target_id = game.target_music.get("id") if game.target_music else None
                has_correct = False
                correct_rank = -1
                for idx, match in enumerate(sorted_matches):
                    if match["id"] == target_id:
                        has_correct = True
                        correct_rank = idx + 1
                        break
                
                additional_info = ""
                if has_correct and correct_rank > 1:
                    if correct_rank <= 5:
                        additional_info += f"\n💡 提示：您的搜索结果中包含正确答案，但不是排名第一的结果。"
                    else:
                        additional_info += f"\n💡 提示：正确答案可能在您的搜索结果中，请尝试更精确的关键词。"
                logger.debug(f"使用热度最高的匹配项进行猜测: {match_id} ({match_title}) - 热度: {popularity}")
                if len(matches) == 1:
                    result = game.submit_guess(match_id, user_id)
                else:
                    result = game.submit_guess(match_id, user_id)
                    if result["success"]:
                        #popularity_text = f"(热度: {popularity})" if popularity > 0 else ""
                        result["message"] = f"\n使用'{match_title}'进行猜测。\n" + result["message"] + f"{additional_info}"
        if not result["success"]:
            await matcher.finish(UniMessage(f"{get_mood_emoji()} {result['message']}"))
        update_game_activity(session_id)
        hints_text = format_hints(result["hints"])
        response_msg = f"{result['message']}\n{hints_text}"
        if result.get("game_over", False):
            if result.get("win", False):
                players = result.get("players", [])
                players_count = len(players)
                response_msg += f"\n\n{get_mood_emoji(is_correct=True)} 恭喜你 赢得了游戏！{get_mood_emoji(is_correct=True)}"
                response_msg += f"\n本局游戏共有 {players_count} 名玩家参与 👥"
            else:
                response_msg += f"\n\n{get_mood_emoji()} 游戏结束，已用完所有猜测机会。祝下次好运！"
            if session_id in game_instances:
                del game_instances[session_id]
        else:
            remaining = 10 - len(game.guesses)
            response_msg += f"\n\n⏳ 还剩 {remaining} 次猜测机会"
        response = UniMessage(response_msg)
        if is_group:
            response = response.at(user_id)
        await matcher.finish(response)
    except FinishedException:
        pass
    except Exception as e:
        logger.exception(f"提交猜测时出错: {str(e)}")
        await matcher.finish(UniMessage(f"猜测出错: {str(e)}"))

@quit_cmd.handle()
async def handle_quit(event: Event, matcher: Matcher):
    session_id, user_id, is_group = get_session_info(event)
    
    try:
        if session_id not in game_instances:
            await matcher.finish(UniMessage(f"{get_mood_emoji()} 当前没有进行中的猜歌游戏！"))
        game = game_instances[session_id].game
        result = game.quit_game(user_id)
        if not result["success"]:
            await matcher.finish(UniMessage(f"{get_mood_emoji()} {result['message']}"))
        players = result.get("players", [])
        players_count = len(players)
        end_msg = f"{get_random_emoji()} {result['message']}\n"
        end_msg += f"本局游戏共有 {players_count} 名玩家参与 👥"
        del game_instances[session_id]
        await matcher.finish(UniMessage(end_msg))
    except FinishedException:
            pass
    except Exception as e:
        logger.exception(f"结束游戏时出错: {str(e)}")
        await matcher.finish(UniMessage(f"结束游戏出错: {str(e)}"))