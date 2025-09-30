import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Callable

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 人品值文案（完整，仅示例部分，实际请替换为全量 jrrp_text）
jrrp_text: Dict[int, str] = {
    0: "今日运势：凶 ⚠️ 诸事不宜，建议宅家保平安",
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


# 特殊用户规则示例
SPECIAL_RULES: Dict[str, Callable[[], int]] = {
    "123456789": lambda: 100,  # 用户 ID 为 123456789 的用户固定 100
    "114514": lambda: 0,    # 用户 ID 为 114514 的用户固定 0
    "1919810": lambda: random.choice([0, random.randint(0, 100)])  # 用户 ID 为 1919810 的用户有概率为 0
}


@register("jrrp", "kuank", "一个每日生成一次人品值的插件", "1.0.0", "https://github.com/kuankqaq/astr_bot_jrrp")
class JrrpPlugin(Star):
    """Jrrp 插件：每日生成并持久化保存用户人品值，支持特殊用户规则"""

    def __init__(self, context: Context):
        super().__init__(context)
        self.jrrp_data: Dict[str, Any] = load_jrrp_data()
        logger.info("Jrrp 插件 (特殊用户规则版) 加载成功。数据已从文件加载。")

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
            # 使用特殊规则或随机生成
            new_jrrp: int = SPECIAL_RULES.get(user_id, lambda: random.randint(0, 100))()
            self.jrrp_data['users'][user_id] = {'date': today, 'jrrp': new_jrrp}
            save_jrrp_data(self.jrrp_data)

        user_jrrp: int = self.jrrp_data['users'][user_id]['jrrp']
        message: str = f"{event.get_sender_name()} 今天的人品值是: {user_jrrp}\n{get_jrrp_text(user_jrrp)}"
        yield event.plain_result(message)
