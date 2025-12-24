# 导入pygame库，用于游戏开发
import pygame
# 导入time库，用于时间相关操作
import time
# 导入random库，用于生成随机数
import random
# 导入sys库，用于系统相关功能
import sys
# 从pygame.locals导入所有常量
from pygame.locals import *

# 导入配置文件
import config
# 导入精灵文件（包含飞机、子弹等游戏对象）
import sprites
# 导入工具函数文件
import utils

# 初始化
# 初始化混音器（用于播放音效）
pygame.mixer.init()
# 初始化字体模块
pygame.font.init()

# 游戏管理器类，负责整个游戏的运行和控制
class GameManager:
    def __init__(self):
        # 创建游戏窗口，设置屏幕大小
        self.window_screen = pygame.display.set_mode(config.SCREEN_SIZE, 0, 32)
        # 设置窗口标题
        pygame.display.set_caption('飞机大战')
        
        # [Fix 3] 引入时钟对象，用于解决帧率慢的问题
        # 创建时钟对象，用于控制游戏帧率
        self.clock = pygame.time.Clock()
        
        # 游戏状态变量
        self.hit_score = 0      # 当前得分
        self.is_pause = False   # 是否暂停
        
        # 游戏精灵对象
        self.hero = None        # 英雄飞机对象
        self.enemy0_list = []   # 小型敌机列表
        self.enemy1_list = []   # 中型敌机列表
        self.enemy2_list = []   # 大型敌机列表
        self.blood_supply = None    # 血量补给对象
        self.bullet_supply = None   # 子弹补给对象
        
        # 加载游戏资源（图片、音效等）
        self.load_resources()
        self.load_music()
        
        # 初始化英雄飞机
        self.reborn()

    def load_resources(self):
        """加载所有UI图片"""
        try:
            # 加载背景图片
            self.background = pygame.image.load("./images/background.png")
            # 加载暂停界面图片
            self.pause_image = pygame.image.load("./images/btn_finish.png")
            # 下面这两个图片在新版UI中不再使用，但为了不修改你的注释和结构，保留加载代码
            self.restart_img = pygame.image.load("./images/restart_nor.png")
            self.exit_img = pygame.image.load("./images/quit_nor.png")
            
            # 加载各种UI元素图片
            self.desc_img = pygame.image.load("./images/description.png")     # 描述图片
            self.line_img = pygame.image.load("./images/line.png")           # 分割线图片
            self.score_hp_img = pygame.image.load("./images/score_hp.png")   # 分数血量UI图片
            self.max_score_img = pygame.image.load("./images/max_score.png") # 最高分UI图片
            self.boss_hp_img = pygame.image.load("./images/boss_HP.png")     # BOSS血量UI图片
            self.bullet_3_stock_img = pygame.image.load("./images/bullet_3_stock.png") # 三管炮弹药UI图片
            
            # 加载子弹UI图片（普通子弹和三管炮）
            self.bullet_ui_imgs = [
                pygame.image.load("./images/bullet_temp1.png"),  # 普通子弹UI
                pygame.image.load("./images/bullet_temp3.png")   # 三管炮UI
            ]
            
            # 加载数字图片（0-9）
            self.number_imgs = []
            for i in range(10):
                self.number_imgs.append(pygame.image.load(f"./images/number_{i}.png"))
                
        except Exception as e:
            print(f"Resource load error: {e}")
            sys.exit()

    def load_music(self):
        try:
            # 加载背景音乐
            pygame.mixer.music.load("./sound/PlaneWarsBackgroundMusic.mp3")
            # 设置背景音乐音量
            pygame.mixer.music.set_volume(0.3)
            # 循环播放背景音乐
            pygame.mixer.music.play(-1)
            # 加载英雄飞机发射音效
            self.hero_fire_sound = pygame.mixer.Sound("./sound/hero_fire.wav")
            # 设置发射音效音量
            self.hero_fire_sound.set_volume(0.2)
        except Exception:
            pass

    def reborn(self):
        # 创建新的英雄飞机对象
        self.hero = sprites.HeroPlane(self.window_screen)
        # 设置英雄飞机的发射音效
        self.hero.play_fire_music = self.hero_fire_sound
        # 重置得分为0
        self.hit_score = 0
        # 清空所有敌机列表
        self.enemy0_list.clear()
        self.enemy1_list.clear()
        self.enemy2_list.clear()
        # 清空补给对象
        self.blood_supply = None
        self.bullet_supply = None

    def create_enemies(self):
        # 难度动态调整：根据当前难度设置敌机最大数量
        limits = config.CURRENT_DIFFICULTY["enemy_limits"]
        config.ENEMY0_MAXIMUM = limits[0]  # 小型敌机最大数量
        config.ENEMY1_MAXIMUM = limits[1]  # 中型敌机最大数量
        config.ENEMY2_MAXIMUM = limits[2]  # 大型敌机最大数量
        
        # 根据得分动态调整敌机血量
        if self.hit_score < 40: config.HP_LIST[:] = [1, 20, 100, 20]      # 得分小于40时的血量
        elif self.hit_score < 450: config.HP_LIST[:] = [1, 20, 120, 20]   # 得分40-450时的血量
        elif self.hit_score < 650: config.HP_LIST[:] = [1, 30, 140, 20]   # 得分450-650时的血量
        else: config.HP_LIST[:] = [2, 40, 180, 20]                        # 得分超过650时的血量

        # 生成1-60之间的随机数，用于控制小型敌机生成
        random_num = random.randint(1, 60)
        
        # 生成小型敌机
        spawn_rate = config.CURRENT_DIFFICULTY["spawn_rate_0"]
        # 如果随机数在生成率范围内且敌机数量未达到上限
        if random_num in spawn_rate and len(self.enemy0_list) < config.ENEMY0_MAXIMUM:
            # 创建小型敌机对象并添加到列表
            self.enemy0_list.append(sprites.Enemy0Plane(self.window_screen))
            
        # 生成中型敌机（BOSS1）
        b1_min, b1_max = config.CURRENT_DIFFICULTY["boss1_interval"]  # 获取BOSS1出现间隔范围
        boss1_trigger = random.randint(b1_min, b1_max)                # 生成随机触发值
        # 如果得分达到触发条件且敌机数量未达到上限
        if (self.hit_score >= boss1_trigger and self.hit_score % boss1_trigger == 0) and len(self.enemy1_list) < config.ENEMY1_MAXIMUM:
            # 创建中型敌机对象并添加到列表
            self.enemy1_list.append(sprites.Enemy1Plane(self.window_screen))
            
        # 生成大型敌机（BOSS2）
        b2_min, b2_max = config.CURRENT_DIFFICULTY["boss2_interval"]  # 获取BOSS2出现间隔范围
        boss2_trigger = random.randint(b2_min, b2_max)                # 生成随机触发值
        # 如果得分达到触发条件且敌机数量未达到上限
        if (self.hit_score >= boss2_trigger and self.hit_score % boss2_trigger == 0) and len(self.enemy2_list) < config.ENEMY2_MAXIMUM:
            # 创建大型敌机对象并添加到列表
            self.enemy2_list.append(sprites.Enemy2Plane(self.window_screen))

    def create_supply(self):
        # 根据是否有大型敌机来设置补给生成概率
        limit = 1201 if self.enemy2_list else 2080
        # 生成随机数
        rand = random.randint(1, limit)
        
        # 生成血量补给
        # 如果当前没有血量补给且随机数能被690整除
        if not self.blood_supply and rand % 690 == 0:
            # 创建血量补给对象（类型0，速度3，血量增加-3）
            self.blood_supply = sprites.Supply(self.window_screen, random.randint(0, 422), random.randint(-105, -95), 0, 3, -3)
            
        # 生成子弹补给
        # 如果当前没有子弹补给且随机数能被300整除
        if not self.bullet_supply and rand % 300 == 0:
            # 创建子弹补给对象（类型1，速度3，血量影响0）
            self.bullet_supply = sprites.Supply(self.window_screen, random.randint(0, 420), random.randint(-115, -108), 1, 3, 0)

    def draw_ui(self):
        # 绘制右侧UI背景
        self.window_screen.blit(self.background, (0, 0))
        # 绘制描述信息图片
        self.window_screen.blit(self.desc_img, (482, 10))
        # 绘制最高分标签
        self.window_screen.blit(self.max_score_img, (480, 705))
        # 绘制分割线
        self.window_screen.blit(self.line_img, (482, 445))
        self.window_screen.blit(self.line_img, (482, 690))
        
        # 实时保存并显示最高分
        utils.save_max_score(self.hit_score)
        max_s = utils.read_max_score()
        # 在指定位置绘制最高分
        self.draw_number(max_s, 590, 700)

        # 获取英雄飞机状态信息
        hero_hp = 0
        hero_bullet_stock = 0
        is_three = False
        if self.hero:
            # 确保血量不为负数
            hero_hp = max(0, self.hero.HP)
            # 获取三管炮弹药数量
            hero_bullet_stock = self.hero.three_bullet_stock
            # 获取是否开启三管炮模式
            is_three = self.hero.is_three_bullet
        
        # 绘制分数和血量UI
        self.window_screen.blit(self.score_hp_img, (480, 460))
        # 根据是否开启三管炮选择对应的UI图片
        img_idx = 1 if is_three else 0
        self.window_screen.blit(self.bullet_ui_imgs[img_idx], (480, 560))
        # 绘制三管炮弹药UI
        self.window_screen.blit(self.bullet_3_stock_img, (480, 605))
        
        # 绘制当前得分
        self.draw_number(self.hit_score, 600, 460)
        # 绘制英雄血量
        self.draw_number(hero_hp, 600, 510)
        # 绘制三管炮弹药数量
        self.draw_number(hero_bullet_stock, 605, 600)

        # 如果有大型敌机，绘制BOSS血量
        if self.enemy2_list:
            self.window_screen.blit(self.boss_hp_img, (480, 640))
            # 确保BOSS血量不为负数
            hp_val = max(0, self.enemy2_list[0].HP)
            # 绘制BOSS血量
            self.draw_number(hp_val, 590, 640)
            
        # ================= [UI 修改重点区域] 开始 =================
        # [Fix 4 & 新需求] 重新设计右下角按钮组
        # 将三个按钮统一为矩形样式，并排列在底部
        
        # 创建按钮字体
        font_btn = pygame.font.SysFont('SimHei', 20)
        
        # 按钮布局参数
        btn_x = 500         # 按钮左上角X坐标 (右侧栏宽度约160，居中大概在500)
        btn_w = 130         # 按钮宽度
        btn_h = 35          # 按钮高度
        start_y = 745       # 第一个按钮的起始Y坐标 (在最高分下方)
        gap_y = 42          # 按钮之间的垂直间距

        # 定义三个按钮的矩形区域 (保存为self变量以便在点击事件中使用)
        self.restart_btn_rect = pygame.Rect(btn_x, start_y, btn_w, btn_h)  # 重新开始按钮区域
        self.return_btn_rect = pygame.Rect(btn_x, start_y + gap_y, btn_w, btn_h)  # 返回菜单按钮区域
        self.quit_btn_rect = pygame.Rect(btn_x, start_y + gap_y * 2, btn_w, btn_h)  # 退出游戏按钮区域

        # 定义按钮颜色 (R, G, B)
        color_restart = (46, 139, 87)   # 海洋绿 (重新开始)
        color_return = (70, 130, 180)   # 钢蓝 (返回菜单)
        color_quit = (178, 34, 34)      # 耐火砖红 (退出游戏)
        text_color = (255, 255, 255)    # 白色文字

        # 1. 绘制按钮背景矩形
        pygame.draw.rect(self.window_screen, color_restart, self.restart_btn_rect, border_radius=5)
        pygame.draw.rect(self.window_screen, color_return, self.return_btn_rect, border_radius=5)
        pygame.draw.rect(self.window_screen, color_quit, self.quit_btn_rect, border_radius=5)

        # 2. 渲染按钮文字
        txt_restart = font_btn.render('重新开始(R)', True, text_color)  # 重新开始按钮文字
        txt_return = font_btn.render('返回菜单', True, text_color)      # 返回菜单按钮文字
        txt_quit = font_btn.render('退出游戏', True, text_color)        # 退出游戏按钮文字

        # 3. 将文字居中绘制到按钮上
        self.window_screen.blit(txt_restart, (self.restart_btn_rect.centerx - txt_restart.get_width()//2, self.restart_btn_rect.centery - txt_restart.get_height()//2))
        self.window_screen.blit(txt_return, (self.return_btn_rect.centerx - txt_return.get_width()//2, self.return_btn_rect.centery - txt_return.get_height()//2))
        self.window_screen.blit(txt_quit, (self.quit_btn_rect.centerx - txt_quit.get_width()//2, self.quit_btn_rect.centery - txt_quit.get_height()//2))
        # ================= [UI 修改重点区域] 结束 =================

    def draw_number(self, num, x, y):
        # 将数字分解为百位、十位、个位
        h, t, s = utils.cut_number(num)
        # 绘制百位数字
        self.window_screen.blit(self.number_imgs[h], (x, y))
        # 绘制十位数字
        self.window_screen.blit(self.number_imgs[t], (x+30, y))
        # 绘制个位数字
        self.window_screen.blit(self.number_imgs[s], (x+60, y))

    def process_enemy_logic(self, enemy_list):
        # 遍历敌机列表中的每个敌机
        for enemy in enemy_list[:]:
            # 更新并绘制敌机
            enemy.update_and_draw() 
            
            # [Fix 1] 敌机死亡逻辑优化
            # 如果敌机血量大于0（即还存活）
            if enemy.HP > 0:
                # 敌机发射子弹
                enemy.fire(config.PLANE_MAXIMUM_BULLET[enemy.plane_type])
                # 敌机移动
                enemy.move()
                
                # 如果英雄飞机存在、活跃且血量大于0
                if self.hero and self.hero.active and self.hero.HP > 0:
                    # 检测英雄飞机是否被敌机子弹击中
                    self.hero.isHitted(enemy, config.PLANE_SIZE[3]["width"], config.PLANE_SIZE[3]["height"])
                    # 检测敌机是否被英雄飞机子弹击中
                    if enemy.isHitted(self.hero, config.PLANE_SIZE[enemy.plane_type]["width"], config.PLANE_SIZE[enemy.plane_type]["height"]):
                        # 如果敌机血量小于等于0且还没有计算过分数
                        if enemy.HP <= 0 and not getattr(enemy, "scored", False):
                            # 添加得分
                            self.add_score(enemy.plane_type)
                            # 标记敌机已计算过分数
                            enemy.scored = True
            
            # 如果敌机不活跃（被摧毁或飞出屏幕），从列表中移除
            if not enemy.active:
                enemy_list.remove(enemy)

    def add_score(self, p_type):
        # 获取敌机基础血量作为得分基准
        base_hp = config.HP_LIST[p_type]
        # 根据敌机类型计算得分
        if p_type == 0:  # 小型敌机
            # 如果当前得分小于650分，得分为基础血量；否则为一半
            self.hit_score += base_hp if self.hit_score < 650 else base_hp/2
        elif p_type == 1:  # 中型敌机
            self.hit_score += base_hp / 2  # 得分为基础血量的一半
        else:  # 大型敌机
            self.hit_score += base_hp / 4  # 得分为基础血量的四分之一
        # 将得分转换为整数
        self.hit_score = int(self.hit_score)

    def process_input(self):
        # 处理所有pygame事件
        for event in pygame.event.get():
            # 处理窗口关闭事件
            if event.type == QUIT:
                sys.exit()
                
            # 处理按键按下事件
            elif event.type == KEYDOWN:
                # Q键：暂停/继续游戏
                if event.key == K_q:
                    self.is_pause = not self.is_pause
                    # 暂停时暂停音乐，继续时恢复音乐
                    if self.is_pause: pygame.mixer.music.pause()
                    else: pygame.mixer.music.unpause()
                # R键：重新开始游戏
                elif event.key == K_r:
                    self.reborn()
                
                # [Fix 2] 只有当英雄存活(HP>0)时，才响应控制按键
                if self.hero and self.hero.active and self.hero.HP > 0:
                    # 方向键：控制飞机移动
                    if event.key in [K_LEFT, K_RIGHT, K_UP, K_DOWN]:
                        self.hero.key_down(event.key)
                    # S键：切换三管炮模式
                    elif event.key == K_s:
                        # 只有当有三管炮弹药时才能切换
                        if self.hero.three_bullet_stock > 0:
                            self.hero.is_three_bullet = not self.hero.is_three_bullet
                    # 空格键：发射子弹
                    elif event.key == K_SPACE:
                        self.hero.space_key_down(K_SPACE)
                    # B键：自爆
                    elif event.key == K_b:
                        self.hero.bomb()

            # 处理按键释放事件
            elif event.type == KEYUP:
                if self.hero and self.hero.active:
                    # 方向键释放：停止对应方向的移动
                    if event.key in [K_LEFT, K_RIGHT, K_UP, K_DOWN]:
                        self.hero.key_up(event.key)
                    # 空格键释放：停止发射子弹
                    elif event.key == K_SPACE:
                        self.hero.space_key_up(K_SPACE)

            # 处理鼠标点击事件
            elif event.type == MOUSEBUTTONDOWN:
                # 检测是否是左键点击
                if pygame.mouse.get_pressed()[0]:
                    # 获取鼠标点击位置
                    mx, my = pygame.mouse.get_pos()
                    # 暂停界面点击：恢复游戏
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
        # 创建字体对象
        font = pygame.font.SysFont('SimHei', 30)        # 按钮文字字体
        title_font = pygame.font.SysFont('SimHei', 50)  # 标题字体
        
        # 按钮区域设置
        button_width, button_height = 180, 60           # 按钮宽度和高度
        screen_center_x = config.SCREEN_SIZE[0] // 2    # 屏幕中心X坐标
        button_center_x = screen_center_x - button_width // 2  # 按钮中心X坐标
        
        # 定义三个难度按钮的矩形区域
        btn_easy_rect = pygame.Rect(button_center_x, 300, button_width, button_height)   # 简单难度按钮
        btn_normal_rect = pygame.Rect(button_center_x, 400, button_width, button_height) # 中等难度按钮
        btn_hard_rect = pygame.Rect(button_center_x, 500, button_width, button_height)   # 困难难度按钮
        
        # 难度选择循环
        while True:
            # 控制帧率为60FPS
            self.clock.tick(60) 
            # 填充背景色
            self.window_screen.fill(config.BG_COLOR)
            
            # 渲染标题文字
            title_text1 = title_font.render('欢迎使用飞机大战小游戏', True, (0, 0, 0))  # 主标题
            title_text2 = title_font.render('请选择游戏难度', True, (0, 0, 0))      # 副标题
            # 计算主标题的居中位置
            title_x = (config.SCREEN_SIZE[0] - title_text1.get_width()) // 2
            # 绘制主标题
            self.window_screen.blit(title_text1, (title_x, 150))
            
            # 绘制三个难度按钮的背景
            pygame.draw.rect(self.window_screen, (100, 200, 100), btn_easy_rect)   # 简单按钮背景（绿色）
            pygame.draw.rect(self.window_screen, (100, 100, 200), btn_normal_rect) # 中等按钮背景（蓝色）
            pygame.draw.rect(self.window_screen, (200, 100, 100), btn_hard_rect)   # 困难按钮背景（红色）
            
            # 渲染按钮文字
            text_easy = font.render('简单', True, (255, 255, 255))   # 简单按钮文字
            text_normal = font.render('中等', True, (255, 255, 255)) # 中等按钮文字
            text_hard = font.render('困难', True, (255, 255, 255))   # 困难按钮文字
            
            # 将按钮文字居中绘制到按钮上
            self.window_screen.blit(text_easy, (btn_easy_rect.centerx - text_easy.get_width()//2, btn_easy_rect.centery - text_easy.get_height()//2))
            self.window_screen.blit(text_normal, (btn_normal_rect.centerx - text_normal.get_width()//2, btn_normal_rect.centery - text_normal.get_height()//2))
            self.window_screen.blit(text_hard, (btn_hard_rect.centerx - text_hard.get_width()//2, btn_hard_rect.centery - text_hard.get_height()//2))
            
            # 更新显示
            pygame.display.update()
            
            # 处理事件
            for event in pygame.event.get():
                # 处理窗口关闭事件
                if event.type == QUIT:
                    sys.exit()
                # 处理鼠标点击事件
                elif event.type == MOUSEBUTTONDOWN:
                    # 获取鼠标点击位置
                    mx, my = pygame.mouse.get_pos()
                    # 如果点击简单按钮
                    if btn_easy_rect.collidepoint(mx, my):
                        # 设置当前难度为简单
                        config.CURRENT_DIFFICULTY = config.DIFFICULTY_LEVELS[0]
                        return
                    # 如果点击中等按钮
                    elif btn_normal_rect.collidepoint(mx, my):
                        # 设置当前难度为中等
                        config.CURRENT_DIFFICULTY = config.DIFFICULTY_LEVELS[1]
                        return
                    # 如果点击困难按钮
                    elif btn_hard_rect.collidepoint(mx, my):
                        # 设置当前难度为困难
                        config.CURRENT_DIFFICULTY = config.DIFFICULTY_LEVELS[2]
                        return

    def show_game_over(self):
        """显示游戏结束界面 - UI优化版"""
        # 定义字体
        font_btn = pygame.font.SysFont('SimHei', 22)  # 按钮字体略微调大
        font_score = pygame.font.SysFont('SimHei', 35)  # 分数字体
        big_font = pygame.font.SysFont('SimHei', 60)    # 大标题字体
        
        # 绘制半透明遮罩
        overlay = pygame.Surface((config.SCREEN_SIZE[0], config.SCREEN_SIZE[1]))
        overlay.set_alpha(200) # 稍微加深一点透明度，突出文字
        overlay.fill((0, 0, 0))
        self.window_screen.blit(overlay, (0, 0))
        
        # 绘制标题和分数
        game_over_text = big_font.render('游戏结束', True, (255, 50, 50)) # 标题用淡红色
        score_text = font_score.render(f'最终得分: {self.hit_score}', True, (255, 215, 0)) # 分数用金色
        
        # 计算居中坐标
        cx = config.SCREEN_SIZE[0] // 2
        # 绘制居中的游戏结束标题
        self.window_screen.blit(game_over_text, (cx - game_over_text.get_width() // 2, 200))
        # 绘制居中的最终得分
        self.window_screen.blit(score_text, (cx - score_text.get_width() // 2, 300))
        
        # ================= [按钮 UI 配置] =================
        # 按钮参数
        btn_w, btn_h = 200, 45  # 按钮宽200，高45
        btn_x = cx - btn_w // 2 # 按钮X轴居中
        start_y = 420           # 第一个按钮的起始Y高度
        gap_y = 65              # 按钮垂直间距
        
        # 定义按钮颜色 (和主界面保持一致)
        color_restart = (46, 139, 87)   # 海洋绿（重新开始）
        color_return = (70, 130, 180)   # 钢蓝（返回菜单）
        color_quit = (178, 34, 34)      # 耐火砖红（退出游戏）
        text_color = (255, 255, 255)    # 白色文字

        # 定义按钮区域 (Rect)
        rect_restart = pygame.Rect(btn_x, start_y, btn_w, btn_h)      # 重新开始按钮区域
        rect_return = pygame.Rect(btn_x, start_y + gap_y, btn_w, btn_h)  # 返回菜单按钮区域
        rect_quit = pygame.Rect(btn_x, start_y + gap_y * 2, btn_w, btn_h)  # 退出游戏按钮区域
        
        # 绘制按钮背景 (带圆角)
        pygame.draw.rect(self.window_screen, color_restart, rect_restart, border_radius=10)
        pygame.draw.rect(self.window_screen, color_return, rect_return, border_radius=10)
        pygame.draw.rect(self.window_screen, color_quit, rect_quit, border_radius=10)
        
        # 渲染按钮文字
        txt_restart = font_btn.render('重新开始(R)', True, text_color)  # 重新开始按钮文字
        txt_return = font_btn.render('返回主菜单', True, text_color)    # 返回菜单按钮文字
        txt_quit = font_btn.render('退出游戏', True, text_color)        # 退出游戏按钮文字
        
        # 将按钮文字居中绘制到按钮上
        self.window_screen.blit(txt_restart, (rect_restart.centerx - txt_restart.get_width()//2, rect_restart.centery - txt_restart.get_height()//2))
        self.window_screen.blit(txt_return, (rect_return.centerx - txt_return.get_width()//2, rect_return.centery - txt_return.get_height()//2))
        self.window_screen.blit(txt_quit, (rect_quit.centerx - txt_quit.get_width()//2, rect_quit.centery - txt_quit.get_height()//2))
        
        # 更新显示
        pygame.display.update()
        
        # 游戏结束界面循环
        while True:
            # 控制帧率为60FPS
            self.clock.tick(60) 
            # 处理事件
            for event in pygame.event.get():
                # 处理窗口关闭事件
                if event.type == QUIT:
                    sys.exit()
                    
                # 处理按键事件
                elif event.type == KEYDOWN:
                    # R键：重新开始游戏
                    if event.key == K_r:
                        self.reborn()
                        return # 退出当前循环，回到run循环
                        
                # 处理鼠标点击事件
                elif event.type == MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]: # 确保是左键点击
                        # 获取鼠标点击位置
                        mx, my = pygame.mouse.get_pos()
                        
                        # 检测点击的按钮区域
                        if rect_restart.collidepoint(mx, my):  # 重新开始按钮
                            self.reborn()
                            return
                        elif rect_return.collidepoint(mx, my):  # 返回菜单按钮
                            self.return_to_main_menu()
                            return
                        elif rect_quit.collidepoint(mx, my):  # 退出游戏按钮
                            sys.exit()

    def return_to_main_menu(self):
        """返回主菜单界面"""
        # 保存当前得分到最高分
        utils.save_max_score(self.hit_score)
        # 重新开始（重置游戏状态）
        self.reborn()
        # 显示难度选择界面
        self.select_difficulty()

    def run(self):
        # 打印游戏启动信息
        print("jerry的期末作业 - 优化UI版")
        # 显示难度选择界面
        self.select_difficulty()
        
        # 主游戏循环
        while True:
            # [Fix 3] 使用 Clock 控制 60 FPS
            self.clock.tick(60)
            
            # 填充背景色
            self.window_screen.fill(config.BG_COLOR)
            
            # 如果游戏暂停
            if self.is_pause:
                # 绘制UI
                self.draw_ui() 
                # 绘制暂停界面图片
                self.window_screen.blit(self.pause_image, (170, 402))
                # 更新显示
                pygame.display.update()
                # 处理输入事件
                self.process_input()
                # 继续下一轮循环
                continue

            # 创建敌机
            self.create_enemies()
            # 创建补给
            self.create_supply()
            # 绘制UI
            self.draw_ui()

            # [Fix 2] 游戏结束逻辑优化
            # 如果英雄飞机存在且活跃
            if self.hero and self.hero.active:
                # 更新并绘制英雄飞机
                self.hero.update_and_draw()
                
                # 如果英雄飞机血量大于0
                if self.hero.HP > 0:
                    # 处理英雄飞机的移动
                    self.hero.press_move()
                    # 处理英雄飞机的射击
                    self.hero.press_fire()
                    # 处理英雄飞机的边界限制
                    self.hero.move_limit()
                    
                    # 处理补给物品
                    for supply in [self.blood_supply, self.bullet_supply]:
                        if supply:
                            # 显示补给
                            supply.display()
                            # 移动补给
                            supply.move()
                            # 标记是否需要删除补给
                            to_delete = False
                            # 如果补给超出边界
                            if supply.judge(): to_delete = True
                            # 如果英雄飞机吃到补给
                            if self.hero.supply_hitted(supply):
                                # 如果是血量补给
                                if supply.supply_type == 0: 
                                    # 增加英雄血量（不超过41）
                                    self.hero.HP = min(41, self.hero.HP - supply.supply_HP)
                                else: 
                                    # 开启三管炮模式
                                    self.hero.is_three_bullet = True
                                    # 增加三管炮弹药
                                    self.hero.three_bullet_stock += 20
                                # 标记需要删除补给
                                to_delete = True
                            
                            # 如果需要删除补给
                            if to_delete:
                                # 如果是血量补给，清空血量补给对象
                                if supply == self.blood_supply: self.blood_supply = None
                                # 如果是子弹补给，清空子弹补给对象
                                elif supply == self.bullet_supply: self.bullet_supply = None
                
            # 如果英雄飞机存在但不活跃（被摧毁）
            elif self.hero and not self.hero.active:
                # 显示游戏结束界面
                self.show_game_over()
                # 处理输入事件
                self.process_input()
                # 继续下一轮循环
                continue
            else:
                # 如果英雄飞机不存在，设置为None
                self.hero = None 

            # 如果英雄飞机存在，处理敌机逻辑
            if self.hero:
                # 处理小型敌机逻辑
                self.process_enemy_logic(self.enemy0_list)
                # 处理中型敌机逻辑
                self.process_enemy_logic(self.enemy1_list)
                # 处理大型敌机逻辑
                self.process_enemy_logic(self.enemy2_list)

            # 更新显示
            pygame.display.update()
            # 处理输入事件
            self.process_input()

if __name__ == "__main__":
    game = GameManager()
    game.run()