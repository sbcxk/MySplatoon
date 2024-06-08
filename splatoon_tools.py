import datetime
from plugins.MySplatoon.image_processer_tools import *
from plugins.MySplatoon.utils import *
from common.log import logger


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
    for i, group in enumerate(data[4].groups):
        text += "地图: " + group.subCards[0]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt) + "\n"
        text += "武器: "
        for index, weapon in enumerate(group.weapons):
            text += weapon['name']
            if index < len(group.weapons) - 1:  # 检查是否是最后一个元素
                text += "、"
        text += "\nBoss: " + group.boss['name']
        if i < len(data[4].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
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
        if index < len(data[1].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


def get_bankara_open(data):
    text = "蛮颓(开放)\n"
    for index, group in enumerate(data[2].groups):
        text += "模式: " + group.groupTitle + "\n"
        text += "地图: " + group.subCards[0]['subCardTitle'] + " & " + group.subCards[1]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        if index < len(data[2].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


def get_event(data):
    text = "活动比赛\n"
    for index, group in enumerate(data[5].groups):
        text += "活动: " + group.subTitle + " - " + group.description + "\n"
        text += "模式: " + group.groupTitle + "\n"
        text += "地图: " + group.subCards[0]['subCardTitle'] + " & " + group.subCards[1]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        if index < len(data[5].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


def get_x_match(data):
    text = "X比赛\n"
    for index, group in enumerate(data[3].groups):
        text += "模式: " + group.groupTitle + "\n"
        text += "地图: " + group.subCards[0]['subCardTitle'] + " & " + group.subCards[1]['subCardTitle'] + "\n"
        text += "时间: " + remove_year(group.startAt) + " ~ " + remove_year(group.endAt)
        if index < len(data[3].groups) - 1:  # 检查是否是最后一个元素
            text += "\n\n"
    return text


# 获取打工信息
def get_coop_info(data, _all=None):
    """取 打工 信息"""

    # 取时间信息
    def get_str_time(start, end):
        # _start_time = time_converter_mdhm(start)
        _start_time = remove_year(start)
        # _end_time = time_converter_mdhm(end)
        _end_time = remove_year(end)
        return "{} - {}".format(_start_time, _end_time)

    # 取日程
    schedule = formatS3JSON(data)
    # 一般打工数据
    stage = []
    stage_name = []
    weapon = []
    time = []
    boss = []
    mode = []
    for i, group in enumerate(schedule[4].groups):
        stage.append(group.subCards[0]['pic'])
        stage_name.append(group.subCards[0]['subCardTitle'])
        w = []
        for index, weapons in enumerate(group.weapons):
            w.append(weapons['icon'])
        weapon.append(w)
        time.append(get_str_time(group.startAt, group.endAt))
        boss.append(group.boss['icon'])
        mode.append("coop")

    return stage, stage_name, weapon, time, boss, mode


def get_coop_stages(stage, stage_name, weapon, time, boss):
    """绘制 打工地图"""

    # 校验是否需要绘制小鲑鱼(现在时间处于该打工时间段内)
    def check_coop_fish(_time):
        start_time = _time.split(" - ")[0]
        now_time = get_time_now_china()
        # 输入时间都缺少年份，需要手动补充一个年份后还原为date对象
        year = now_time.year
        start_time = str(year) + "-" + start_time
        st = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        if st < now_time:
            return True
        return False

    top_size_pos = (0, -2)
    bg_size = (800, len(stage) * 162 + top_size_pos[1])
    stage_bg_size = (300, 160)
    weapon_size = (90, 90)
    boss_size = (40, 40)
    mode_size = (40, 40)
    coop_fish_size = (36, 48)

    # 创建纯色背景
    image_background_rgb = dict_bg_rgb["打工"]
    image_background = Image.new("RGBA", bg_size, image_background_rgb)
    bg_mask_size = (300, 200)
    bg_mask = get_file("coop_mask").resize(bg_mask_size)
    # 填充小图蒙版
    image_background = tiled_fill(image_background, bg_mask)

    # 绘制地图信息
    coop_stage_bg = Image.new("RGBA", (bg_size[0], bg_size[1] + 2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(coop_stage_bg)
    font = ImageFont.truetype(ttf_path, 30)
    for pos, val in enumerate(time):
        # 绘制时间文字
        time_text_pos = (50, 5 + pos * 160)
        # time_text_size = font.getsize(val)
        dr.text(time_text_pos, val, font=font, fill="#FFFFFF")
        # if check_coop_fish(val):
        #     # 现在时间处于打工时间段内，绘制小鲑鱼
        #     coop_fish_img = get_file("coop_fish").resize(coop_fish_size)
        #     coop_fish_img_pos = (5, 8 + pos * 160)
        #     paste_with_a(coop_stage_bg, coop_fish_img, coop_fish_img_pos)
    for pos, val in enumerate(stage):
        # 绘制打工地图
        stage_bg = get_image_from_url(val).resize(stage_bg_size, Image.ANTIALIAS)
        stage_bg_pos = (500, 2 + 162 * pos)
        coop_stage_bg.paste(stage_bg, stage_bg_pos)

        # 绘制 地图名
        stage_name_bg = get_stage_name_bg(stage_name[pos], 25)
        stage_name_bg_size = stage_name_bg.size
        # X:地图x点位+一半的地图宽度-文字背景的一半宽度   Y:地图Y点位+一半地图高度-文字背景高度
        stage_name_bg_pos = (
            stage_bg_pos[0] + +stage_bg_size[0] // 2 - stage_name_bg_size[0] // 2,
            stage_bg_pos[1] + stage_bg_size[1] - stage_name_bg_size[1],
        )
        paste_with_a(coop_stage_bg, stage_name_bg, stage_name_bg_pos)

        for pos_weapon, val_weapon in enumerate(weapon[pos]):
            # 绘制武器底图
            weapon_bg_img = Image.new("RGBA", weapon_size, (30, 30, 30))
            # 绘制武器图片
            weapon_image = get_image_from_url(val_weapon).resize(weapon_size, Image.ANTIALIAS)
            paste_with_a(weapon_bg_img, weapon_image, (0, 0))
            coop_stage_bg.paste(weapon_bg_img, (120 * pos_weapon + 20, 60 + 160 * pos))
    for pos, val in enumerate(boss):
        if val != "":
            # 绘制boss图标
            try:
                boss_img = get_image_from_url(val).resize(boss_size)
                boss_img_pos = (500, 160 * pos + stage_bg_size[1] - 40)
                paste_with_a(coop_stage_bg, boss_img, boss_img_pos)
            except Exception as e:
                logger.warning(f"get boss file error: {e}")
    # for pos, val in enumerate(mode):
    #     # 绘制打工模式图标
    #     mode_img = get_file(val).resize(mode_size)
    #     mode_img_pos = (500 - 70, 160 * pos + 15)
    #     paste_with_a(coop_stage_bg, mode_img, mode_img_pos)

    paste_with_a(image_background, coop_stage_bg, top_size_pos)
    # 圆角
    image_background = circle_corner(image_background, radii=20)

    return image_background


def get_coop_stages_image(data):
    """取 打工图片"""
    # 获取数据
    stage, stage_name, weapon, time, boss, mode = get_coop_info(data)
    # 绘制图片
    image = get_coop_stages(stage, stage_name, weapon, time, boss)
    return image


def remove_year(date_str):
    return date_str[3:]
