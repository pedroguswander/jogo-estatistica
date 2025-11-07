import pygame
from constants import *

chart1_rect = pygame.Rect(CHARTS_START_X, CHART_ROW_ONE_Y, CHART_WIDTH, CHART_HEIGHT)

def draw_chart_one_border(win):
    border_color = (255, 255, 0) # Amarelo
    border_thickness = 2
    pygame.draw.rect(win, border_color, chart1_rect, border_thickness)

