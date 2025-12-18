# 屏幕设置
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 852
SCREEN_SIZE = (695, 852)
BG_COLOR = (205, 205, 205)

# 敌人飞机的血量属性设置
HP_LIST = [1, 20, 100, 20]

# 飞机大小
PLANE_SIZE = [
    {"width":51, "height":39 },
    {"width":69, "height":89 },
    {"width":165, "height":246 },
    {"width":100, "height":124 },
]

# 爆炸效果计数
PLANE_BOMB_TIME = [5, 8, 14, 8]

PLANE_MAXIMUM_BULLET = [2, 5, 7, 8]
PLANE_MAXIUM_BULLET = PLANE_MAXIMUM_BULLET

# 子弹类型图片
BULLET_TYPE_IMAGES = [
    "bullet1.png",
    "bullet-1.gif",
    "bullet2.png",
    "bullet.png",
]

# 子弹伤害
BULLET_DAMAGE_VALUE = [1, 1, 3, 1]
# 补给设置
SUPPLY_IMAGES = [
    "prop_type_0.png",
    "prop_type_1.png",
]
SUPPLY_SIZE = [
    {"width":58, "height":88 },
    {"width":60, "height":103 },
]
SUPPLT_SIZE = SUPPLY_SIZE

ENEMY0_MAXIMUM = 8
ENEMY1_MAXIMUM = 1
ENEMY2_MAXIMUM = 1
ENEMY0_MAXIUM = ENEMY0_MAXIMUM
ENEMY1_MAXIUM = ENEMY1_MAXIMUM
ENEMY2_MAXIUM = ENEMY2_MAXIMUM

# 难度配置字典
# key: 难度级别 (0:简单, 1:中等, 2:困难)
# value: 包含各项游戏参数的字典
DIFFICULTY_LEVELS = {
    0: { # 简单模式
        "enemy_speed": {0: 3, 1: 2, 2: 3}, # 敌机速度降低
        "enemy_limits": [4, 1, 1], # 敌机数量减少
        "spawn_rate_0": [20], # Enemy0 出现概率降低 (只保留一个触发点)
        "boss1_interval": (30, 40), # Enemy1 出现间隔变长
        "boss2_interval": (120, 150) # Enemy2 出现间隔变长
    },
    1: { # 中等模式 (保持原版数值)
        "enemy_speed": {0: 4, 1: 3, 2: 5},
        "enemy_limits": [8, 1, 1],
        "spawn_rate_0": [20, 40],
        "boss1_interval": (18, 28),
        "boss2_interval": (80, 100)
    },
    2: { # 困难模式
        "enemy_speed": {0: 6, 1: 5, 2: 7}, # 敌机速度加快
        "enemy_limits": [12, 2, 1], # 敌机数量增加
        "spawn_rate_0": [10, 20, 40, 50], # Enemy0 出现概率增加
        "boss1_interval": (10, 20), # Enemy1 出现间隔变短
        "boss2_interval": (50, 70) # Enemy2 出现间隔变短
    }
}

# 当前难度设置 (默认为中等，会在游戏开始时被修改)
CURRENT_DIFFICULTY = DIFFICULTY_LEVELS[1]
