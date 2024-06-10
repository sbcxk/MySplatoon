import datetime
import hashlib
import io
import tempfile
import time

from plugins.MySplatoon.image_processer_tools import *
from plugins.MySplatoon.utils import *
from common.log import logger

# 全局缓存字典
image_cache = {}

# 缓存有效期（秒）
CACHE_TTL = 2 * 60 * 60  # 2小时

# 类 图片信息 ImageInfo
class ImageInfo:
    def __init__(self, name, url, zh_name, source_type):
        self.name = name
        self.url = url
        self.zh_name = zh_name
        self.source_type = source_type

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


def get_coop_stage(stage, stage_name, weapon, time, boss):
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
        stage_bg = get_image_from_url(val).resize(stage_bg_size, Image.LANCZOS)
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
            weapon_image = get_image_from_url(val_weapon).resize(weapon_size, Image.LANCZOS)
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
    image = get_coop_stage(stage, stage_name, weapon, time, boss)
    # 将 Image 对象保存到临时文件
    # with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
    #     image.save(temp_file.name)
    #     file_path = temp_file.name
    return image


def remove_year(date_str):
    return date_str[3:]


# ==================对战日程======================

# 翻译字典
dict_rule_reverse_trans = {
    "LOFT": "真格塔楼",
    "CLAM": "真格蛤蜊",
    "GOAL": "真格鱼虎",
    "AREA": "真格区域",
    "TURF_WAR": "占地对战",
    "真格塔楼": "LOFT",
    "真格蛤蜊": "CLAM",
    "真格鱼虎": "GOAL",
    "真格区域": "AREA",
    "占地对战": "TURF_WAR",
    "真格鱼虎对战": "GOAL",
}

def get_trans_game_mode(text):
    """用现有翻译字典对游戏模式进行翻译"""
    if text in dict_rule_reverse_trans:
        return dict_rule_reverse_trans[text]
    return text

def time_converter_yd(time_str):
    """
    将时间字符串 "DD/MM/YY HH:MM" 转换为 "日-月" 格式。

    :param time_str: 时间字符串，格式为 "DD/MM/YY HH:MM"
    :return: 返回转换后的 "日-月" 格式的字符串
    """
    try:
        # 解析时间字符串
        dt = datetime.strptime(time_str, '%y/%m/%d %H:%M')
    except ValueError:
        raise ValueError('时间字符串格式不正确，应为 "DD/MM/YY HH:MM"')

    # 格式化为 "日-月"
    day_month = dt.strftime('%m-%d')
    return day_month


def time_converter_hm(time_str):
    """
    将时间字符串 "DD/MM/YY HH:MM" 转换为 "时:分" 格式。

    :param time_str: 时间字符串，格式为 "DD/MM/YY HH:MM"
    :return: 返回转换后的 "时:分" 格式的字符串
    """
    try:
        # 解析时间字符串
        dt = datetime.strptime(time_str, '%d/%m/%y %H:%M')
    except ValueError:
        raise ValueError('时间字符串格式不正确，应为 "DD/MM/YY HH:MM"')

    # 格式化为 "时:分"
    hour_minute = dt.strftime('%H:%M')
    return hour_minute

