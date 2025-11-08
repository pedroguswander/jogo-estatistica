from game import Game
from game_over import GameOver
from main_menu import MainMenu
from stats_screen import StatsScreen
from chart_one import *
from charts import *
from constants import *
import pygame
import sys

class StateManager:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("My Pygame Window - Pattern Recognition")
        self.font = pygame.font.Font(None, 36)
        # create a clock and inject common dependencies into the starting state
        self.clock = pygame.time.Clock()

        self.state_dict = {
            "GAME": Game(self),
            "GAME_OVER": GameOver(self),
            "MAIN_MENU": MainMenu(self),
            "STATS": StatsScreen(),
        }

        self.current_state = "GAME"

        
    def get_state(self):
        return self.current_state
    
    def set_state(self, next_state):
        self.current_state = next_state

    def reset_state(self, state):
        self.state_dict[self.current_state](self)

    def main_game_loop(self):
        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.state_dict[self.current_state].run(events)

