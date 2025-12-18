import pygame
import random
from pygame.locals import *
import config

# --- 基础类 ---
class Base(object):
    def __init__(self, screen, x, y, image_name):
        self.x = x
        self.y = y
        self.screen = screen
        try:
            self.image = pygame.image.load(image_name)
        except Exception:
            print(f"图片读取错误：{image_name}")
            self.image = pygame.Surface((10, 10))

# --- 飞机基类 (核心逻辑修复) ---
class BasePlane(Base):
    """飞机的基本类"""
    def __init__(self, plane_type, screen, x, y, image_name, picture_num, HP_temp):
        super().__init__(screen, x, y, image_name)
        
        # 战斗属性
        self.bullet_list = [] 
        self.plane_type = plane_type 
        self.HP = HP_temp 
        self.fire_bullet_count = 0        
        
        # 状态标记
        self.active = True    # 存活状态
        self.hitted = False   # 是否被击中
        self.scored = False   # 是否已加分
        
        # 爆炸动画配置
        self.bomb_picture_list = [] 
        self.bomb_picture_num = picture_num
        self.last_update_time = pygame.time.get_ticks()
        self.frame_rate = 100 # 动画速度
        self.image_index = 0
             
    def create_images(self, bomb_picture_name):
        for i in range(1, self.bomb_picture_num + 1):
            try:
                img = pygame.image.load("./images/" + bomb_picture_name + str(i) + ".png")
                self.bomb_picture_list.append(img)
            except Exception as e:
                print(f"爆炸图片缺失: {bomb_picture_name}{i}.png")

    def update_and_draw(self):
        """【核心修复】：显示并更新状态"""
        
        # 1. 如果已经死亡（active=False），直接不再绘制，彻底消失
        if not self.active:
            return

        now = pygame.time.get_ticks()

        # 2. 爆炸状态处理 (被击中 且 血量<=0)
        if self.hitted and self.HP <= 0:
            # 播放动画
            if self.image_index < self.bomb_picture_num:
                # 绘制当前爆炸帧
                if self.image_index < len(self.bomb_picture_list):
                    self.screen.blit(self.bomb_picture_list[self.image_index], (self.x, self.y))
                
                # 切换下一帧
                if now - self.last_update_time > self.frame_rate:
                    self.last_update_time = now
                    self.image_index += 1
            
            # 动画播放完毕
            else:
                self.active = False # 标记为彻底死亡，等待 Main 移除
                return # 立即结束

        # 3. 正常存活状态
        else:
            self.screen.blit(self.image, (self.x, self.y))

        # 4. 越界检查
        if self.y > 860:
            self.active = False

        # 5. 更新子弹
        self.clean_bullets()

    def clean_bullets(self):
        for bullet in self.bullet_list[:]:
            bullet.display()
            bullet.move()
            if bullet.judge():
                self.bullet_list.remove(bullet)

    def isHitted(self, other_plane, width, height):
        if not self.active or self.HP <= 0:
            return False
        
        is_hit = False
        # 检测主子弹
        for bullet in other_plane.bullet_list[:]:
            if (bullet.x > self.x + 0.05*width and bullet.x < self.x + 0.95*width and 
                bullet.y + 0.1*height > self.y and bullet.y < self.y + 0.8*height):
                self.HP -= bullet.damage_value
                other_plane.bullet_list.remove(bullet)
                self.hitted = True
                is_hit = True

        # 检测额外炮管 (如果是Hero)
        if other_plane.plane_type == 3 and hasattr(other_plane, 'barrel_2'):
            for barrel in [other_plane.barrel_2, other_plane.barrel_3]:
                for bullet in barrel[:]:
                     if (bullet.x > self.x + 0.05*width and bullet.x < self.x + 0.95*width and 
                        bullet.y + 0.1*height > self.y and bullet.y < self.y + 0.8*height):
                        self.HP -= bullet.damage_value
                        barrel.remove(bullet)
                        self.hitted = True
                        is_hit = True
        return is_hit

    def fire(self, bullet_maximun):
        if self.HP > 0:
            random_num = random.randint(1, 60)
            if (random_num == 10 or random_num == 45) and len(self.bullet_list) < bullet_maximun:
                self.bullet_list.append(EnemyBullet(self.screen, self.x, self.y, self))
                self.fire_bullet_count += 1

