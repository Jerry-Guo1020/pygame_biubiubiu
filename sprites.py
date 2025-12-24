# 导入pygame库，用于游戏开发
import pygame
# 导入random库，用于生成随机数
import random
# 从pygame.locals导入所有常量
from pygame.locals import *
# 导入配置文件
import config

# 游戏对象的基础类，包含所有游戏对象的共同属性
class Base(object):
    def __init__(self, screen, x, y, image_name):
        # 设置对象的x坐标
        self.x = x
        # 设置对象的y坐标
        self.y = y
        # 设置对象绘制的屏幕
        self.screen = screen
        
        # 尝试加载指定的图片文件
        try:
            self.image = pygame.image.load(image_name)
        except Exception:
            # 如果加载失败，打印错误信息并创建一个10x10的默认表面
            print(f"这个照片的读取出现了错误：{image_name}")
            self.image = pygame.Surface((10, 10))


# 飞机类的基础类，继承自Base类
class BasePlane(Base):
    """飞机的基本类"""
    def __init__(self, plane_type, screen, x, y, image_name, picture_num, HP_temp):
        # 调用父类的初始化方法
        super().__init__(screen, x, y, image_name)
        
        """战斗相关"""
        # 子弹列表：用于存储这架飞机飞射出去的所有"子弹对象"
        self.bullet_list = [] 
        # 飞机类型的索引：用来区分是hi哪一种飞机
        self.plane_type = plane_type 
        # 飞机当前血量
        self.HP = HP_temp 
        # 记录已经发射的数量,默认开始为0
        self.fire_bullet_count = 0        
        
        """状态标记"""
        # 标记对象是否存活
        self.active = True 
        # 是否开启爆炸状态
        self.hitted = False
        # 标记是否已计算过分数
        self.scored = False
        
        """爆炸动画的相关基本配置"""
        # 存储爆炸效果的图片的列表 
        self.bomb_picture_list = [] 
        # 爆炸图片数量
        self.bomb_picture_num = picture_num
        # 动画延时计数器：用来控制爆炸动画的播放速度。 
        self.last_update_time = pygame.time.get_ticks()
        # 设置动画速度: 每 100 毫秒就换一张图
        self.frame_rate = 100
        # 当前动画帧索引：记录当前正在播放到第几张的爆炸图
        self.image_index = 0
      
         
        
    def create_images(self, bomb_picture_name):
        # 循环创建爆炸动画的图片列表
        for i in range(1, self.bomb_picture_num + 1):
            # 加载爆炸动画图片并添加到列表中
            self.bomb_picture_list.append(pygame.image.load("./images/" + bomb_picture_name + str(i) + ".png"))
            
            
    def update_and_draw(self):
        # 第一个版本的写法
        # """显示并更新飞机状态,爆炸动画逻辑"""
        # # 首先判断飞机是否已经
        # # 1\被击中了 hitted
        # # 2\被击中之后爆炸的每一帧的照片是否全部放完
        # # 3\血量是否大于小于0
        # if self.hitted and self.image_index < self.bomb_picture_num and self.HP <= 0:
        #     # 如果满足,则:
        #     # 1\在当前位置开始放爆炸的过程帧的所有照片(self.x, self.y)
        #     # 2\通过 self.image_index 来判断当前的爆炸过程,一般是从0开始
        #     # 3\然后再通过 bomb_picture_list 列表,这个列表存放的是爆炸全过程的照片,从0开始是第一张,通过列表的顺序代表了照片的爆炸的过程
        #     self.screen.blit(self.bomb_picture_list[self.image_index], (self.x, self.y))
            
        #     # 重要知识点!!!!
        #     self.picture_count += 1
        #     if self.picture_count == config.PLANE_BOMB_TIME[self.plane_type]:
        #         self.picture_count = 0
        #         self.image_index += 1
        
        
        
        
        # 第二个版本的写法
        now = pygame.time.get_ticks()
        
        if (self.hitted and self.HP <=0) or self.HP <= 0:
            # 确保被击中标志被设置
            if not self.hitted:
                self.hitted = True
            if now - self.last_update_time > self.frame_rate:
                self.last_update_time = now
                self.image_index += 1
                
                if self.image_index >= self.bomb_picture_num:
                    self.active = False
                    self.image_index = 0  # 重置图像索引
                    return  # 不再绘制
            
            if self.image_index < self.bomb_picture_num:
                self.screen.blit(self.bomb_picture_list[self.image_index], (self.x, self.y))
        
        # 正常飞行
        else:
            self.screen.blit(self.image, (self.x, self.y))
        
        # 越界判断:当飞出屏幕下方
        if self.y > 860:
            self.active = False
            
        # 删除越界的子弹
        self.clean_bullets()
    
    # 清理并更新子弹状态
    def clean_bullets(self):
        # 遍历当前飞机发出所有子弹的列表
        for bullet in self.bullet_list[:]:
            # 首先先在屏幕画出子弹
            bullet.display()
            # 改变子弹的位置 
            bullet.move()
            # 判断子弹是否超出边界
            if bullet.judge():
                # 如果超出边界则从列表中移除
                self.bullet_list.remove(bullet)
    
    def isHitted(self, other_plane, width, height):
        """碰撞检测:判断我方有没有被敌机的子弹打中"""
        # 如果当前飞机不活跃或血量为0，返回False
        if not self.active or self.HP <= 0:
            return False
            
        # 初始化命中标志
        is_hit = False
        
        # 检测主子弹
        for bullet in other_plane.bullet_list[:]:
            # 检查子弹是否在当前飞机的碰撞区域内
            if (bullet.x > self.x + 0.05*width and bullet.x < self.x + 0.95*width and 
                bullet.y + 0.1*height > self.y and bullet.y < self.y + 0.8*height):
                # 减少当前飞机血量
                self.HP -= bullet.damage_value
                # 从敌机子弹列表中移除该子弹
                other_plane.bullet_list.remove(bullet)
                # 设置被击中标志
                self.hitted = True
                # 设置命中标志
                is_hit = True
        # 如果是Hero且开启了三管炮，检测额外炮管
        if other_plane.plane_type == 3 and hasattr(other_plane, 'barrel_2'):
            # 检测额外炮管的子弹
            for barrel in [other_plane.barrel_2, other_plane.barrel_3]:
                for bullet in barrel[:]:
                     # 检查额外炮管子弹是否在当前飞机的碰撞区域内
                     if (bullet.x > self.x + 0.05*width and bullet.x < self.x + 0.95*width and 
                        bullet.y + 0.1*height > self.y and bullet.y < self.y + 0.8*height):
                        # 减少当前飞机血量
                        self.HP -= bullet.damage_value
                        # 从额外炮管子弹列表中移除该子弹
                        barrel.remove(bullet)
                        # 设置被击中标志
                        self.hitted = True
                        # 设置命中标志
                        is_hit = True
        return is_hit
    
    def fire(self, bullet_maximun):
            # 如果飞机血量大于0
            if self.HP > 0:
                # 生成1-60之间的随机数
                random_num = random.randint(1, 60)
                # 如果随机数为10或45且子弹数量未达到最大值
                if (random_num == 10 or random_num == 45) and len(self.bullet_list) < bullet_maximun:
                    # 创建敌机子弹并添加到子弹列表
                    self.bullet_list.append(EnemyBullet(self.screen, self.x, self.y, self))
                    # 增加发射子弹计数
                    self.fire_bullet_count += 1
                    
                    
