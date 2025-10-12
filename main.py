import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 人品值文案（完整）
jrrp_text: Dict[int, str] = {
    0: "今日运势：凶 ⚠️ 诸事不宜，建议宅家保平安",
    1: "今日运势：凶 ⚠️ 运势极差，避免任何冒险",
    2: "今日运势：凶 ⚠️ 容易发生冲突，保持冷静",
    3: "今日运势：凶 ⚠️ 健康运势低迷，多休息",
    4: "今日运势：凶 ⚠️ 财运不济，谨慎消费",
    5: "今日运势：凶 ⚠️ 工作学习效率低，不要强求",
    6: "今日运势：凶 ⚠️ 人际关系易有误会，少言为妙",
    7: "今日运势：凶 ⚠️ 情绪不稳定，避免决策",
    8: "今日运势：凶 ⚠️ 可能丢失物品，注意保管",
    9: "今日运势：凶 ⚠️ 出行不利，尽量留守",
    10: "今日运势：凶 ⚠️ 整体运程差，耐心度过",
    11: "今日运势：低迷 🌧️ 出门记得带伞，小心水逆",
    12: "今日运势：低迷 🌧️ 运势低迷，凡事慢行",
    13: "今日运势：低迷 🌧️ 可能遇到延误，保持耐心",
    14: "今日运势：低迷 🌧️ 心情容易郁闷，找点乐子",
    15: "今日运势：低迷 🌧️ 工作进展缓慢，不要急躁",
    16: "今日运势：低迷 🌧️ 财运平平，避免大笔开支",
    17: "今日运势：低迷 🌧️ 健康注意感冒，保暖防寒",
    18: "今日运势：低迷 🌧️ 人际关系一般，少管闲事",
    19: "今日运势：低迷 🌧️ 学习效率不高，温故知新",
    20: "今日运势：低迷 🌧️ 整体运势不佳，期待明天",
    21: "今日运势：平平 ☁️ 保持平常心，稳中求进",
    22: "今日运势：平平 ☁️ 运势平稳，按部就班",
    23: "今日运势：平平 ☁️ 无风无浪，享受平淡",
    24: "今日运势：平平 ☁️ 工作学习正常发挥",
    25: "今日运势：平平 ☁️ 财运一般，收支平衡",
    26: "今日运势：平平 ☁️ 健康无恙，保持习惯",
    27: "今日运势：平平 ☁️ 人际关系和谐，简单相处",
    28: "今日运势：平平 ☁️ 适合 routine 事务",
    29: "今日运势：平平 ☁️ 不宜冒险，保守为宜",
    30: "今日运势：平平 ☁️ 整体平顺，小有收获",
    31: "今日运势：小吉 🌤️ 小事顺利，大事需谨慎",
    32: "今日运势：小吉 🌤️ 运势渐佳，把握小机会",
    33: "今日运势：小吉 🌤️ 心情不错，适合社交",
    34: "今日运势：小吉 🌤️ 工作有进展，继续努力",
    35: "今日运势：小吉 🌤️ 财运小有收获，但勿贪心",
    36: "今日运势：小吉 🌤️ 健康良好，保持运动",
    37: "今日运势：小吉 🌤️ 人际关系融洽，帮助他人",
    38: "今日运势：小吉 🌤️ 适合学习新知识",
    39: "今日运势：小吉 🌤️ 出行顺利，但注意安全",
    40: "今日运势：小吉 🌤️ 整体吉利，积极行动",
    41: "今日运势：中平 📊 整体平稳，可尝试新计划",
    42: "今日运势：中平 📊 运势中等，适合规划",
    43: "今日运势：中平 📊 工作学习稳定，寻求突破",
    44: "今日运势：中平 📊 财运一般，考虑投资",
    45: "今日运势：中平 📊 健康平稳，注意饮食",
    46: "今日运势：中平 📊 人际关系正常，多沟通",
    47: "今日运势：中平 📊 适合总结反思",
    48: "今日运势：中平 📊 不宜大幅变动",
    49: "今日运势：中平 📊 小有压力，妥善处理",
    50: "今日运势：中平 📊 整体可控，保持平衡",
    51: "今日运势：小旺 📈 适合学习工作，效率提升",
    52: "今日运势：小旺 📈 运势上升，积极行动",
    53: "今日运势：小旺 📈 工作顺利，有望进步",
    54: "今日运势：小旺 📈 学习效率高，抓住时机",
    55: "今日运势：小旺 📈 财运渐旺，小试牛刀",
    56: "今日运势：小旺 📈 健康运佳，精力充沛",
    57: "今日运势：小旺 📈 人际关系友好，合作顺利",
    58: "今日运势：小旺 📈 适合开始新项目",
    59: "今日运势：小旺 📈 整体运势向好，保持努力",
    60: "今日运势：小旺 📈 小有成就，再接再厉",
    61: "今日运势：吉 🍀 机会增多，注意把握时机",
    62: "今日运势：吉 🍀 运势吉利，主动争取",
    63: "今日运势：吉 🍀 工作有好机会，展示能力",
    64: "今日运势：吉 🍀 学习有灵感，深入学习",
    65: "今日运势：吉 🍀 财运不错，可能有意外的",
    66: "今日运势：吉 🍀 健康运好，享受生活",
    67: "今日运势：吉 🍀 人际关系旺，广结善缘",
    68: "今日运势：吉 🍀 适合决策和行动",
    69: "今日运势：吉 🍀 整体顺利，心想事成",
    70: "今日运势：吉 🍀 幸运相伴，勇敢尝试",
    71: "今日运势：大吉 ✨ 贵人运旺，合作事项顺利",
    72: "今日运势：大吉 ✨ 运势大吉，大事可成",
    73: "今日运势：大吉 ✨ 工作得心应手，获得认可",
    74: "今日运势：大吉 ✨ 学习突破，成绩提升",
    75: "今日运势：大吉 ✨ 财运亨通，投资获利",
    76: "今日运势：大吉 ✨ 健康运强，活力四射",
    77: "今日运势：大吉 ✨ 人际关系极佳，遇到贵人",
    78: "今日运势：大吉 ✨ 适合签约和合作",
    79: "今日运势：大吉 ✨ 整体运程灿烂，积极进取",
    80: "今日运势：大吉 ✨ 好运连连，把握机遇",
    81: "今日运势：爆棚 🌟 适合抽卡/买彩票！",
    82: "今日运势：爆棚 🌟 运势爆棚，惊喜不断",
    83: "今日运势：爆棚 🌟 工作学习超常发挥",
    84: "今日运势：爆棚 🌟 财运极佳，大胆行动",
    85: "今日运势：爆棚 🌟 健康运满分，充满能量",
    86: "今日运势：爆棚 🌟 人际关系火爆，受欢迎",
    87: "今日运势：爆棚 🌟 适合冒险和尝试",
    88: "今日运势：爆棚 🌟 整体运气极好，心想事成",
    89: "今日运势：爆棚 🌟 幸运女神微笑，抓住机会",
    90: "今日运势：爆棚 🌟 好事成双，享受当下",
    91: "今日运势：天命之子 🏆 心想事成，好运连连",
    92: "今日运势：天命之子 🏆 运势无敌，一切顺利",
    93: "今日运势：天命之子 🏆 工作达到巅峰，获得成就",
    94: "今日运势：天命之子 🏆 学习完美，理解深刻",
    95: "今日运势：天命之子 🏆 财运爆表，财富滚滚",
    96: "今日运势：天命之子 🏆 健康极佳，身心愉悦",
    97: "今日运势：天命之子 🏆 人际关系完美，支持众多",
    98: "今日运势：天命之子 🏆 适合任何挑战",
    99: "今日运势：天命之子 🏆 整体运程完美，享受成功",
    100: "今日运势：天命之子 🏆 天选之人，无所不能",
}


