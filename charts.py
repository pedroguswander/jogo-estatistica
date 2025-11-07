import pygame
from constants import *

chart2_rect = pygame.Rect(CHARTS_START_X + CHART_WIDTH, CHART_ROW_ONE_Y, CHART_WIDTH, CHART_HEIGHT)
chart3_rect = pygame.Rect(CHARTS_START_X, CHART_ROW_TWO_Y, CHART_WIDTH, CHART_HEIGHT)
chart4_rect = pygame.Rect(CHARTS_START_X + CHART_WIDTH, CHART_ROW_TWO_Y, CHART_WIDTH, CHART_HEIGHT)

def draw_chart_two_border(win):
    border_color = (0, 255, 255) # Ciano
    border_thickness = 2
    pygame.draw.rect(win, border_color, chart2_rect, border_thickness)

def draw_chart_three_border(win):
    """Desenha a borda do Chart C3."""
    border_color = (255, 0, 255) # Magenta
    border_thickness = 2
    pygame.draw.rect(win, border_color, chart3_rect, border_thickness)

def draw_chart_four_border(win):
    """Desenha a borda do Chart C4."""
    border_color = (0, 255, 0) # Verde
    border_thickness = 2
    pygame.draw.rect(win, border_color, chart4_rect, border_thickness)