# 英雄飞机类，继承自BasePlane
class HeroPlane(BasePlane):
    def __init__(self, screen):
        # 调用父类初始化方法，参数：飞机类型(3-英雄飞机), 屏幕, x坐标, y坐标, 图片路径, 爆炸图片数量, 血量
        super().__init__(3, screen, 210, 728, "./images/hero1.png", 4, config.HP_LIST[3])
        # 创建英雄飞机爆炸动画图片
        self.create_images("hero_blowup_n")
        # 存储按下的按键
        self.key_down_list = []
        # 存储空格键按下的状态
        self.space_key_list = []
        # 是否开启三管炮模式
        self.is_three_bullet = False
        # 第二个炮管的子弹列表
        self.barrel_2 = []
        # 第三个炮管的子弹列表
        self.barrel_3 = []
        # 三管炮弹药数量
        self.three_bullet_stock = 50
        # 发射子弹音效对象（由Main类赋值）
        self.play_fire_music = None # Main会赋值给它

    # 移动逻辑保持不变
    # 向左移动
    def move_left(self): self.x -= 7
    # 向右移动
    def move_right(self): self.x += 7
    # 向上移动
    def move_up(self): self.y -= 6
    # 向下移动
    def move_down(self): self.y += 6
    # 左上移动
    def move_left_and_up(self): self.x -= 5; self.y -= 6
    # 右上移动
    def move_right_and_up(self): self.x += 5; self.y -= 6
    # 左下移动
    def move_left_and_down(self): self.x -= 5; self.y += 6
    # 右下移动
    def move_right_and_down(self): self.x += 5; self.y += 6

    def move_limit(self):
        # 限制飞机左右边界
        if self.x < 0: self.x = -2
        elif self.x + 100 > 480: self.x = 380
        # 限制飞机上下边界
        if self.y > 728: self.y = 728
        elif self.y < 350: self.y += 6

    # 按键按下处理
    def key_down(self, key): self.key_down_list.append(key)
    # 按键释放处理
    def key_up(self, key): 
        # 如果按键在按下列表中则移除
        if key in self.key_down_list: self.key_down_list.remove(key)

    def press_move(self):
        # 简化原有的按键逻辑
        # 如果没有按键按下则返回
        if not self.key_down_list: return
        
        # 将按键列表转换为集合，去重
        keys = set(self.key_down_list)
        # 根据按下的键组合执行相应的移动
        if K_LEFT in keys and K_UP in keys: self.move_left_and_up()
        elif K_RIGHT in keys and K_UP in keys: self.move_right_and_up()
        elif K_LEFT in keys and K_DOWN in keys: self.move_left_and_down()
        elif K_RIGHT in keys and K_DOWN in keys: self.move_right_and_down()
        elif K_LEFT in keys: self.move_left()
        elif K_RIGHT in keys: self.move_right()
        elif K_UP in keys: self.move_up()
        elif K_DOWN in keys: self.move_down()

    def bomb(self):
        # 设置被击中标志
        self.hitted = True
        # 将血量设为0，触发爆炸动画
        self.HP = 0

    # 空格键按下处理
    def space_key_down(self, key): self.space_key_list.append(key)
    # 空格键释放处理
    def space_key_up(self, key): 
        # 如果空格键列表不为空则移除第一个元素
        if self.space_key_list: self.space_key_list.pop(0)

    def press_fire(self):
        # 如果没有子弹且按下了空格键
        if not self.bullet_list and self.space_key_list:
            self.fire()
        # 如果按下了空格键且有子弹
        elif self.space_key_list and self.bullet_list:
            # 如果最后一个子弹的位置在飞机上方一定距离
            if self.bullet_list[-1].y < self.y - 74:
                self.fire()

    def fire(self):
        # 如果有音效对象则播放发射音效
        if self.play_fire_music: self.play_fire_music.play()
        
        # 如果没有开启三管炮模式
        if not self.is_three_bullet:
            # 如果子弹数量未达到最大值
            if len(self.bullet_list) < config.PLANE_MAXIMUM_BULLET[self.plane_type]:
                # 创建普通子弹
                self.bullet_list.append(Bullet(self.screen, self.x+40, self.y-14, self))
        else:
            # 创建主炮子弹
            self.bullet_list.append(Bullet(self.screen, self.x+40, self.y-14, self))
            # 创建第二炮管子弹
            self.barrel_2.append(Bullet(self.screen, self.x+5, self.y+20, self))
            # 创建第三炮管子弹
            self.barrel_3.append(Bullet(self.screen, self.x+75, self.y+20, self))
            # 减少三管炮弹药数量
            self.three_bullet_stock -= 1
            # 如果弹药用完
            if not self.three_bullet_stock:
                # 关闭三管炮模式
                self.is_three_bullet = False

    def clean_bullets(self):
        # 调用父类的清理子弹方法
        super().clean_bullets()
        # 处理额外炮管
        for barrel in [self.barrel_2, self.barrel_3]:
            # 遍历每个炮管的子弹
            for bullet in barrel[:]:
                # 显示子弹
                bullet.display()
                # 移动子弹
                bullet.move()
                # 判断子弹是否超出边界
                if bullet.judge():
                    # 如果超出边界则从炮管列表中移除
                    barrel.remove(bullet)

    def supply_hitted(self, supply):
        """判断是否吃到补给"""
        # 如果补给不存在或英雄血量为0，返回False
        if not supply or not self.HP: return False
        
        # 获取补给的宽度和高度
        s_w = config.SUPPLY_SIZE[supply.supply_type]["width"]
        s_h = config.SUPPLY_SIZE[supply.supply_type]["height"]
        
        # 计算补给的碰撞区域
        s_left = supply.x + s_w * 0.15  # 左边界
        s_right = supply.x + s_w * 0.85  # 右边界
        s_top = supply.y + s_h * 0.4     # 上边界
        s_bottom = supply.y + s_h * 0.9  # 下边界
        
        # 英雄的判定范围
        h_w = config.PLANE_SIZE[3]["width"]
        h_h = config.PLANE_SIZE[3]["height"]
        
        # 检查补给是否在英雄的碰撞区域内
        if (s_left > self.x + 0.05*h_w and s_right < self.x + 0.95*h_w and 
            s_top < self.y + 0.95*h_h and s_bottom > self.y + 0.1*h_h):
            return True
        return False

