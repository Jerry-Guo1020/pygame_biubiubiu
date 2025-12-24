import pygame
import time
import random
import sys
from pygame.locals import *

import config
import sprites
import utils

# 初始化
pygame.mixer.init()
pygame.font.init()

class GameManager:
    def __init__(self):
        self.window_screen = pygame.display.set_mode(config.SCREEN_SIZE, 0, 32)
        pygame.display.set_caption('飞机大战')
        
        # [Fix 3] 引入时钟对象，用于解决帧率慢的问题
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.hit_score = 0
        self.is_pause = False
        
        # 精灵组
        self.hero = None
        self.enemy0_list = []
        self.enemy1_list = []
        self.enemy2_list = []
        self.blood_supply = None
        self.bullet_supply = None
        
        # 资源加载
        self.load_resources()
        self.load_music()
        
        # 初始化Hero
        self.reborn()

    def load_resources(self):
        """加载所有UI图片"""
        try:
            self.background = pygame.image.load("./images/background.png")
            self.pause_image = pygame.image.load("./images/btn_finish.png")
            # 下面这两个图片在新版UI中不再使用，但为了不修改你的注释和结构，保留加载代码
            self.restart_img = pygame.image.load("./images/restart_nor.png")
            self.exit_img = pygame.image.load("./images/quit_nor.png")
            
            self.desc_img = pygame.image.load("./images/description.png")
            self.line_img = pygame.image.load("./images/line.png")
            self.score_hp_img = pygame.image.load("./images/score_hp.png")
            self.max_score_img = pygame.image.load("./images/max_score.png")
            self.boss_hp_img = pygame.image.load("./images/boss_HP.png")
            self.bullet_3_stock_img = pygame.image.load("./images/bullet_3_stock.png")
            
            self.bullet_ui_imgs = [
                pygame.image.load("./images/bullet_temp1.png"),
                pygame.image.load("./images/bullet_temp3.png")
            ]
            
            self.number_imgs = []
            for i in range(10):
                self.number_imgs.append(pygame.image.load(f"./images/number_{i}.png"))
                
        except Exception as e:
            print(f"Resource load error: {e}")
            sys.exit()

    def load_music(self):
        try:
            pygame.mixer.music.load("./sound/PlaneWarsBackgroundMusic.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            self.hero_fire_sound = pygame.mixer.Sound("./sound/hero_fire.wav")
            self.hero_fire_sound.set_volume(0.2)
        except Exception:
            pass

    def reborn(self):
        self.hero = sprites.HeroPlane(self.window_screen)
        self.hero.play_fire_music = self.hero_fire_sound
        self.hit_score = 0
        self.enemy0_list.clear()
        self.enemy1_list.clear()
        self.enemy2_list.clear()
        self.blood_supply = None
        self.bullet_supply = None

    def create_enemies(self):
        # 难度动态调整
        limits = config.CURRENT_DIFFICULTY["enemy_limits"]
        config.ENEMY0_MAXIMUM = limits[0]
        config.ENEMY1_MAXIMUM = limits[1]
        config.ENEMY2_MAXIMUM = limits[2]
        
        if self.hit_score < 40: config.HP_LIST[:] = [1, 20, 100, 20]
        elif self.hit_score < 450: config.HP_LIST[:] = [1, 20, 120, 20]
        elif self.hit_score < 650: config.HP_LIST[:] = [1, 30, 140, 20]
        else: config.HP_LIST[:] = [2, 40, 180, 20]

        random_num = random.randint(1, 60)
        
        spawn_rate = config.CURRENT_DIFFICULTY["spawn_rate_0"]
        if random_num in spawn_rate and len(self.enemy0_list) < config.ENEMY0_MAXIMUM:
            self.enemy0_list.append(sprites.Enemy0Plane(self.window_screen))
            
        b1_min, b1_max = config.CURRENT_DIFFICULTY["boss1_interval"]
        boss1_trigger = random.randint(b1_min, b1_max)
        if (self.hit_score >= boss1_trigger and self.hit_score % boss1_trigger == 0) and len(self.enemy1_list) < config.ENEMY1_MAXIMUM:
            self.enemy1_list.append(sprites.Enemy1Plane(self.window_screen))
            
        b2_min, b2_max = config.CURRENT_DIFFICULTY["boss2_interval"]
        boss2_trigger = random.randint(b2_min, b2_max)
        if (self.hit_score >= boss2_trigger and self.hit_score % boss2_trigger == 0) and len(self.enemy2_list) < config.ENEMY2_MAXIMUM:
            self.enemy2_list.append(sprites.Enemy2Plane(self.window_screen))

    def create_supply(self):
        limit = 1201 if self.enemy2_list else 2080
        rand = random.randint(1, limit)
        
        if not self.blood_supply and rand % 690 == 0:
            self.blood_supply = sprites.Supply(self.window_screen, random.randint(0, 422), random.randint(-105, -95), 0, 3, -3)
            
        if not self.bullet_supply and rand % 300 == 0:
            self.bullet_supply = sprites.Supply(self.window_screen, random.randint(0, 420), random.randint(-115, -108), 1, 3, 0)

    def draw_ui(self):
        # 右侧背景
        self.window_screen.blit(self.background, (0, 0))
        self.window_screen.blit(self.desc_img, (482, 10))
        self.window_screen.blit(self.max_score_img, (480, 705))
        self.window_screen.blit(self.line_img, (482, 445))
        self.window_screen.blit(self.line_img, (482, 690))
        
        # 实时保存并显示最高分
        utils.save_max_score(self.hit_score)
        max_s = utils.read_max_score()
        self.draw_number(max_s, 590, 700)

        # 游戏状态UI
        hero_hp = 0
        hero_bullet_stock = 0
        is_three = False
        if self.hero:
            hero_hp = max(0, self.hero.HP)
            hero_bullet_stock = self.hero.three_bullet_stock
            is_three = self.hero.is_three_bullet
        
        self.window_screen.blit(self.score_hp_img, (480, 460))
        img_idx = 1 if is_three else 0
        self.window_screen.blit(self.bullet_ui_imgs[img_idx], (480, 560))
        self.window_screen.blit(self.bullet_3_stock_img, (480, 605))
        
        self.draw_number(self.hit_score, 600, 460)
        self.draw_number(hero_hp, 600, 510)
        self.draw_number(hero_bullet_stock, 605, 600)

        if self.enemy2_list:
            self.window_screen.blit(self.boss_hp_img, (480, 640))
            hp_val = max(0, self.enemy2_list[0].HP)
            self.draw_number(hp_val, 590, 640)
            
        # ================= [UI 修改重点区域] 开始 =================
        # [Fix 4 & 新需求] 重新设计右下角按钮组
        # 将三个按钮统一为矩形样式，并排列在底部
        
        font_btn = pygame.font.SysFont('SimHei', 20)
        
        # 按钮布局参数
        btn_x = 500         # 按钮左上角X坐标 (右侧栏宽度约160，居中大概在500)
        btn_w = 130         # 按钮宽度
        btn_h = 35          # 按钮高度
        start_y = 745       # 第一个按钮的起始Y坐标 (在最高分下方)
        gap_y = 42          # 按钮之间的垂直间距

        # 定义三个按钮的矩形区域 (保存为self变量以便在点击事件中使用)
        self.restart_btn_rect = pygame.Rect(btn_x, start_y, btn_w, btn_h)
        self.return_btn_rect = pygame.Rect(btn_x, start_y + gap_y, btn_w, btn_h)
        self.quit_btn_rect = pygame.Rect(btn_x, start_y + gap_y * 2, btn_w, btn_h)

        # 定义颜色 (R, G, B) - 区分颜色
        color_restart = (46, 139, 87)   # 海洋绿 (重新开始)
        color_return = (70, 130, 180)   # 钢蓝 (返回菜单)
        color_quit = (178, 34, 34)      # 耐火砖红 (退出游戏)
        text_color = (255, 255, 255)    # 白色文字

        # 1. 绘制按钮背景矩形
        pygame.draw.rect(self.window_screen, color_restart, self.restart_btn_rect, border_radius=5)
        pygame.draw.rect(self.window_screen, color_return, self.return_btn_rect, border_radius=5)
        pygame.draw.rect(self.window_screen, color_quit, self.quit_btn_rect, border_radius=5)

        # 2. 渲染文字
        txt_restart = font_btn.render('重新开始(R)', True, text_color)
        txt_return = font_btn.render('返回菜单', True, text_color)
        txt_quit = font_btn.render('退出游戏', True, text_color)

        # 3. 将文字居中绘制到按钮上
        self.window_screen.blit(txt_restart, (self.restart_btn_rect.centerx - txt_restart.get_width()//2, self.restart_btn_rect.centery - txt_restart.get_height()//2))
        self.window_screen.blit(txt_return, (self.return_btn_rect.centerx - txt_return.get_width()//2, self.return_btn_rect.centery - txt_return.get_height()//2))
        self.window_screen.blit(txt_quit, (self.quit_btn_rect.centerx - txt_quit.get_width()//2, self.quit_btn_rect.centery - txt_quit.get_height()//2))
        # ================= [UI 修改重点区域] 结束 =================

    def draw_number(self, num, x, y):
        h, t, s = utils.cut_number(num)
        self.window_screen.blit(self.number_imgs[h], (x, y))
        self.window_screen.blit(self.number_imgs[t], (x+30, y))
        self.window_screen.blit(self.number_imgs[s], (x+60, y))

    def process_enemy_logic(self, enemy_list):
        for enemy in enemy_list[:]:
            enemy.update_and_draw() 
            
            # [Fix 1] 敌机死亡逻辑优化
            if enemy.HP > 0:
                enemy.fire(config.PLANE_MAXIMUM_BULLET[enemy.plane_type])
                enemy.move()
                
                if self.hero and self.hero.active and self.hero.HP > 0:
                    self.hero.isHitted(enemy, config.PLANE_SIZE[3]["width"], config.PLANE_SIZE[3]["height"])
                    if enemy.isHitted(self.hero, config.PLANE_SIZE[enemy.plane_type]["width"], config.PLANE_SIZE[enemy.plane_type]["height"]):
                        if enemy.HP <= 0 and not getattr(enemy, "scored", False):
                            self.add_score(enemy.plane_type)
                            enemy.scored = True
            
            if not enemy.active:
                enemy_list.remove(enemy)

    def add_score(self, p_type):
        base_hp = config.HP_LIST[p_type]
        if p_type == 0:
            self.hit_score += base_hp if self.hit_score < 650 else base_hp/2
        elif p_type == 1:
            self.hit_score += base_hp / 2
        else:
            self.hit_score += base_hp / 4
        self.hit_score = int(self.hit_score)

    def process_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
                
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    self.is_pause = not self.is_pause
                    if self.is_pause: pygame.mixer.music.pause()
                    else: pygame.mixer.music.unpause()
                elif event.key == K_r:
                    self.reborn()
                
                # [Fix 2] 只有当英雄存活(HP>0)时，才响应控制按键
                if self.hero and self.hero.active and self.hero.HP > 0:
                    if event.key in [K_LEFT, K_RIGHT, K_UP, K_DOWN]:
                        self.hero.key_down(event.key)
                    elif event.key == K_s:
                        if self.hero.three_bullet_stock > 0:
                            self.hero.is_three_bullet = not self.hero.is_three_bullet
                    elif event.key == K_SPACE:
                        self.hero.space_key_down(K_SPACE)
                    elif event.key == K_b:
                        self.hero.bomb()

            elif event.type == KEYUP:
                if self.hero and self.hero.active:
                    if event.key in [K_LEFT, K_RIGHT, K_UP, K_DOWN]:
                        self.hero.key_up(event.key)
                    elif event.key == K_SPACE:
                        self.hero.space_key_up(K_SPACE)

            elif event.type == MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    # 暂停界面点击
                    if self.is_pause and 170 < mx < 310 and 402 < my < 450:
                        self.is_pause = False
                        pygame.mixer.music.unpause()
                    
                    # ================= [输入处理修改] 开始 =================
                    # 使用新的矩形区域检测点击，替代了原来的硬编码坐标和旧按钮
                    
                    # 重新开始按钮点击
                    elif hasattr(self, 'restart_btn_rect') and self.restart_btn_rect.collidepoint(mx, my):
                        self.reborn()
                    # 返回菜单按钮点击
                    elif hasattr(self, 'return_btn_rect') and self.return_btn_rect.collidepoint(mx, my):
                        self.return_to_main_menu()
                    # 退出游戏按钮点击
                    elif hasattr(self, 'quit_btn_rect') and self.quit_btn_rect.collidepoint(mx, my):
                        sys.exit()
                    # ================= [输入处理修改] 结束 =================

    def select_difficulty(self):
        """显示难度选择界面"""
        font = pygame.font.SysFont('SimHei', 30)
        title_font = pygame.font.SysFont('SimHei', 50)
        
        # 按钮区域
        button_width, button_height = 180, 60
        screen_center_x = config.SCREEN_SIZE[0] // 2
        button_center_x = screen_center_x - button_width // 2
        
        btn_easy_rect = pygame.Rect(button_center_x, 300, button_width, button_height)
        btn_normal_rect = pygame.Rect(button_center_x, 400, button_width, button_height)
        btn_hard_rect = pygame.Rect(button_center_x, 500, button_width, button_height)
        
        while True:
            self.clock.tick(60) 
            self.window_screen.fill(config.BG_COLOR)
            
            title_text1 = title_font.render('欢迎使用飞机大战小游戏', True, (0, 0, 0))
            title_text2 = title_font.render('请选择游戏难度', True, (0, 0, 0))
            title_x = (config.SCREEN_SIZE[0] - title_text1.get_width()) // 2
            self.window_screen.blit(title_text1, (title_x, 150))
            
            pygame.draw.rect(self.window_screen, (100, 200, 100), btn_easy_rect)
            pygame.draw.rect(self.window_screen, (100, 100, 200), btn_normal_rect)
            pygame.draw.rect(self.window_screen, (200, 100, 100), btn_hard_rect)
            
            text_easy = font.render('简单', True, (255, 255, 255))
            text_normal = font.render('中等', True, (255, 255, 255))
            text_hard = font.render('困难', True, (255, 255, 255))
            
            self.window_screen.blit(text_easy, (btn_easy_rect.centerx - text_easy.get_width()//2, btn_easy_rect.centery - text_easy.get_height()//2))
            self.window_screen.blit(text_normal, (btn_normal_rect.centerx - text_normal.get_width()//2, btn_normal_rect.centery - text_normal.get_height()//2))
            self.window_screen.blit(text_hard, (btn_hard_rect.centerx - text_hard.get_width()//2, btn_hard_rect.centery - text_hard.get_height()//2))
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if btn_easy_rect.collidepoint(mx, my):
                        config.CURRENT_DIFFICULTY = config.DIFFICULTY_LEVELS[0]
                        return
                    elif btn_normal_rect.collidepoint(mx, my):
                        config.CURRENT_DIFFICULTY = config.DIFFICULTY_LEVELS[1]
                        return
                    elif btn_hard_rect.collidepoint(mx, my):
                        config.CURRENT_DIFFICULTY = config.DIFFICULTY_LEVELS[2]
                        return

    def show_game_over(self):
        """显示游戏结束界面 - UI优化版"""
        # 定义字体
        font_btn = pygame.font.SysFont('SimHei', 22)  # 按钮字体略微调大
        font_score = pygame.font.SysFont('SimHei', 35)
        big_font = pygame.font.SysFont('SimHei', 60)
        
        # 绘制半透明遮罩
        overlay = pygame.Surface((config.SCREEN_SIZE[0], config.SCREEN_SIZE[1]))
        overlay.set_alpha(200) # 稍微加深一点透明度，突出文字
        overlay.fill((0, 0, 0))
        self.window_screen.blit(overlay, (0, 0))
        
        # 绘制标题和分数
        game_over_text = big_font.render('游戏结束', True, (255, 50, 50)) # 标题用淡红色
        score_text = font_score.render(f'最终得分: {self.hit_score}', True, (255, 215, 0)) # 分数用金色
        
        # 计算标题居中坐标
        cx = config.SCREEN_SIZE[0] // 2
        self.window_screen.blit(game_over_text, (cx - game_over_text.get_width() // 2, 200))
        self.window_screen.blit(score_text, (cx - score_text.get_width() // 2, 300))
        
        # ================= [按钮 UI 配置] =================
        # 按钮参数
        btn_w, btn_h = 200, 45  # 按钮宽200，高45
        btn_x = cx - btn_w // 2 # 按钮X轴居中
        start_y = 420           # 第一个按钮的起始Y高度
        gap_y = 65              # 按钮垂直间距
        
        # 定义颜色 (和你主界面保持一致)
        color_restart = (46, 139, 87)   # 海洋绿
        color_return = (70, 130, 180)   # 钢蓝
        color_quit = (178, 34, 34)      # 耐火砖红
        text_color = (255, 255, 255)

        # 定义按钮区域 (Rect)
        rect_restart = pygame.Rect(btn_x, start_y, btn_w, btn_h)
        rect_return = pygame.Rect(btn_x, start_y + gap_y, btn_w, btn_h)
        rect_quit = pygame.Rect(btn_x, start_y + gap_y * 2, btn_w, btn_h)
        
        # 绘制按钮背景 (带圆角)
        pygame.draw.rect(self.window_screen, color_restart, rect_restart, border_radius=10)
        pygame.draw.rect(self.window_screen, color_return, rect_return, border_radius=10)
        pygame.draw.rect(self.window_screen, color_quit, rect_quit, border_radius=10)
        
        # 渲染按钮文字
        txt_restart = font_btn.render('重新开始(R)', True, text_color)
        txt_return = font_btn.render('返回主菜单', True, text_color)
        txt_quit = font_btn.render('退出游戏', True, text_color)
        
        # 文字居中绘制
        self.window_screen.blit(txt_restart, (rect_restart.centerx - txt_restart.get_width()//2, rect_restart.centery - txt_restart.get_height()//2))
        self.window_screen.blit(txt_return, (rect_return.centerx - txt_return.get_width()//2, rect_return.centery - txt_return.get_height()//2))
        self.window_screen.blit(txt_quit, (rect_quit.centerx - txt_quit.get_width()//2, rect_quit.centery - txt_quit.get_height()//2))
        
        pygame.display.update()
        
        while True:
            self.clock.tick(60) 
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                    
                elif event.type == KEYDOWN:
                    if event.key == K_r:
                        self.reborn()
                        return # 退出当前循环，回到run循环
                        
                elif event.type == MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]: # 确保是左键点击
                        mx, my = pygame.mouse.get_pos()
                        
                        # 检测点击区域
                        if rect_restart.collidepoint(mx, my):
                            self.reborn()
                            return
                        elif rect_return.collidepoint(mx, my):
                            self.return_to_main_menu()
                            return
                        elif rect_quit.collidepoint(mx, my):
                            sys.exit()

    def return_to_main_menu(self):
        """返回主菜单界面"""
        utils.save_max_score(self.hit_score)
        self.reborn()
        self.select_difficulty()

    def run(self):
        print("jerry的期末作业 - 优化UI版")
        self.select_difficulty()
        
        while True:
            # [Fix 3] 使用 Clock 控制 60 FPS
            self.clock.tick(60)
            
            self.window_screen.fill(config.BG_COLOR)
            
            if self.is_pause:
                self.draw_ui() 
                self.window_screen.blit(self.pause_image, (170, 402))
                pygame.display.update()
                self.process_input()
                continue

            self.create_enemies()
            self.create_supply()
            self.draw_ui()

            # [Fix 2] 游戏结束逻辑优化
            if self.hero and self.hero.active:
                self.hero.update_and_draw()
                
                if self.hero.HP > 0:
                    self.hero.press_move()
                    self.hero.press_fire()
                    self.hero.move_limit()
                    
                    for supply in [self.blood_supply, self.bullet_supply]:
                        if supply:
                            supply.display()
                            supply.move()
                            to_delete = False
                            if supply.judge(): to_delete = True
                            if self.hero.supply_hitted(supply):
                                if supply.supply_type == 0: 
                                    self.hero.HP = min(41, self.hero.HP - supply.supply_HP)
                                else: 
                                    self.hero.is_three_bullet = True
                                    self.hero.three_bullet_stock += 20
                                to_delete = True
                            
                            if to_delete:
                                if supply == self.blood_supply: self.blood_supply = None
                                elif supply == self.bullet_supply: self.bullet_supply = None
                
            elif self.hero and not self.hero.active:
                self.show_game_over()
                self.process_input()
                continue
            else:
                self.hero = None 

            if self.hero:
                self.process_enemy_logic(self.enemy0_list)
                self.process_enemy_logic(self.enemy1_list)
                self.process_enemy_logic(self.enemy2_list)

            pygame.display.update()
            self.process_input()

if __name__ == "__main__":
    game = GameManager()
    game.run()