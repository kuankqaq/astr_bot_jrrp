import random
import sqlite3
from pathlib import Path
from datetime import datetime

# 严格遵循官方文档，从正确的 `astrbot.api` 路径导入所需模块
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

def _get_luck_description(luck: int) -> str:
    """根据人品值返回对应的配文"""
    if luck == 100:
        return "✨ 欧皇附体！今天你就是天选之子，做什么都顺！✨"
    elif luck >= 90:
        return "🎉 吉星高照！今天运气爆棚，快去买张彩票吧！"
    elif luck >= 75:
        return "👍 顺风顺水！今天是个好日子，事事顺心。"
    elif luck >= 60:
        return "👌 平平稳稳！普通的一天，保持平常心就好。"
    elif luck >= 40:
        return "🤔 稍安勿躁。今天可能会遇到点小麻烦，问题不大。"
    elif luck >= 20:
        return "😥 诸事不宜！今天还是摸鱼吧，别搞大事。"
    elif luck >= 1:
        return "😭 非酋本酋！今天出门记得看黄历，小心行事！"
    else:
        return "数值异常，你的人品可能超越了三界！"

@register(
    "jrrp",  # 插件ID
    "kuank",  # 你的名字
    "一个每日生成一次人品值的插件",  # 描述
    "1.0.4",  # 版本
    "https://github.com/kuankqaq/astr_bot_jrrp"  # 你的仓库地址
)
class JrppPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        
        # --- 最终修正 ---
        # 获取插件专属数据目录的唯一正确方法，是通过 self (插件实例) 调用
        plugin_data_dir = self.get_data_dir()
        plugin_data_dir.mkdir(exist_ok=True) # 确保目录存在
        db_path = plugin_data_dir / "jrrp.db"
        
        logger.info(f"今日人品插件数据库路径: {db_path}")
        
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """初始化数据库，创建表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jrrp (
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                luck_value INTEGER NOT NULL,
                PRIMARY KEY (user_id, date)
            );
        ''')
        self.conn.commit()

    @filter.command("jrrp", alias={'今日人品'})
    async def handle_jrrp(self, event: AstrMessageEvent):
        """处理 jrrp 或 今日人品 命令"""
        user_id = event.get_sender_id()
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT luck_value FROM jrrp WHERE user_id = ? AND date = ?", (user_id, today_str))
        result = cursor.fetchone()
        
        if result:
            luck = result[0]
            description = _get_luck_description(luck)
            reply = (
                f"你今天的人品是【{luck}】！\n"
                f"{description}\n\n"
                "今天已经测过了哦，明天再来吧！"
            )
            yield event.plain_result(reply)
            return

        luck = random.randint(1, 100)
        description = _get_luck_description(luck)
        
        try:
            cursor.execute("INSERT INTO jrrp (user_id, date, luck_value) VALUES (?, ?, ?)", (user_id, today_str, luck))
            self.conn.commit()
            
            reply = (
                f"你今天的人品是【{luck}】！\n"
                f"{description}"
            )
            yield event.plain_result(reply)

        except Exception as e:
            logger.error(f"写入jrrp数据时出错: {e}")
            yield event.plain_result("哎呀，运势数据库出了点问题，请稍后再试！")

    async def terminate(self):
        """插件卸载时关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("今日人品插件数据库连接已关闭。")