# 绘制 一排 地图卡片
def get_stage_card(
        stage1,
        stage2,
        contest_mode,
        contest_name,
        game_mode,
        start_time="",
        end_time="",
        desc="",
        img_size=(1024, 340),
):
    image_background = circle_corner(get_file("bg").resize(img_size), radii=20)

    # 绘制两张地图
    # 计算尺寸，加载图片
    stage_size = (int(img_size[0] * 0.48), int(img_size[1] * 0.7))
    image_left = get_image_from_url(stage1.url).resize(stage_size, Image.LANCZOS)
    image_right = get_image_from_url(stage2.url).resize(stage_size, Image.LANCZOS)
    # 定义圆角 蒙版
    image_alpha = circle_corner(image_left, radii=16)

    # 计算地图间隔
    width_between_stages = int((img_size[0] - 2 * stage_size[0]) / 3)
    # 绘制第一张地图
    # 图片左上点位
    start_stage_pos = (
        width_between_stages,
        int((img_size[1] - stage_size[1]) / 8 * 7) - 20,
    )
    image_background.paste(image_left, start_stage_pos, mask=image_alpha)
    # 绘制第二张地图
    # 图片左上点位
    next_stage_pos = (
        start_stage_pos[0] + width_between_stages + stage_size[0],
        start_stage_pos[1],
    )
    image_background.paste(image_right, next_stage_pos, mask=image_alpha)

    # 绘制地图中文名及文字背景
    # 左半地图名
    stage_name_bg = get_stage_name_bg(stage1.zh_name, 30)
    stage_name_bg_size = stage_name_bg.size
    # X:地图x点位+一半的地图宽度-文字背景的一半宽度   Y:地图Y点位+一半地图高度-文字背景高度
    stage_name_bg_pos = (
        start_stage_pos[0] + stage_size[0] // 2 - stage_name_bg_size[0] // 2,
        start_stage_pos[1] + stage_size[1] - stage_name_bg_size[1],
    )
    paste_with_a(image_background, stage_name_bg, stage_name_bg_pos)

    # 右半地图名
    stage_name_bg = get_stage_name_bg(stage2.zh_name, 30)
    stage_name_bg_size = stage_name_bg.size
    # X:地图x点位+一半的地图宽度-文字背景的一半宽度   Y:地图Y点位+一半地图高度-文字背景高度
    stage_name_bg_pos = (
        next_stage_pos[0] + +stage_size[0] // 2 - stage_name_bg_size[0] // 2,
        next_stage_pos[1] + stage_size[1] - stage_name_bg_size[1],
    )
    paste_with_a(image_background, stage_name_bg, stage_name_bg_pos)

    # 中间绘制 模式图标
    # 中文转英文来取文件
    image_icon = get_file(contest_name)
    image_icon_size = image_icon.size
    # X: 整张卡片宽度/2 - 图标宽度/2    Y: 左地图x点位+地图高度/2 - 图标高度/2
    stage_mid_pos = (
        img_size[0] // 2 - image_icon_size[0] // 2,
        start_stage_pos[1] + stage_size[1] // 2 - image_icon_size[1] // 2,
    )
    paste_with_a(image_background, image_icon, stage_mid_pos)

    # 绘制模式文本
    # 空白尺寸
    blank_size = (img_size[0], start_stage_pos[1])
    drawer = ImageDraw.Draw(image_background)
    # 绘制竞赛模式文字
    ttf = ImageFont.truetype(ttf_path_chinese, 40)
    contest_mode_pos = (start_stage_pos[0] + 10, start_stage_pos[1] - 60)
    drawer.text(contest_mode_pos, contest_mode, font=ttf, fill=(255, 255, 255))
    # 绘制游戏模式文字
    game_mode_text = game_mode
    game_mode_text_pos = (blank_size[0] // 3, contest_mode_pos[1])
    drawer.text(game_mode_text_pos, game_mode_text, font=ttf, fill=(255, 255, 255))
    # 绘制游戏模式小图标
    game_mode_img = get_file(get_trans_game_mode(game_mode)).resize((35, 35), Image.LANCZOS)
    game_mode_img_pos = (game_mode_text_pos[0] - 40, game_mode_text_pos[1] + 10)
    paste_with_a(image_background, game_mode_img, game_mode_img_pos)
    # # 绘制开始，结束时间
    # ttf = ImageFont.truetype(ttf_path, 40)
    # time_pos = (blank_size[0] * 2 // 3, contest_mode_pos[1] - 10)
    # drawer.text(
    #     time_pos, "{} - {}".format(start_time, end_time), font=ttf, fill=(255, 255, 255)
    # )
    # 绘制活动模式描述
    if desc != "":
        ttf = ImageFont.truetype(ttf_path, 40)
        desc_pos = (blank_size[0] * 2 // 3, contest_mode_pos[1] - 10)
        drawer.text(desc_pos, desc, font=ttf, fill=(255, 255, 255))

    return image_background


def get_stage_info(data):
    """取 图 信息"""
    num_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    schedule = formatS3JSON(data)

    return schedule, num_list


def get_stages(schedule, num_list, contest_match=None, rule_match=None):
    """绘制 竞赛地图"""
    # 涂地
    regular = schedule[0]
    # 真格
    ranked_open = schedule[2]
    ranked_challenge = schedule[1]
    # X段
    xschedule = schedule[3]
    # 祭典
    # festivals = schedule["festSchedules"]["nodes"]

    # 如果存在祭典，且当前时间位于祭典，转变为输出祭典地图，后续不再进行处理
    # TODO

    cnt = 12
    time_head_count = 3
    time_head_bg_size = (540, 60)
    # 一张对战卡片高度为340 时间卡片高度为time_head_bg_size[1] 加上间隔为10
    background_size = (1044, 340 * cnt + (time_head_bg_size[1] + 10) * time_head_count)
    # 取背景rgb颜色
    default_bg_rgb = dict_bg_rgb["X Schedule"]
    if contest_match is not None:
        bg_rgb = dict_bg_rgb[contest_match]
    else:
        bg_rgb = default_bg_rgb
    # 创建纯色背景
    image_background = Image.new("RGBA", background_size, bg_rgb)
    bg_mask = get_file("fight_mask").resize((600, 399))
    # 填充小图蒙版
    image_background = tiled_fill(image_background, bg_mask)

    total_pos = 0
    for i in num_list:
        pos = 0
        # 创建一张纯透明图片 用来存放一个时间周期内的多张地图卡片
        background = Image.new("RGBA", background_size, (0, 0, 0, 0))
        # 筛选到数据的个数
        count_match_data = 0

        # 第一排绘制 默认为涂地模式
        if regular is not None:
            count_match_data += 1
            stage = regular.groups[i]
            regular_card = get_stage_card(
                ImageInfo(
                    name=stage.subCards[0]['pic'],
                    url=stage.subCards[0]['pic'],
                    zh_name=stage.subCards[0]['subCardTitle'],
                    source_type="对战地图",
                ),
                ImageInfo(
                    name=stage.subCards[1]['pic'],
                    url=stage.subCards[1]['pic'],
                    zh_name=stage.subCards[1]['subCardTitle'],
                    source_type="对战地图",
                ),
                "一般比赛",
                "Regular",
                stage.groupTitle,
                # "Regular",
                remove_year(stage.startAt),
                remove_year(stage.endAt),
            )
            paste_with_a(background, regular_card, (10, pos))
            pos += 340
            total_pos += 340

        # 第二排绘制 默认为真格区域
        if ranked_challenge is not None:
            count_match_data += 1
            ranked = ranked_challenge.groups[i]
            ranked_challenge_card = get_stage_card(
                ImageInfo(
                    name=ranked.subCards[0]['pic'],
                    url=ranked.subCards[0]['pic'],
                    zh_name=ranked.subCards[0]['subCardTitle'],
                    source_type="对战地图",
                ),
                ImageInfo(
                    name=ranked.subCards[1]['pic'],
                    url=ranked.subCards[1]['pic'],
                    zh_name=ranked.subCards[1]['subCardTitle'],
                    source_type="对战地图",
                ),
                "蛮颓比赛-挑战",
                "Ranked-Challenge",
                ranked.groupTitle,
                # ranked.groupTitle,
                remove_year(ranked.startAt),
                remove_year(ranked.endAt),
            )
            paste_with_a(background, ranked_challenge_card, (10, pos))
            pos += 340
            total_pos += 340

        # 第三排绘制 默认为真格开放
        if ranked_open is not None:
            count_match_data += 1
            ranked = ranked_open.groups[i]
            ranked_challenge_card = get_stage_card(
                ImageInfo(
                    name=ranked.subCards[0]['pic'],
                    url=ranked.subCards[0]['pic'],
                    zh_name=ranked.subCards[0]['subCardTitle'],
                    source_type="对战地图",
                ),
                ImageInfo(
                    name=ranked.subCards[1]['pic'],
                    url=ranked.subCards[1]['pic'],
                    zh_name=ranked.subCards[1]['subCardTitle'],
                    source_type="对战地图",
                ),
                "蛮颓比赛-开放",
                "Ranked-Open",
                # "Ranked-Open",
                ranked.groupTitle,
                remove_year(ranked.startAt),
                remove_year(ranked.endAt),
            )
            paste_with_a(background, ranked_challenge_card, (10, pos))
            pos += 340
            total_pos += 340

        # 第四排绘制 默认为X赛
        if xschedule is not None:
            count_match_data += 1
            xMatch = xschedule.groups[i]
            x_match_card = get_stage_card(
                ImageInfo(
                    name=xMatch.subCards[0]['pic'],
                    url=xMatch.subCards[0]['pic'],
                    zh_name=xMatch.subCards[0]['subCardTitle'],
                    source_type="对战地图",
                ),
                ImageInfo(
                    name=xMatch.subCards[1]['pic'],
                    url=xMatch.subCards[1]['pic'],
                    zh_name=xMatch.subCards[1]['subCardTitle'],
                    source_type="对战地图",
                ),
                "X比赛",
                "X",
                xMatch.groupTitle,
                remove_year(xMatch.startAt),
                remove_year(xMatch.endAt),
            )
            paste_with_a(background, x_match_card, (10, pos))
            pos += 340
            total_pos += 340

        # 取涂地模式的时间，除举办祭典外，都可用
        date_time = time_converter_yd(regular.groups[i].startAt)
        start_time = time_converter_hm(regular.groups[i].startAt)
        end_time = time_converter_hm(regular.groups[i].endAt)
        # 绘制时间表头
        time_head_bg = get_time_head_bg(time_head_bg_size, date_time, start_time, end_time)
        # 贴到大图上
        time_head_bg_pos = (
            (background_size[0] - time_head_bg_size[0]) // 2,
            total_pos - 340 * count_match_data + 10,
        )
        paste_with_a(image_background, time_head_bg, time_head_bg_pos)
        total_pos += time_head_bg_size[1] + 10
        # 将一组图片贴到底图上
        paste_with_a(
            image_background,
            background,
            (0, time_head_bg_pos[1] + time_head_bg_size[1]),
        )
    # 圆角化
    image_background = circle_corner(image_background, radii=16)
    return image_background


def get_stages_image(data):
    """取 对战图片"""
    # 获取数据
    num_list = [0, 1, 2]
    # print(schedule)
    # 绘制图片
    image = get_stages(data, num_list)
    return image


def get_cached_image(data):
    global image_cache
    current_time = time.time()

    try:
        format_data = formatS3JSON(data)
        # 计算 splatoon_data.a 的哈希值作为缓存字典的键
        data_hash = hashlib.sha256(str(format_data[0].groups[0].startAt).encode('utf-8')).hexdigest()
        logger.info(f"data_hash: {data_hash}")
        # 检查缓存是否存在且未过期
        if data_hash in image_cache:
            cached_image, timestamp = image_cache[data_hash]
            logger.info(f"cached_image: {cached_image}, timestamp: {timestamp}, current_time: {current_time}")
            if current_time - timestamp < CACHE_TTL:
                return cached_image

        # 如果缓存过期或不存在，重新生成图片
        img = get_stages_image(format_data)
        b_img = io.BytesIO()
        img.save(b_img, format="PNG")

        # 更新缓存
        image_cache[data_hash] = (b_img, current_time)

        return b_img
    except Exception as e:
        logger.info(f"主接口获取成功：{e}")
        # 如果缓存部分出现异常，直接走正常逻辑
        img = get_stages_image(format_data)
        b_img = io.BytesIO()
        img.save(b_img, format="PNG")
        return b_img