# --- 英雄飞机类 ---
class HeroPlane(BasePlane):
    def __init__(self, screen):
        super().__init__(3, screen, 210, 728, "./images/hero1.png", 4, config.HP_LIST[3])
        self.create_images("hero_blowup_n")
        self.key_down_list = []
        self.space_key_list = []
        self.is_three_bullet = False
        self.barrel_2 = []
        self.barrel_3 = []
        self.three_bullet_stock = 50
        self.play_fire_music = None 

    # 移动方法
    def move_left(self): self.x -= 7
    def move_right(self): self.x += 7
    def move_up(self): self.y -= 6
    def move_down(self): self.y += 6
    def move_left_and_up(self): self.x -= 5; self.y -= 6
    def move_right_and_up(self): self.x += 5; self.y -= 6
    def move_left_and_down(self): self.x -= 5; self.y += 6
    def move_right_and_down(self): self.x += 5; self.y += 6

    def move_limit(self):
        if self.x < 0: self.x = -2
        elif self.x + 100 > 480: self.x = 380
        if self.y > 728: self.y = 728
        elif self.y < 350: self.y += 6

    def key_down(self, key): self.key_down_list.append(key)
    def key_up(self, key): 
        if key in self.key_down_list: self.key_down_list.remove(key)

    def press_move(self):
        if not self.key_down_list: return
        keys = set(self.key_down_list)
        if K_LEFT in keys and K_UP in keys: self.move_left_and_up()
        elif K_RIGHT in keys and K_UP in keys: self.move_right_and_up()
        elif K_LEFT in keys and K_DOWN in keys: self.move_left_and_down()
        elif K_RIGHT in keys and K_DOWN in keys: self.move_right_and_down()
        elif K_LEFT in keys: self.move_left()
        elif K_RIGHT in keys: self.move_right()
        elif K_UP in keys: self.move_up()
        elif K_DOWN in keys: self.move_down()

    def bomb(self):
        self.hitted = True
        self.HP = 0

    def space_key_down(self, key): self.space_key_list.append(key)
    def space_key_up(self, key): 
        if self.space_key_list: self.space_key_list.pop(0)

    def press_fire(self):
        if not self.bullet_list and self.space_key_list:
            self.fire()
        elif self.space_key_list and self.bullet_list:
            if self.bullet_list[-1].y < self.y - 74:
                self.fire()

    def fire(self):
        if self.play_fire_music: self.play_fire_music.play()
        if not self.is_three_bullet:
            if len(self.bullet_list) < config.PLANE_MAXIMUM_BULLET[self.plane_type]:
                self.bullet_list.append(Bullet(self.screen, self.x+40, self.y-14, self))
        else:
            self.bullet_list.append(Bullet(self.screen, self.x+40, self.y-14, self))
            self.barrel_2.append(Bullet(self.screen, self.x+5, self.y+20, self))
            self.barrel_3.append(Bullet(self.screen, self.x+75, self.y+20, self))
            self.three_bullet_stock -= 1
            if not self.three_bullet_stock:
                self.is_three_bullet = False

    def clean_bullets(self):
        super().clean_bullets()
        for barrel in [self.barrel_2, self.barrel_3]:
            for bullet in barrel[:]:
                bullet.display()
                bullet.move()
                if bullet.judge():
                    barrel.remove(bullet)

    def supply_hitted(self, supply):
        if not supply or not self.HP: return False
        s_w = config.SUPPLY_SIZE[supply.supply_type]["width"]
        s_h = config.SUPPLY_SIZE[supply.supply_type]["height"]
        s_left = supply.x + s_w * 0.15
        s_right = supply.x + s_w * 0.85
        s_top = supply.y + s_h * 0.4
        s_bottom = supply.y + s_h * 0.9
        h_w = config.PLANE_SIZE[3]["width"]
        h_h = config.PLANE_SIZE[3]["height"]
        if (s_left > self.x + 0.05*h_w and s_right < self.x + 0.95*h_w and 
            s_top < self.y + 0.95*h_h and s_bottom > self.y + 0.1*h_h):
            return True
        return False