# 敌机0类（小型敌机），继承自BasePlane
class Enemy0Plane(BasePlane):
    def __init__(self, screen):
        # 调用父类初始化方法，参数：飞机类型(0-小型敌机), 屏幕, 随机x坐标, 随机y坐标, 图片路径, 爆炸图片数量, 血量
        super().__init__(0, screen, random.randint(12, 418), random.randint(-50, -40), 
                         "./images/enemy0.png", 4, config.HP_LIST[0])
        # 创建敌机0爆炸动画图片
        self.create_images("enemy0_down")
    # 移动方法：向下移动
    def move(self): self.y += config.CURRENT_DIFFICULTY["enemy_speed"][0]

# 敌机1类（中型敌机），继承自BasePlane
class Enemy1Plane(BasePlane):
    def __init__(self, screen):
        # 调用父类初始化方法，参数：飞机类型(1-中型敌机), 屏幕, x坐标, y坐标, 图片路径, 爆炸图片数量, 血量
        super().__init__(1, screen, 205, -90, "./images/enemy1.png", 4, config.HP_LIST[1])
        # 创建敌机1爆炸动画图片
        self.create_images("enemy1_down")
        # 移动方向，默认向右
        self.direction = "right"
        # 随机确定y轴移动目标
        self.num_y = random.randint(15, 400)
    
    def move(self):
        # 获取当前难度下的移动速度
        speed = config.CURRENT_DIFFICULTY["enemy_speed"][1]
        # 根据方向移动
        if self.direction == "right": self.x += speed
        elif self.direction == "left": self.x -= speed
        
        # 边界检测，到达边界时改变方向
        if self.x + 70 > 480: self.direction = "left"
        elif self.x < 0: self.direction = "right"
        
        # y轴移动逻辑
        if self.y < self.num_y: self.y += speed
        elif self.fire_bullet_count > 10: self.y += (speed + 1)

