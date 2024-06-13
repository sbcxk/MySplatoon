import io

import requests
import plugins
from plugins import *
from plugins.MySplatoon.splatoon_tools import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from functools import lru_cache

BASE_URL_DM = "https://splatoon.com.cn/api/datasource/external/schedule/list?version=3"
options = ["/涂地", "/蛮颓开放", "/蛮颓挑战", "/x比赛", "/打工", "/活动", "/打工图", "/日程图"]


@plugins.register(name="MySplatoon",
                  desc="查询屎不拉通3日程信息",
                  version="1.1",
                  author="piplong",
                  desire_priority=123)
class MySplatoon(Plugin):
    content = None

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f"【温馨提示】下列功能均需 @机器人 后发送\n\n" \
                    f"👉发送：【/日程图 】、【/打工图】获取 Splatoon 3 日程图片信息\n\n" \
                    f"👉发送：【/涂地】、【/蛮颓开放】、【/蛮颓挑战】、【/x比赛】、【/打工】、【/活动】获取比赛文字信息\n\n" \
                    f"参考致谢：https://github.com/Cypas/splatoon3-schedule\n\n" \
                    f"更多功能正在开发中，欢迎提供意见~"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        result, reply = None, None
        if self.content in options:
            if self.content == "/涂地":
                logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
                reply = Reply()
                reply.type = ReplyType.TEXT
                result = get_regular(formatS3JSON(self.MySplatoon()))

            elif self.content == "/蛮颓开放":
                logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
                reply = Reply()
                reply.type = ReplyType.TEXT
                result = get_bankara_open(formatS3JSON(self.MySplatoon()))

            elif self.content == "/蛮颓挑战":
                logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
                reply = Reply()
                reply.type = ReplyType.TEXT
                result = get_bankara_challenge(formatS3JSON(self.MySplatoon()))

            elif self.content == "/打工":
                logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
                reply = Reply()
                reply.type = ReplyType.TEXT
                result = get_coop_stages(formatS3JSON(self.MySplatoon()))

            elif self.content == "/活动":
                logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
                reply = Reply()
                reply.type = ReplyType.TEXT
                result = get_event(formatS3JSON(self.MySplatoon()))

            elif self.content == "/x比赛":
                logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
                reply = Reply()
                reply.type = ReplyType.TEXT
                result = get_x_match(formatS3JSON(self.MySplatoon()))

            elif self.content == "/打工图":
                logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
                reply = Reply()
                img = get_coop_stages_image(self.MySplatoon())
                b_img = io.BytesIO()
                img.save(b_img, format="PNG")
                result = b_img
                # 图片类型
                reply.type = ReplyType.IMAGE

            elif self.content == "/日程图":
                logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
                reply = Reply()
                result = get_cached_image(self.MySplatoon())
                # b_img = io.BytesIO()
                # img.save(b_img, format="PNG")
                # result = b_img
                # 图片类型
                reply.type = ReplyType.IMAGE

            if result is not None:
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
                # logger.info(f"接口返回的数据：{json_data}")
                if json_data.get('status') and json_data.get('data'):
                    text = json_data['data']
                    # logger.info(f"主接口获取成功：{text}")
                    # res = formatS3JSON(json_data.get('data'))
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
    result = my_splatoon_plugin
    if result:
        print("获取到的文案内容：", result)
    else:
        print("获取失败")
