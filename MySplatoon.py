import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

from Splatoon_tools import *

BASE_URL_DM = "https://splatoon.com.cn/api/datasource/external/schedule/list?version=3"

@plugins.register(name="MySplatoon",
                  desc="查询屎不拉通3日程信息",
                  version="1.0",
                  author="piplong",
                  desire_priority=123)
class MySplatoon(Plugin):
    content = None

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f"发送【/涂地】、【/蛮颓开放】、【/蛮颓挑战】、【/X赛】、【/打工】、【/活动】获取 Splatoon3 比赛信息，更多功能正在开发中~"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()

        if self.content == "/涂地":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = get_regular(MySplatoon())
            if result is not None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            return

        if self.content == "/蛮颓开放":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = get_bankara_open(MySplatoon())
            if result is not None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            return

        if self.content == "/蛮颓挑战":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = get_bankara_challenge(MySplatoon())
            if result is not None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            return

        if self.content == "/打工":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = get_coop_stages(MySplatoon())
            if result is not None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            return

        if self.content == "/活动":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = get_event(MySplatoon())
            if result is not None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            return


    def MySplatoon(self):
        url = BASE_URL_DM
        params = {"type": "json"}
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=2)
            if response.status_code == 200:
                json_data = response.json()
                logger.info(f"接口返回的数据：{json_data}")
                if json_data.get('code') == 200 and json_data.get('text'):
                    text = json_data['text']
                    logger.info(f"主接口获取成功：{text}")
                    return json_data
                else:
                    logger.error(f"主接口返回值异常:{json_data}")
                    raise ValueError('not found')
            else:
                logger.error(f"主接口请求失败:{response.text}")
                raise Exception('request failed')
        except Exception as e:
            logger.error(f"接口异常：{e}")
        logger.error("所有接口都挂了,无法获取")
        return None

if __name__ == "__main__":
    my_splatoon_plugin = MySplatoon()
    result = my_splatoon_plugin.MySplatoon()
    if result:
        print("获取到的文案内容：", result)
    else:
        print("获取失败")