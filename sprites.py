import pygame
import random
from pygame.locals import *
import config

class Base(object):
    def __init__(self, screen, x, y, image_name):
        self.x = x
        self.y = y
        self.screen = screen
        
        try:
            self.image = pygame.image.load(image_name)
        except Exception:
            print(f"这个照片的读取出现了错误：{image_name}")
            self.image = pygame.Surface((10, 10))


class BasePlane(Base):
    """飞机的基本类"""
    def __init__(self, plane_type, screen, x, y, image_name, picture_num, HP_temp):
        super().__init__(screen, x, y, image_name)
        
        """战斗相关"""
        # 子弹列表：用于存储这架飞机飞射出去的所有“子弹对象”
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
        self.scored = False
        
        """爆炸动画的相关基本配置"""
        # 存储爆炸效果的图片的列表 
        self.bomb_picture_list = [] 
        self.bomb_picture_num = picture_num
        # 动画延时计数器：用来控制爆炸动画的播放速度。 
        self.last_update_time = pygame.time.get_ticks()
        # 设置动画速度: 每 100 毫秒就换一张图
        self.frame_rate = 100
        # 当前动画帧索引：记录当前正在播放到第几张的爆炸图
        self.image_index = 0
      
         
        
    def create_images(self, bomb_picture_name):
        for i in range(1, self.bomb_picture_num + 1):
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
        
        if self.hitted and self.HP <=0:
            if now - self.last_update_time > self.frame_rate:
                self.last_update_time = now
                self.image_index += 1
                
                if self.image_index >= self.bomb_picture_num:
                    self.active = False
            
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
            if bullet.judge():
                self.bullet_list.remove(bullet)
    
    def isHitted(self, other_plane, width, height):
        """碰撞检测:判断我方有没有被敌机的子弹打中"""
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

        # 如果是Hero且开启了三管炮，检测额外炮管
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
        self.play_fire_music = None # Main会赋值给它

    # 移动逻辑保持不变
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
        # 简化原有的按键逻辑
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
        # 处理额外炮管
        for barrel in [self.barrel_2, self.barrel_3]:
            for bullet in barrel[:]:
                bullet.display()
                bullet.move()
                if bullet.judge():
                    barrel.remove(bullet)

    def supply_hitted(self, supply):
        """判断是否吃到补给"""
        if not supply or not self.HP: return False
        
        s_w = config.SUPPLY_SIZE[supply.supply_type]["width"]
        s_h = config.SUPPLY_SIZE[supply.supply_type]["height"]
        
        s_left = supply.x + s_w * 0.15
        s_right = supply.x + s_w * 0.85
        s_top = supply.y + s_h * 0.4
        s_bottom = supply.y + s_h * 0.9
        
        # 英雄的判定范围
        h_w = config.PLANE_SIZE[3]["width"]
        h_h = config.PLANE_SIZE[3]["height"]
        
        if (s_left > self.x + 0.05*h_w and s_right < self.x + 0.95*h_w and 
            s_top < self.y + 0.95*h_h and s_bottom > self.y + 0.1*h_h):
            return True
        return False

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
        
