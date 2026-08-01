import os


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# Deployment-specific settings are deliberately kept outside the repository.
RTSP_URL = required_env("RTSP_URL")
SNAPSHOT_URL = required_env("SNAPSHOT_URL").rstrip("/")

# Bark 推送 Key
# 支持多个设备
BARK_KEYS = [
    key.strip() for key in required_env("BARK_KEYS").split(",") if key.strip()
]
# =====================
# 推送配置
# =====================
PUSH_SLOTS = {"4", "5"}   # 只对这些车位推送

#识别类别0:person  1:bicycle  2:car  3:motorcycle  4:airplane  5:bus  6:train  7:truck  8:boat  9:traffic_light
#10:fire_hydrant  11:stop_sign  12:parking_meter  13:bench  14:bird  15:cat  16:dog  17:horse  18:sheep  19:cow
#20:elephant  21:bear  22:zebra  23:giraffe  24:backpack  25:umbrella  26:handbag  27:tie  28:suitcase  29:frisbee
#30:skis  31:snowboard  32:sports_ball  33:kite  34:baseball_bat  35:baseball_glove  36:skateboard  37:surfboard  38:tennis_racket  39:bottle
#40:wine_glass  41:cup  42:fork  43:knife  44:spoon  45:bowl  46:banana  47:apple  48:sandwich  49:orange
#50:broccoli  51:carrot  52:hot_dog  53:pizza  54:donut  55:cake  56:chair  57:couch  58:potted_plant  59:bed
#60:dining_table  61:toilet  62:tv  63:laptop  64:mouse  65:remote  66:keyboard  67:cell_phone  68:microwave  69:oven
#70:toaster  71:sink  72:refrigerator  73:book  74:clock  75:vase  76:scissors  77:teddy_bear  78:hair_drier  79:toothbrush
DETECT_CLASSES = None

# 抽帧间隔（秒）
FRAME_INTERVAL = 4

# 状态机阈值
EMPTY_CONFIRM = 10   # 连续空
OCCUPY_CONFIRM = 10  # 连续占用
# =====================
# 参数配置（昼夜判断）
# =====================
DAY_conf = 0.25
NIGHT_conf = 0.15
NIGHT_BRIGHTNESS_THRESHOLD = 100

# 车位 ROI + 中文名称
PARKING_SLOTS = {

    "1": {
        "name": "左侧绿化带横",
        "polygon": [(441, 172), (636, 163), (588, 295), (420, 301)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },

    "2": {
        "name": "左3",
        "polygon": [(612, 228), (732, 228), (693, 501), (555, 498)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },

    "3": {
        "name": "左2",
        "polygon": [(741, 228), (858, 222), (834, 506), (708, 504)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },

    "4": {
        "name": "左1",
        "polygon": [(867, 228), (987, 225), (987, 504), (843, 506)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },

    "5": {
        "name": "右1",
        "polygon": [(1077, 214), (1209, 203), (1233, 506), (1065, 509)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },

    "6": {
        "name": "右2",
        "polygon": [(1224, 203), (1380, 188), (1413, 501), (1242, 509)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },

    "7": {
        "name": "右3",
        "polygon": [(1392, 191), (1539, 174), (1590, 484), (1422, 498)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },

    "8": {
        "name": "右侧横",
        "polygon": [(1071, 73), (1497, 42), (1518, 163), (1080, 200)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },

    "9": {
        "name": "左侧横",
        "polygon": [(645, 96), (1050, 73), (1047, 217), (645, 217)],
        "state": "unknown",
        "empty": 0,
        "occupy": 0,
    },
}