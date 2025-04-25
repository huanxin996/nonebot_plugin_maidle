import random, os, json,random
from nonebot.adapters import Event
from nonebot.log import logger
from typing import Tuple, Dict, List, Any, Optional

def get_session_id(event: Event) -> Tuple[bool, str]:
    """
    获取会话ID，如果是群聊则返回群ID，私聊则返回用户ID
    返回: (是否群聊, 会话ID)
    """
    session_id = event.get_session_id()
    logger.debug(f"获取session_ID: {session_id}")
    
    if session_id.startswith("group"):
        # 群聊消息，返回群号作为游戏ID
        return True, session_id.split("_")[1]
    else:
        # 私聊消息，返回用户ID作为游戏ID
        return False, event.get_user_id()

class MaidleGame:
    def __init__(self):
        self.music_info = {}  # 存储音乐信息
        self.alias = {}       # 存储别名信息
        self.music_alias = {} # 存储音乐别名映射
        self.target_music = None  # 目标音乐
        self.is_playing = False
        self.guesses = []     # 记录猜测历史
        self.hints_list = []  # 记录提示历史
        self.guessed_ids = [] # 记录已猜过的ID
        self.players = set()  # 记录参与游戏的玩家
        self.difficulty = "unlimited"  # 当前游戏难度
        self.version_to_id = {
            "maimai": 1, "maimai PLUS": 2, "maimai GreeN": 3, "maimai GreeN PLUS": 4,
            "maimai ORANGE": 5, "maimai ORANGE PLUS": 6, "maimai PiNK": 7, "maimai PiNK PLUS": 8,
            "maimai MURASAKi": 9, "maimai MURASAKi PLUS": 10, "maimai MiLK": 11, "MiLK PLUS": 12,
            "maimai FiNALE": 13, "舞萌DX": 14, "舞萌DX2021": 15, "舞萌DX2022": 16,
            "舞萌DX2023": 17, "舞萌DX2024": 18
        }
        logger.info("MaidleGame实例已初始化")
        
    def load_game_data(self) -> bool:
        """加载游戏数据"""
        try:
            # 修正路径，使用相对于当前文件夹的static目录
            static_dir = os.path.join(os.path.dirname(__file__), "static")
            logger.debug(f"尝试从目录加载数据: {static_dir}")
            
            # 加载音乐信息
            music_info_path = os.path.join(static_dir, "music_info.json")
            logger.debug(f"加载音乐信息: {music_info_path}")
            with open(music_info_path, "r", encoding="utf-8") as f:
                self.music_info = json.load(f)
            logger.info(f"已加载音乐信息，共 {len(self.music_info)} 条记录")
            
            # 加载别名信息
            alias_path = os.path.join(static_dir, "alias.json")
            logger.debug(f"加载别名信息: {alias_path}")
            with open(alias_path, "r", encoding="utf-8") as f:
                self.alias = json.load(f)
            logger.info(f"已加载别名信息，共 {len(self.alias)} 条记录")
                
            # 加载音乐别名映射
            all_alias_path = os.path.join(static_dir, "all_alias.json")
            logger.debug(f"加载音乐别名映射: {all_alias_path}")
            with open(all_alias_path, "r", encoding="utf-8") as f:
                self.music_alias = json.load(f)
            logger.info(f"已加载音乐别名映射，共 {len(self.music_alias)} 条记录")
                
            logger.info("所有游戏数据加载完成")
            return True
        except Exception as e:
            error_msg = f"加载游戏数据失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False
    
    def add_player(self, user_id: str) -> None:
        """添加参与游戏的玩家"""
        self.players.add(user_id)
        logger.debug(f"玩家 {user_id} 加入游戏，当前玩家数: {len(self.players)}")
    
    def start_game(self, difficulty_range: str = "unlimited") -> bool:
        """开始游戏，根据难度选择目标音乐"""
        logger.info(f"开始游戏，难度范围: {difficulty_range}")
        if difficulty_range == "无限制":
            difficulty_range = "unlimited"
        if self.is_playing:
            logger.warning("游戏已在进行中，无法开始新游戏")
            return False
        self.difficulty = difficulty_range
        keys = []
        logger.debug("开始根据难度筛选歌曲")
        for key, music in self.music_info.items():
            if difficulty_range == "13" and music["masds"] >= 13 and music["masds"] < 13.7:
                keys.append(key)
            elif difficulty_range == "13+" and music["masds"] >= 13.7 and music["masds"] < 14:
                keys.append(key)
            elif difficulty_range == "14" and music["masds"] >= 14 and music["masds"] < 14.7:
                keys.append(key)
            elif difficulty_range == "14+" and music["masds"] >= 14.7:
                keys.append(key)
            elif difficulty_range == "unlimited":
                keys.append(key)
        
        logger.info(f"筛选结果: 符合难度 {difficulty_range} 的曲目数量为 {len(keys)}")
        
        if not keys:
            logger.warning(f"没有符合难度 {difficulty_range} 的曲目")
            return False
        random_index = random.randint(0, len(keys) - 1)
        target_id = keys[random_index]
        self.target_music = self.music_info[target_id]
        logger.info(f"已随机选择目标音乐: ID={target_id}, 标题={self.target_music['title']}")
        logger.debug(f"目标音乐完整信息: {self.target_music}")
        self.is_playing = True
        self.guesses = []
        self.hints_list = []
        self.guessed_ids = []
        self.players = set()  # 清空玩家列表
        logger.debug("游戏初始化完成，等待用户猜测")
        return True
    
    def search_matches(self, input_text: str) -> List[Dict[str, str]]:
        """搜索匹配的歌曲"""
        logger.debug(f"搜索匹配的歌曲，输入: '{input_text}'")
        if not input_text:
            logger.debug("搜索输入为空，返回空列表")
            return []
        input_text = input_text.strip().lower()
        matches = []
        logger.debug("开始搜索匹配")
        for key, music in self.music_info.items():
            # 检查ID、标题或别名是否匹配
            title_match = music["title"].lower().find(input_text) != -1
            id_match = key.lower().find(input_text) != -1
            alias_match = False
            if key in self.music_alias:
                alias_match = any(alias.lower().find(input_text) != -1 for alias in self.music_alias[key])
            if id_match or title_match or alias_match:
                matches.append({
                    "id": key,
                    "title": music["title"]
                })
                logger.debug(f"找到匹配: ID={key}, 标题={music['title']}")
        logger.info(f"搜索完成，共找到 {len(matches)} 个匹配结果")
        return matches
    
    def get_hint(self, target: Dict[str, Any], guess: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成猜测提示"""
        logger.info(f"生成提示，目标ID: {target['id']}，猜测ID: {guess['id']}")
        hints = []
        # ID提示
        #correct_id = target["id"] == guess["id"]
        #hints.append({"text": f"ID: {guess['id']}", "correct": correct_id})
        # 类型提示
        correct_type = target["type"] == guess["type"] 
        hints.append({"text": f"类型: {guess['type']}", "correct": correct_type})
        # 标题提示
        correct_title = target["title"] == guess["title"]
        hints.append({"text": f"标题: {guess['title']}", "correct": correct_title})
        # 艺术家提示
        correct_artist = target["artist"] == guess["artist"]
        hints.append({"text": f"艺术家: {guess['artist']}", "correct": correct_artist})
        # 流派提示
        correct_genre = target["genre"] == guess["genre"]
        hints.append({"text": f"流派: {guess['genre']}", "correct": correct_genre})
        # 版本提示
        correct_version = target["version"] == guess["version"]
        version_hint = f"版本: {guess['version']}"
        if not correct_version:
            target_version_id = self.version_to_id.get(target["version"], 0)
            guess_version_id = self.version_to_id.get(guess["version"], 0)
            
            if target_version_id > guess_version_id:
                version_hint = f"版本: 早了 {guess['version']}"
            else:
                version_hint = f"版本: 晚了 {guess['version']}"
        hints.append({"text": version_hint, "correct": correct_version})
        
        # BPM提示
        correct_bpm = target["bpm"] == guess["bpm"]
        bpm_hint = f"BPM: {guess['bpm']}"
        if not correct_bpm:
            if target["bpm"] > guess["bpm"]:
                bpm_hint = f"BPM: 低了 {guess['bpm']}"
            else:
                bpm_hint = f"BPM: 高了 {guess['bpm']}"
        hints.append({"text": bpm_hint, "correct": correct_bpm})
        
        # 红谱定数提示
        exp_level_same = target["explevel"] == guess["explevel"]
        correct_expds = target["expds"] == guess["expds"]
        
        if correct_expds:
            hints.append({"text": f"红谱定数: {guess['expds']}", "correct": True})
        elif target["expds"] > guess["expds"]:
            if exp_level_same:
                hints.append({"text": f"红谱定数: 低了 {guess['expds']}", "correct": False, "same_level": True})
            else:
                hints.append({"text": f"红谱定数: 低了 {guess['expds']}", "correct": False})
        else:
            if exp_level_same:
                hints.append({"text": f"红谱定数: 高了 {guess['expds']}", "correct": False, "same_level": True})
            else:
                hints.append({"text": f"红谱定数: 高了 {guess['expds']}", "correct": False})
        
        # 紫谱定数提示
        mas_level_same = target["maslevel"] == guess["maslevel"]
        correct_masds = target["masds"] == guess["masds"]
        
        if correct_masds:
            hints.append({"text": f"紫谱定数: {guess['masds']}", "correct": True})
        elif target["masds"] > guess["masds"]:
            if mas_level_same:
                hints.append({"text": f"紫谱定数: 低了 {guess['masds']}", "correct": False, "same_level": True})
            else:
                hints.append({"text": f"紫谱定数: 低了 {guess['masds']}", "correct": False})
        else:
            if mas_level_same:
                hints.append({"text": f"紫谱定数: 高了 {guess['masds']}", "correct": False, "same_level": True})
            else:
                hints.append({"text": f"紫谱定数: 高了 {guess['masds']}", "correct": False})
        
        # 紫谱谱师提示
        correct_charter = target["mascharter"] == guess["mascharter"]
        hints.append({"text": f"紫谱谱师: {guess['mascharter']}", "correct": correct_charter})
        
        # 紫谱绝赞数量提示
        correct_break = target["masbreak"] == guess["masbreak"]
        break_hint = f"紫谱绝赞数量: {guess['masbreak']}"
        if not correct_break:
            if target["masbreak"] > guess["masbreak"]:
                break_hint = f"紫谱绝赞数量: 少了 {guess['masbreak']}"
            else:
                break_hint = f"紫谱绝赞数量: 多了 {guess['masbreak']}"
        
        hints.append({"text": break_hint, "correct": correct_break})
        
        logger.debug(f"生成提示完成，共 {len(hints)} 条提示")
        return hints
    
    def submit_guess(self, guess_id: str, user_id: str) -> Dict[str, Any]:
        """提交猜测"""
        logger.debug(f"玩家 {user_id} 提交猜测: {guess_id}")
        if not self.is_playing:
            logger.warning("游戏未开始，无法提交猜测")
            return {"success": False, "message": "游戏未开始，请先开始游戏！"}
        if not guess_id:
            logger.warning("提交的猜测ID为空")
            return {"success": False, "message": "请输入曲目 ID 或别名。"}
        self.add_player(user_id)
        
        # 查找曲目
        guess_data = self.music_info.get(guess_id)
        if not guess_data:
            logger.debug(f"直接ID未找到: {guess_id}，尝试在别名中查找")
            if guess_id in self.alias:
                logger.debug(f"在别名中找到: {guess_id}")
                if len(self.alias[guess_id]) > 1:
                    logger.debug(f"别名有多个匹配: {self.alias[guess_id]}")
                    matches = [f"ID: {item['id']}, 标题: {item['name']}" for item in self.alias[guess_id]]
                    return {
                        "success": False, 
                        "message": f"别名有多个匹配，请输入具体的曲目 ID：\n{' '.join(matches)}"
                    }
                else:
                    new_id = str(self.alias[guess_id][0]["id"])
                    logger.debug(f"别名唯一匹配，转换为ID: {new_id}")
                    guess_id = new_id
                    guess_data = self.music_info.get(guess_id)
                    if not guess_data:
                        logger.warning(f"转换后的ID不存在: {guess_id}")
                        return {"success": False, "message": "曲目不存在，请重新输入。"}
            else:
                logger.warning(f"曲目ID和别名都不存在: {guess_id}")
                return {"success": False, "message": "曲目不存在，请重新输入。"}
        
        # 检查是否已经猜过
        if guess_id in self.guessed_ids:
            logger.warning(f"已经猜过的ID: {guess_id}")
            return {"success": False, "message": "这个曲目已经被猜过了，请尝试其他曲目。"}
        
        # 记录猜测
        self.guessed_ids.append(guess_id)
        guesser_info = f"[{user_id}] ID: {guess_id}, 标题: {guess_data['title']}"
        self.guesses.append(guesser_info)
        logger.info(f"添加猜测记录: {guesser_info}")
        
        # 生成提示
        hints = self.get_hint(self.target_music, guess_data)
        self.hints_list.append(hints)
        
        # 检查是否猜对
        correct_guess = self.target_music["title"] == guess_data["title"]
        logger.debug(f"检查是否猜对: {correct_guess}")
        
        if correct_guess:
            self.is_playing = False
            logger.info(f"游戏胜利，玩家 {user_id} 猜对了")
            return {
                "success": True,
                "message": f"🎉 恭喜你 猜对了！🎉", 
                "hints": hints,
                "game_over": True,
                "win": True,
                "winner": user_id,
                "players": list(self.players)
            }
        
        # 检查是否已经猜了10次
        if len(self.guesses) >= 10:
            self.is_playing = False
            logger.info("游戏结束，10次机会用完")
            return {
                "success": True,
                "message": f"已经猜错10次，游戏结束！正确答案是 {self.target_music['id']}：{self.target_music['title']}",
                "hints": hints,
                "game_over": True,
                "win": False,
                "players": list(self.players)
            }
        
        logger.info(f"继续游戏，当前已猜测 {len(self.guesses)} 次")
        return {
            "success": True,
            "message": f"猜测继续！",
            "hints": hints,
            "game_over": False
        }
    
    def quit_game(self, user_id: str) -> Dict[str, Any]:
        """结束游戏"""
        logger.info(f"玩家 {user_id} 请求结束游戏")
        
        if not self.is_playing:
            logger.warning("没有正在进行的游戏，无法结束")
            return {"success": False, "message": "当前没有正在进行的游戏。"}
        
        self.is_playing = False
        logger.info(f"游戏已结束，正确答案是: ID={self.target_music['id']}，标题={self.target_music['title']}")
        
        return {
            "success": True,
            "message": f"游戏结束，正确答案是 {self.target_music['id']}：{self.target_music['title']}",
            "players": list(self.players)
        }
    
    def get_game_status(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        status = {
            "is_playing": self.is_playing,
            "difficulty": self.difficulty,
            "guesses_count": len(self.guesses),
            "players_count": len(self.players),
            "remaining_chances": 10 - len(self.guesses) if self.is_playing else 0
        }
        
        if self.is_playing:
            status["players"] = list(self.players)
            status["guessed_songs"] = [g.split(", 标题: ")[1] for g in self.guesses]
        
        return status


def get_random_emoji() -> str:
    """
    获取随机游戏相关的emoji表情
    """
    emoji_list = [
        "🎵", "🎶", "🎼", "🎹", "🎸", "🎷", "🎺", "🎻", "🥁", "🎤", 
        "🎧", "🎬", "🎮", "🎯", "🎲", "🎭", "🎨", "🎪", "🎟️", "🎫",
        "✨", "🌟", "⭐", "💫", "🔥", "💥", "💯", "🏆", "🥇", "🎖️",
        "🎁", "🎉", "🎊", "🎈", "🎀", "🎗️", "🏅", "💎", "👑", "🌈"
    ]
    return random.choice(emoji_list)

def get_mood_emoji(is_correct: bool = False, is_close: bool = False) -> str:
    """
    根据猜测的正确度获取表情
    """
    if is_correct:
        correct_emojis = ["🎉", "🎊", "🥳", "🙌", "👏", "🤩", "✅", "💯", "🏆", "🔥"]
        return random.choice(correct_emojis)
    elif is_close:
        close_emojis = ["🤔", "🧐", "🤏", "👀", "💭", "🔍", "🤏", "↕️", "↔️", "📊"]
        return random.choice(close_emojis)
    else:
        wrong_emojis = ["❌", "🙅", "🤷", "😕", "🤦", "😓", "😬", "🥺", "😢", "⛔"]
        return random.choice(wrong_emojis)

def get_difficulty_emoji(difficulty: str) -> str:
    """
    根据难度级别返回对应的emoji
    """
    difficulty_map = {
        "unlimited": "🌍",
        "13": "⚡",
        "13+": "⚡⚡",
        "14": "💥",
        "14+": "💥💥"
    }
    return difficulty_map.get(difficulty, "🎵")