# 敌机2类（大型敌机/BOSS），继承自BasePlane
class Enemy2Plane(BasePlane):
    def __init__(self, screen):
        # 调用父类初始化方法，参数：飞机类型(2-大型敌机), 屏幕, x坐标, y坐标, 图片路径, 爆炸图片数量, 血量
        super().__init__(2, screen, 158, -246, "./images/enemy2.png", 5, config.HP_LIST[2])
        # 创建敌机2爆炸动画图片
        self.create_images("enemy2_down")
        # 移动方向，默认向右
        self.direction = "right"

    def move(self):
        # 获取当前难度下的移动速度
        speed = config.CURRENT_DIFFICULTY["enemy_speed"][2]
        # 根据方向移动
        if self.direction == "right": self.x += speed
        elif self.direction == "left": self.x -= speed
        
        # 边界检测，到达边界时改变方向
        if self.x + 165 > 480: self.direction = "left"
        elif self.x < 0: self.direction = "right"
        
        # y轴移动逻辑
        if self.y < 0: self.y += speed
        elif self.fire_bullet_count > 25: self.y += (speed - 2)

# 子弹基础类，继承自Base类
class BaseBullet(Base):
    def __init__(self, screen, x, y, image_name, plane=None):
        # 调用父类初始化方法
        super().__init__(screen, x, y, image_name)
        # 如果传入了飞机对象，设置子弹伤害值
        if plane:
            self.damage_value = config.BULLET_DAMAGE_VALUE[plane.plane_type]
    # 显示子弹
    def display(self): self.screen.blit(self.image, (self.x, self.y))

