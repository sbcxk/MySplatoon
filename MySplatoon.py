import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger


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
        help_text = f"发送【/涂地】、【/蛮颓开放】、【/蛮颓挑战】、【/x比赛】、【/打工】、【/活动】获取 Splatoon3 比赛信息，更多功能正在开发中~"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()

        if self.content == "/涂地":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = get_regular(self.MySplatoon())
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
            result = get_bankara_open(self.MySplatoon())
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
            result = get_bankara_challenge(self.MySplatoon())
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
            result = get_coop_stages(self.MySplatoon())
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
            result = get_event(self.MySplatoon())
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

        if self.content == "/x比赛":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = get_x_match(self.MySplatoon())
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
    result = my_splatoon_plugin
    if result:
        print("获取到的文案内容：", result)
    else:
        print("获取失败")

# 创建结构体来存储数据
class Tab:
    def __init__(self, id, key, name, image=None, isDropdown=False, subTabs=None):
        self.id = id
        self.key = key
        self.name = name
        self.image = image
        self.isDropdown = isDropdown
        self.subTabs = subTabs

    def __str__(self):
        return f"Tab(id={self.id}, key={self.key}, name={self.name}, image={self.image}, isDropdown={self.isDropdown}, subTabs={self.subTabs})"


class Content:
    def __init__(self, id, title, groups):
        self.id = id
        self.title = title
        self.groups = groups

    def __str__(self):
        return f"Content(id={self.id}, title={self.title}, groups={self.groups})"


class Group:
    def __init__(self, id, groupTitle, icon, subCards, startAt, endAt, weapons, badges, boss, subTitle, description):
        self.id = id
        self.groupTitle = groupTitle
        self.icon = icon
        self.subCards = subCards
        self.startAt = startAt
        self.endAt = endAt
        self.weapons = weapons
        self.badges = badges
        self.boss = boss
        self.subTitle = subTitle
        self.description = description

    def __str__(self):
        sub_cards_str = "\n".join([
            f"SubCard(id={sub_card['id']}, key={sub_card['key']}, pic={sub_card['pic']}, subCardTitle={sub_card['subCardTitle']})"
            for sub_card in self.subCards])
        return f"Group(id={self.id}, groupTitle={self.groupTitle}, icon={self.icon}, subCards=[{sub_cards_str}], startAt={self.startAt}, endAt={self.endAt}, weapons={self.weapons}, badges={self.badges})"


def formatS3JSON(data_dict):
    # 将 JSON 数据解析为 Python 字典
    # data_dict = json.loads(data)
    # 解析数据并存储到结构体中
    tabs = []
    for tab_data in data_dict["data"]["tabs"]:
        if "subTabs" in tab_data:
            sub_tabs = [Tab(sub_tab["id"], sub_tab["key"], sub_tab["name"], sub_tab["image"]) for sub_tab in
                        tab_data["subTabs"]]
            tabs.append(Tab(tab_data["id"], tab_data["key"], tab_data["name"], tab_data["image"], True, sub_tabs))
        else:
            tabs.append(Tab(tab_data["id"], tab_data["key"], tab_data["name"], tab_data["image"]))

    contents = []
    # 解析 JSON 数据并存储到结构体中
    for content_data in data_dict["data"]["contents"]:
        groups = []
        for group_data in content_data["groups"]:
            sub_cards = group_data["subCards"]
            start_at = group_data["startAt"]
            end_at = group_data["endAt"]
            weapons = group_data["weapons"]
            badges = group_data["badges"]
            boss = None
            subTitle = None
            description = None
            if "boss" in group_data:
                boss = group_data["boss"]
            if "subTitle" in group_data:
                subTitle = group_data["subTitle"]
            if "description" in group_data:
                description = group_data["description"]
            groups.append(
                Group(group_data["id"], group_data["groupTitle"], group_data["icon"], sub_cards, start_at, end_at,
                      weapons, badges, boss, subTitle, description))
        contents.append(Content(content_data["id"], content_data["title"], groups))

    return contents


def get_coop_stages(data):
    text = "鲑鱼跑\n"
    for group in data[4].groups:
        text += "地图: " + group.subCards[0]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        text += "武器: "
        for index, weapon in enumerate(group.weapons):
            text += weapon['name']
            if index < len(group.weapons) - 1:  # 检查是否是最后一个元素
                text += "、"
        text += "\n"
        text += "Boss: "
        text += group.boss['name']
        text += "\n\n"
        # print(group.boss)
        # print(group)
        # print(contents[4].groups)
    return text


def get_regular(data):
    text = "涂地/一般比赛\n"
    for index, group in enumerate(data[0].groups):
        text += "地图: " + group.subCards[0]['subCardTitle'] + " & " + group.subCards[1]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        if index < len(data[0].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


def get_bankara_challenge(data):
    text = "蛮颓(挑战)\n"
    for index, group in enumerate(data[1].groups):
        text += "模式: " + group.groupTitle + "\n"
        text += "地图: " + group.subCards[0]['subCardTitle'] + " & " + group.subCards[1]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        text += remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        if index < len(data[0].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


def get_bankara_open(data):
    text = "蛮颓(开放)\n"
    for index, group in enumerate(data[2].groups):
        text += "模式: " + group.groupTitle + "\n"
        text += "地图: " + group.subCards[0]['subCardTitle'] + " & " + group.subCards[1]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        if index < len(data[0].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


def get_event(data):
    text = "活动比赛\n"
    for index, group in enumerate(data[5].groups):
        text += "活动: " + group.subTitle + " - " + group.description + "\n"
        text += "模式: " + group.groupTitle + "\n"
        text += "地图: " + group.subCards[0]['subCardTitle'] + " & " + group.subCards[1]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        if index < len(data[0].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


def get_x_match(data):
    text = "X比赛\n"
    for index, group in enumerate(data[2].groups):
        text += "模式: " + group.groupTitle + "\n"
        text += "地图: " + group.subCards[0]['subCardTitle'] + " & " + group.subCards[1]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        if index < len(data[0].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


def remove_year(date_str):
    return date_str[3:]
