import pygame
import sys
# 更好的退出
import traceback

pygame.init()
pygame.mixer.init()


width = 400
height = 700 

bg_size = width, height
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption("飞机大战")

background = pygame.image.load("images/background.png").convert()

# 放入背景音乐和被攻击特效