# --- 敌机类 ---
class Enemy0Plane(BasePlane):
    def __init__(self, screen):
        super().__init__(0, screen, random.randint(12, 418), random.randint(-50, -40), 
                         "./images/enemy0.png", 4, config.HP_LIST[0])
        self.create_images("enemy0_down")
    def move(self): self.y += config.CURRENT_DIFFICULTY["enemy_speed"][0]

class Enemy1Plane(BasePlane):
    def __init__(self, screen):
        super().__init__(1, screen, 205, -90, "./images/enemy1.png", 4, config.HP_LIST[1])
        self.create_images("enemy1_down")
        self.direction = "right"
        self.num_y = random.randint(15, 400)
    
    def move(self):
        speed = config.CURRENT_DIFFICULTY["enemy_speed"][1]
        if self.direction == "right": self.x += speed
        elif self.direction == "left": self.x -= speed
        if self.x + 70 > 480: self.direction = "left"
        elif self.x < 0: self.direction = "right"
        if self.y < self.num_y: self.y += speed
        elif self.fire_bullet_count > 10: self.y += (speed + 1)

class Enemy2Plane(BasePlane):
    def __init__(self, screen):
        super().__init__(2, screen, 158, -246, "./images/enemy2.png", 5, config.HP_LIST[2])
        self.create_images("enemy2_down")
        self.direction = "right"
    def move(self):
        speed = config.CURRENT_DIFFICULTY["enemy_speed"][2]
        if self.direction == "right": self.x += speed
        elif self.direction == "left": self.x -= speed
        if self.x + 165 > 480: self.direction = "left"
        elif self.x < 0: self.direction = "right"
        if self.y < 0: self.y += speed
        elif self.fire_bullet_count > 25: self.y += (speed - 2)

# --- 子弹与补给类 ---
class BaseBullet(Base):
    def __init__(self, screen, x, y, image_name, plane=None):
        super().__init__(screen, x, y, image_name)
        if plane:
            self.damage_value = config.BULLET_DAMAGE_VALUE[plane.plane_type]
    def display(self): self.screen.blit(self.image, (self.x, self.y))

class Bullet(BaseBullet):
    def __init__(self, screen, x, y, plane):
        super().__init__(screen, x, y, "./images/"+config.BULLET_TYPE_IMAGES[plane.plane_type], plane)
    def move(self): self.y -= 16
    def judge(self): return self.y < 0

class EnemyBullet(BaseBullet):
    def __init__(self, screen, x, y, plane):
        p_w = config.PLANE_SIZE[plane.plane_type]["width"]
        p_h = config.PLANE_SIZE[plane.plane_type]["height"]
        super().__init__(screen, x + p_w/2, y + p_h/2, 
                         "./images/"+config.BULLET_TYPE_IMAGES[plane.plane_type], plane)
    def move(self): self.y += 7
    def judge(self): return self.y > 852

class Supply(BaseBullet):
    def __init__(self, screen, x, y, s_type, speed, s_hp):
        super().__init__(screen, x, y, "./images/"+config.SUPPLY_IMAGES[s_type], None)
        self.speed = speed
        self.supply_HP = s_hp
        self.supply_type = s_type
    def move(self): self.y += self.speed
    def judge(self): return self.y > 855