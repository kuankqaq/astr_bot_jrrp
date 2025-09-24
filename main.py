import os
import json
from datetime import datetime
import random
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register

# 人品值文案
jrrp_text = {
    (0, 10): "今天还是待在家里吧,免得发生意外...",
    (11, 20): "看来你今天运气不怎么样",
    (21, 30): "emm...我该怎么说呢...",
    (31, 40): "一般般吧,不能再多了",
    (41, 50): "还行,不算太差",
    (51, 60): "及格了,再接再厉",
    (61, 70): "运气不错,可以出去走走",
    (71, 80): "哇,今天的运气很棒",
    (81, 90): "今天的运气爆棚了,快去抽卡",
    (91, 100): "!!!你就是天选之子!!!",
}

def get_jrrp_text(jrrp):
    for (min_val, max_val), text in jrrp_text.items():
        if min_val <= jrrp <= max_val:
            return text
    return "这个人今天还没测过人品"

@register("jrrp", "kuank", "一个每日生成一次人品值的插件", "1.0.0", "https://github.com/kuankqaq/astr_bot_jrrp")
class JrrpPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # --- 修改部分 开始 ---
        # 插件数据应存储在 'data/' 下的专属文件夹中
        # 移除不存在的 self.context.get_data_dir()
        self.data_dir = "data/jrrp"
        self.jrrp_file = os.path.join(self.data_dir, "jrrp.json")
        
        # 确保数据目录和文件存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists(self.jrrp_file):
            with open(self.jrrp_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        # --- 修改部分 结束 ---

    @filter.command("jrrp", alias={'今日人品'})
    async def jrrp(self, event: AstrMessageEvent):
        qq = event.get_sender_id()
        today = str(datetime.now().date())
        
        with open(self.jrrp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if qq not in data or data[qq]['date'] != today:
            # 今天还没记录，生成新的人品值
            new_jrrp = random.randint(0, 100)
            
            # --- 特殊修正 ---
           # if qq == "": # 这是 kuank
            #    new_jrrp = 100
           # elif qq == "": # 这是屑老板
            #    new_jrrp = 0
            
            data[qq] = {
                'date': today,
                'jrrp': new_jrrp
            }
            with open(self.jrrp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        
        user_jrrp = data[qq]['jrrp']
        user_name = event.get_sender_name()
        text = get_jrrp_text(user_jrrp)
        
        message = f"{user_name} 今天的人品值是: {user_jrrp}\n{text}"
        yield event.plain_result(message)