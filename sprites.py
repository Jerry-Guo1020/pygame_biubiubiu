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
            self.bomb_picture_list.append(pygame.image.load("/images/" + bomb_picture_name + str(i) + ".png"))
            
            
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
        
        else:
            self.screen.blit(self.image, (self.x, self.y))
            
        if self.y > 860:
            self.active = False