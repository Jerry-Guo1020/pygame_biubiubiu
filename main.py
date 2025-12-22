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
        # 根据难度配置设置敌机最大数量
        limits = config.CURRENT_DIFFICULTY["enemy_limits"]
        config.ENEMY0_MAXIMUM = limits[0]
        config.ENEMY1_MAXIMUM = limits[1]
        config.ENEMY2_MAXIMUM = limits[2]
        
        if self.hit_score < 40: config.HP_LIST[:] = [1, 20, 100, 20]
        elif self.hit_score < 450: config.HP_LIST[:] = [1, 20, 120, 20]
        elif self.hit_score < 650: config.HP_LIST[:] = [1, 30, 140, 20]
        else: config.HP_LIST[:] = [2, 40, 180, 20]

        random_num = random.randint(1, 60)
        
        # Enemy 0
        spawn_rate = config.CURRENT_DIFFICULTY["spawn_rate_0"]
        if random_num in spawn_rate and len(self.enemy0_list) < config.ENEMY0_MAXIMUM:
            self.enemy0_list.append(sprites.Enemy0Plane(self.window_screen))
            
        # Enemy 1
        b1_min, b1_max = config.CURRENT_DIFFICULTY["boss1_interval"]
        boss1_trigger = random.randint(b1_min, b1_max)
        if (self.hit_score >= boss1_trigger and self.hit_score % boss1_trigger == 0) and len(self.enemy1_list) < config.ENEMY1_MAXIMUM:
            self.enemy1_list.append(sprites.Enemy1Plane(self.window_screen))
            
        # Enemy 2
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
        self.window_screen.blit(self.restart_img, (530, 760))
        self.window_screen.blit(self.exit_img, (532, 810))
        self.window_screen.blit(self.line_img, (482, 445))
        self.window_screen.blit(self.line_img, (482, 690))
        
        # 实时保存并显示最高分
        utils.save_max_score(self.hit_score)
        max_s = utils.read_max_score()
        self.draw_number(max_s, 590, 700)

        # 游戏状态UI
        if self.hero and self.hero.active:
            self.window_screen.blit(self.score_hp_img, (480, 460))
            # 炮管状态
            img_idx = 1 if self.hero.is_three_bullet else 0
            self.window_screen.blit(self.bullet_ui_imgs[img_idx], (480, 560))
            self.window_screen.blit(self.bullet_3_stock_img, (480, 605))
            
            # 数值显示
            self.draw_number(self.hit_score, 600, 460) # 得分
            self.draw_number(self.hero.HP, 600, 510)   # HP
            self.draw_number(self.hero.three_bullet_stock, 605, 600) # 弹药
        else:
            # 英雄死亡状态UI (全0)
            self.window_screen.blit(self.score_hp_img, (480, 460))
            self.window_screen.blit(self.bullet_ui_imgs[0], (480, 560))
            self.window_screen.blit(self.bullet_3_stock_img, (480, 605))
            self.draw_number(0, 600, 460)
            self.draw_number(0, 600, 510)
            self.draw_number(0, 605, 600)

        # Boss HP
        if self.enemy2_list:
            self.window_screen.blit(self.boss_hp_img, (480, 640))
            hp_val = max(0, self.enemy2_list[0].HP)
            self.draw_number(hp_val, 590, 640)
            
        # 返回主界面按钮 - 调整位置避免与BOSS血量重叠
        self.return_button = pygame.Rect(530, 590, 100, 40)
        pygame.draw.rect(self.window_screen, (100, 100, 200), self.return_button)
        font = pygame.font.SysFont('SimHei', 20)
        return_text = font.render('返回菜单', True, (255, 255, 255))
        self.window_screen.blit(return_text, (self.return_button.centerx - return_text.get_width()//2, self.return_button.centery - return_text.get_height()//2))

    def draw_number(self, num, x, y):
        h, t, s = utils.cut_number(num)
        self.window_screen.blit(self.number_imgs[h], (x, y))
        self.window_screen.blit(self.number_imgs[t], (x+30, y))
        self.window_screen.blit(self.number_imgs[s], (x+60, y))

    def process_enemy_logic(self, enemy_list):
        for enemy in enemy_list[:]:
            enemy.update_and_draw()
            enemy.fire(config.PLANE_MAXIMUM_BULLET[enemy.plane_type])
            enemy.move()
            
            # 碰撞检测
            if self.hero and self.hero.active:
                # 英雄被撞
                # 这里简化了逻辑：只检测子弹是否击中英雄
                self.hero.isHitted(enemy, config.PLANE_SIZE[3]["width"], config.PLANE_SIZE[3]["height"])
                # 敌机被撞
                if enemy.isHitted(self.hero, config.PLANE_SIZE[enemy.plane_type]["width"], config.PLANE_SIZE[enemy.plane_type]["height"]):
                    if enemy.HP <= 0 and not getattr(enemy, "scored", False):
                        self.add_score(enemy.plane_type)
                        enemy.scored = True

            if not enemy.active:
                enemy_list.remove(enemy)

    def add_score(self, p_type):
        """计算得分"""
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
                
                if self.hero and self.hero.active:
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
                    # 重新开始
                    elif 530 < mx < 642 and 760 < my < 808:
                        self.reborn()
                    # 退出
                    elif 532 < mx < 642 and 810 < my < 834:
                        sys.exit()
                    # 返回主界面按钮
                    elif hasattr(self, 'return_button') and self.return_button.collidepoint(mx, my):
                        self.return_to_main_menu()

    def select_difficulty(self):
        """显示难度选择界面"""
        font = pygame.font.SysFont('SimHei', 30)
        title_font = pygame.font.SysFont('SimHei', 50)
        
        # 按钮区域 - 居中显示
        button_width, button_height = 180, 60
        screen_center_x = config.SCREEN_SIZE[0] // 2
        button_center_x = screen_center_x - button_width // 2
        
        btn_easy_rect = pygame.Rect(button_center_x, 300, button_width, button_height)
        btn_normal_rect = pygame.Rect(button_center_x, 400, button_width, button_height)
        btn_hard_rect = pygame.Rect(button_center_x, 500, button_width, button_height)
        
        while True:
            self.window_screen.fill(config.BG_COLOR)
            
            # 绘制标题 - 居中显示
            title_text = title_font.render('请选择游戏难度', True, (0, 0, 0))
            title_x = (config.SCREEN_SIZE[0] - title_text.get_width()) // 2
            self.window_screen.blit(title_text, (title_x, 150))
            
            # 绘制按钮背景
            pygame.draw.rect(self.window_screen, (100, 200, 100), btn_easy_rect)
            pygame.draw.rect(self.window_screen, (100, 100, 200), btn_normal_rect)
            pygame.draw.rect(self.window_screen, (200, 100, 100), btn_hard_rect)
            
            # 绘制文字
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
            
            time.sleep(0.05)

    def show_game_over(self):
        """显示游戏结束界面"""
        font = pygame.font.SysFont('SimHei', 30)
        big_font = pygame.font.SysFont('SimHei', 50)
        
        # 半透明覆盖层
        overlay = pygame.Surface((config.SCREEN_SIZE[0], config.SCREEN_SIZE[1]))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.window_screen.blit(overlay, (0, 0))
        
        # 显示游戏结束文字
        game_over_text = big_font.render('游戏结束', True, (255, 0, 0))
        score_text = font.render(f'最终得分: {self.hit_score}', True, (255, 255, 255))
        restart_text = font.render('按 R 重新开始 或 点击按钮', True, (255, 255, 255))
        
        # 居中显示
        game_over_x = (config.SCREEN_SIZE[0] - game_over_text.get_width()) // 2
        score_x = (config.SCREEN_SIZE[0] - score_text.get_width()) // 2
        restart_x = (config.SCREEN_SIZE[0] - restart_text.get_width()) // 2
        
        self.window_screen.blit(game_over_text, (game_over_x, 300))
        self.window_screen.blit(score_text, (score_x, 380))
        self.window_screen.blit(restart_text, (restart_x, 430))
        
        # 显示重新开始和退出按钮
        restart_rect = pygame.Rect(config.SCREEN_SIZE[0]//2 - 90, 500, 180, 50)
        quit_rect = pygame.Rect(config.SCREEN_SIZE[0]//2 - 90, 570, 180, 50)
        
        pygame.draw.rect(self.window_screen, (0, 200, 0), restart_rect)
        pygame.draw.rect(self.window_screen, (200, 0, 0), quit_rect)
        
        restart_btn_text = font.render('重新开始', True, (255, 255, 255))
        quit_btn_text = font.render('退出游戏', True, (255, 255, 255))
        
        self.window_screen.blit(restart_btn_text, (restart_rect.centerx - restart_btn_text.get_width()//2, restart_rect.centery - restart_btn_text.get_height()//2))
        self.window_screen.blit(quit_btn_text, (quit_rect.centerx - quit_btn_text.get_width()//2, quit_rect.centery - quit_btn_text.get_height()//2))
        
        pygame.display.update()
        
        # 等待用户操作
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_r:
                        self.reborn()
                        return
                elif event.type == MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if restart_rect.collidepoint(mx, my):
                        self.reborn()
                        return
                    elif quit_rect.collidepoint(mx, my):
                        sys.exit()
            
            time.sleep(0.05)

    def return_to_main_menu(self):
        """返回主菜单界面"""
        # 保存最高分
        utils.save_max_score(self.hit_score)
        # 重新开始游戏并显示难度选择界面
        self.reborn()
        self.select_difficulty()

    def run(self):
        print("jerry的期末作业")
        
        # 启动难度选择
        self.select_difficulty()
        
        while True:
            # 1. 填充背景
            self.window_screen.fill(config.BG_COLOR)
            
            # 2. 暂停逻辑
            if self.is_pause:
                self.draw_ui() # 保持UI显示
                self.window_screen.blit(self.pause_image, (170, 402))
                pygame.display.update()
                self.process_input()
                time.sleep(0.1)
                continue

            # 3. 生成逻辑
            self.create_enemies()
            self.create_supply()
            
            # 4. 绘制右侧背景UI
            self.draw_ui()

            # 5. 更新并绘制Hero
            if self.hero and self.hero.active:
                self.hero.update_and_draw()
                self.hero.press_move()
                self.hero.press_fire()
                self.hero.move_limit()
            elif self.hero and not self.hero.active:
                # 英雄飞机已爆炸，显示游戏结束界面
                self.show_game_over()
                # 处理输入以允许用户操作（重新开始、退出等）
                self.process_input()
                time.sleep(0.04)
                continue  # 跳过剩余的游戏循环逻辑
            else:
                self.hero = None # 彻底清除引用

            # 6. 补给逻辑 (仅在英雄活跃时处理)
            if self.hero and self.hero.active:
                for supply in [self.blood_supply, self.bullet_supply]:
                    if supply:
                        supply.display()
                        supply.move()
                        # 回收越界补给
                        to_delete = False
                        if supply.judge(): 
                            to_delete = True
                        # 吃到补给
                        if self.hero and self.hero.active and self.hero.supply_hitted(supply):
                            if supply.supply_type == 0: # 血量
                                self.hero.HP = min(41, self.hero.HP - supply.supply_HP)
                            else: # 弹药
                                self.hero.is_three_bullet = True
                                self.hero.three_bullet_stock += 20
                            to_delete = True
                        
                        if to_delete:
                            if supply == self.blood_supply: self.blood_supply = None
                            elif supply == self.bullet_supply: self.bullet_supply = None

            # 7. 敌机逻辑 (仅在英雄活跃时处理)
            if self.hero and self.hero.active:
                self.process_enemy_logic(self.enemy0_list)
                self.process_enemy_logic(self.enemy1_list)
                self.process_enemy_logic(self.enemy2_list)

            # 8. 刷新屏幕
            pygame.display.update()
            
            # 9. 输入处理
            self.process_input()
            
            time.sleep(0.04)

if __name__ == "__main__":
    game = GameManager()
    game.run()
