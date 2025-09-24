import json
from datetime import datetime
import random

# 导入 AstrBot 的 API
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger # 导入官方 logger

# 人品值文案
# 人品值文案
jrrp_text = {
    (0, 10): "今日运势：凶 ⚠️ 诸事不宜，建议宅家保平安",
    (11, 20): "今日运势：低迷 🌧️ 出门记得带伞，小心水逆",
    (21, 30): "今日运势：平平 ☁️ 保持平常心，稳中求进",
    (31, 40): "今日运势：小吉 🌤️ 小事顺利，大事需谨慎",
    (41, 50): "今日运势：中平 📊 整体平稳，可尝试新计划",
    (51, 60): "今日运势：小旺 📈 适合学习工作，效率提升",
    (61, 70): "今日运势：吉 🍀 机会增多，注意把握时机",
    (71, 80): "今日运势：大吉 ✨ 贵人运旺，合作事项顺利",
    (81, 90): "今日运势：爆棚 🌟 适合抽卡/买彩票！",
    (91, 100): "今日运势：天命之子 🏆 心想事成，好运连连",
}

def get_jrrp_text(jrrp):
    """根据人品值获取对应的文案"""
    for (min_val, max_val), text in jrrp_text.items():
        if min_val <= jrrp <= max_val:
            return text
    return "这个人今天还没测过人品"

@register("jrrp", "kuank", "一个每日生成一次人品值的插件", "1.0.6", "https://github.com/kuankqaq/astr_bot_jrrp")
class JrppPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 初始化一个空字典，用于在内存中存储数据
        self.jrrp_data = {}
        logger.info("Jrrp 插件 (内存存储版) 加载成功。数据将在重启后重置。")

    @filter.command("jrrp", alias={'今日人品'})
    async def jrrp(self, event: AstrMessageEvent):
        """处理 /jrrp 指令"""
        user_id = event.get_sender_id()
        today = str(datetime.now().date())

        # 检查内存中的数据，而不是文件
        if user_id not in self.jrrp_data or self.jrrp_data[user_id].get('date') != today:
            # 如果今天没有记录，就生成新的人品值
            new_jrrp = random.randint(0, 100)
            
            # --- 特殊修正 ---
         #   if user_id == "1303837926": # kuank
          #      new_jrrp = 100
           # elif user_id == "1794009383": # 屑老板
            #    new_jrrp = 0
            
            # 将新的人品值存入内存的字典中
            self.jrrp_data[user_id] = {
                'date': today,
                'jrrp': new_jrrp
            }
        
        # 从内存中获取数据并准备回复消息
        user_jrrp = self.jrrp_data[user_id]['jrrp']
        user_name = event.get_sender_name()
        text = get_jrrp_text(user_jrrp)
        
        message = f"{user_name} 今天的人品值是: {user_jrrp}\n{text}"
        yield event.plain_result(message)