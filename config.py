# 屏幕设置
SCREEN_WIDTH = 480              # 屏幕宽度（已定义但未使用）
SCREEN_HEIGHT = 900             # 屏幕高度（已定义但未使用）
SCREEN_SIZE = (695, 890)        # 实际屏幕尺寸（宽695，高890）
BG_COLOR = (205, 205, 205)      # 背景色（灰色）

# 敌人飞机的血量属性设置
# 索引0:小型敌机血量, 索引1:中型敌机血量, 索引2:大型敌机血量, 索引3:英雄飞机血量
HP_LIST = [1, 20, 100, 20]

# 飞机大小
# 索引0:小型敌机尺寸, 索引1:中型敌机尺寸, 索引2:大型敌机尺寸, 索引3:英雄飞机尺寸
PLANE_SIZE = [
    {"width":51, "height":39 },   # 小型敌机（enemy0）尺寸
    {"width":69, "height":89 },   # 中型敌机（enemy1）尺寸
    {"width":165, "height":246 }, # 大型敌机（enemy2）尺寸
    {"width":100, "height":124 }, # 英雄飞机尺寸
]

# 爆炸效果计数
# 各类型飞机爆炸动画的播放速度，数值越小动画播放越快
# 索引0:小型敌机, 索引1:中型敌机, 索引2:大型敌机, 索引3:英雄飞机
PLANE_BOMB_TIME = [5, 8, 14, 8]

PLANE_MAXIMUM_BULLET = [2, 5, 7, 8]  # 各类型飞机最大子弹数量：小型敌机2发，中型敌机5发，大型敌机7发，英雄飞机8发
PLANE_MAXIUM_BULLET = PLANE_MAXIMUM_BULLET  # 拼写错误的变量，指向正确的子弹数量列表

# 子弹类型图片
# 索引0:小型敌机子弹, 索引1:中型敌机子弹, 索引2:大型敌机子弹, 索引3:英雄飞机子弹
BULLET_TYPE_IMAGES = [
    "bullet1.png",      # 小型敌机子弹图片
    "bullet-1.gif",     # 中型敌机子弹图片
    "bullet2.png",      # 大型敌机子弹图片
    "bullet.png",       # 英雄飞机子弹图片
]

# 子弹伤害
# 各类型子弹的伤害值：小型敌机子弹1点，中型敌机子弹1点，大型敌机子弹3点，英雄飞机子弹1点
BULLET_DAMAGE_VALUE = [1, 1, 3, 1]
# 补给设置
# 补给物品图片：索引0为血量补给，索引1为子弹补给
SUPPLY_IMAGES = [
    "prop_type_0.png",    # 血量补给图片
    "prop_type_1.png",    # 子弹补给图片
]
# 补给物品尺寸：索引0为血量补给尺寸，索引1为子弹补给尺寸
SUPPLY_SIZE = [
    {"width":58, "height":88 },   # 血量补给尺寸
    {"width":60, "height":103 },  # 子弹补给尺寸
]
SUPPLT_SIZE = SUPPLY_SIZE   # 拼写错误的变量，指向正确的补给尺寸列表

ENEMY0_MAXIMUM = 8    # 小型敌机最大数量
ENEMY1_MAXIMUM = 1    # 中型敌机最大数量
ENEMY2_MAXIMUM = 1    # 大型敌机最大数量
ENEMY0_MAXIUM = ENEMY0_MAXIMUM  # 拼写错误的变量，指向小型敌机最大数量
ENEMY1_MAXIUM = ENEMY1_MAXIMUM  # 拼写错误的变量，指向中型敌机最大数量
ENEMY2_MAXIUM = ENEMY2_MAXIMUM  # 拼写错误的变量，指向大型敌机最大数量

# 难度配置字典
# key: 难度级别 (0:简单, 1:中等, 2:困难)
# value: 包含各项游戏参数的字典
DIFFICULTY_LEVELS = {
    0: { # 简单模式
        "enemy_speed": {0: 3, 1: 2, 2: 3}, # 敌机速度降低：小型敌机3，中型敌机2，大型敌机3
        "enemy_limits": [4, 1, 1], # 敌机数量减少：小型敌机4个，中型敌机1个，大型敌机1个
        "spawn_rate_0": [20], # Enemy0 出现概率降低 (只保留一个触发点)
        "boss1_interval": (30, 40), # Enemy1 出现间隔变长（30-40之间随机）
        "boss2_interval": (120, 150) # Enemy2 出现间隔变长（120-150之间随机）
    },
    1: { # 中等模式 (保持原版数值)
        "enemy_speed": {0: 4, 1: 3, 2: 5},  # 敌机速度：小型敌机4，中型敌机3，大型敌机5
        "enemy_limits": [8, 1, 1],           # 敌机数量：小型敌机8个，中型敌机1个，大型敌机1个
        "spawn_rate_0": [20, 40],           # Enemy0 出现概率（20或40时出现）
        "boss1_interval": (18, 28),         # Enemy1 出现间隔（18-28之间随机）
        "boss2_interval": (80, 100)         # Enemy2 出现间隔（80-100之间随机）
    },
    2: { # 困难模式
        "enemy_speed": {0: 6, 1: 5, 2: 7}, # 敌机速度加快：小型敌机6，中型敌机5，大型敌机7
        "enemy_limits": [12, 2, 1], # 敌机数量增加：小型敌机12个，中型敌机2个，大型敌机1个
        "spawn_rate_0": [10, 20, 40, 50], # Enemy0 出现概率增加（10,20,40,50时出现）
        "boss1_interval": (10, 20), # Enemy1 出现间隔变短（10-20之间随机）
        "boss2_interval": (50, 70) # Enemy2 出现间隔变短（50-70之间随机）
    }
}

# 当前难度设置 (默认为中等，会在游戏开始时被修改)
CURRENT_DIFFICULTY = DIFFICULTY_LEVELS[1]  # 默认设置为中等难度