def get_jrrp_text(jrrp: int) -> str:
    """根据人品值获取对应的文案"""
    return jrrp_text.get(jrrp, "这个人今天还没测过人品")


def get_data_file_path() -> Path:
    """获取数据文件路径"""
    plugin_dir = Path(__file__).parent
    data_dir = plugin_dir / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "jrrp_data.json"


def load_jrrp_data() -> Dict[str, Any]:
    """从JSON文件加载数据，如果日期不是今天则重置"""
    today = str(datetime.now().date())
    try:
        data_file = get_data_file_path()
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)
                if data.get('last_updated_date') != today:
                    logger.info("检测到日期变更，重置人品数据")
                    return {'last_updated_date': today, 'users': {}}
                return data
        return {'last_updated_date': today, 'users': {}}
    except Exception as e:
        logger.error(f"加载人品数据失败: {e}")
        return {'last_updated_date': today, 'users': {}}


def save_jrrp_data(data: Dict[str, Any]) -> None:
    """保存数据到JSON文件，并更新日期"""
    try:
        data['last_updated_date'] = str(datetime.now().date())
        with open(get_data_file_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存人品数据失败: {e}")


@register("jrrp", "kuank", "一个每日生成一次人品值的插件", "1.0.6", "https://github.com/kuankqaq/astr_bot_jrrp")
class JrrpPlugin(Star):
    """Jrrp 插件：每日生成并持久化保存用户人品值"""

    def __init__(self, context: Context):
        super().__init__(context)
        self.jrrp_data: Dict[str, Any] = load_jrrp_data()
        logger.info("Jrrp 插件 (JSON持久化版) 加载成功。数据已从文件加载。")

    @filter.command("jrrp", alias={'今日人品'})
    async def jrrp(self, event: AstrMessageEvent):
        """处理 /jrrp 指令，生成或返回用户今日人品值"""
        user_id: str = event.get_sender_id()
        today: str = str(datetime.now().date())

        if self.jrrp_data.get('last_updated_date') != today:
            self.jrrp_data = {'last_updated_date': today, 'users': {}}
            save_jrrp_data(self.jrrp_data)

        user_data: Dict[str, Any] = self.jrrp_data['users'].get(user_id, {})
        if user_data.get('date') != today:
            new_jrrp: int = random.randint(0, 100)
            self.jrrp_data['users'][user_id] = {'date': today, 'jrrp': new_jrrp}
            save_jrrp_data(self.jrrp_data)

        user_jrrp: int = self.jrrp_data['users'][user_id]['jrrp']
        message: str = f"{event.get_sender_name()} 今天的人品值是: {user_jrrp}\n{get_jrrp_text(user_jrrp)}"
        yield event.plain_result(message)