# 英雄子弹类，继承自BaseBullet
class Bullet(BaseBullet):
    def __init__(self, screen, x, y, plane):
        # 调用父类初始化方法，参数：屏幕, x坐标, y坐标, 子弹图片路径, 飞机对象
        super().__init__(screen, x, y, "./images/"+config.BULLET_TYPE_IMAGES[plane.plane_type], plane)
    # 子弹移动方法（向上移动）
    def move(self): self.y -= 16
    # 判断子弹是否超出边界
    def judge(self): return self.y < 0

# 敌机子弹类，继承自BaseBullet
class EnemyBullet(BaseBullet):
    def __init__(self, screen, x, y, plane):
        # 获取飞机的宽度和高度
        p_w = config.PLANE_SIZE[plane.plane_type]["width"]
        p_h = config.PLANE_SIZE[plane.plane_type]["height"]
        # 调用父类初始化方法，参数：屏幕, x坐标(飞机中心), y坐标(飞机底部), 子弹图片路径, 飞机对象
        super().__init__(screen, x + p_w/2, y + p_h/2, 
                         "./images/"+config.BULLET_TYPE_IMAGES[plane.plane_type], plane)
    # 子弹移动方法（向下移动）
    def move(self): self.y += 7
    # 判断子弹是否超出边界
    def judge(self): return self.y > 852

# 补给类，继承自BaseBullet
class Supply(BaseBullet):
    def __init__(self, screen, x, y, s_type, speed, s_hp):
        # 调用父类初始化方法，参数：屏幕, x坐标, y坐标, 补给图片路径, 飞机对象(None)
        super().__init__(screen, x, y, "./images/"+config.SUPPLY_IMAGES[s_type], None)
        # 补给移动速度
        self.speed = speed
        # 补给对血量的影响值
        self.supply_HP = s_hp
        # 补给类型（0-血量补给，1-子弹补给）
        self.supply_type = s_type
    # 补给移动方法
    def move(self): self.y += self.speed
    # 判断补给是否超出边界
    def judge(self): return self.y > 855
        
