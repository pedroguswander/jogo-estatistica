from game import Game
from game_over import GameOver
from main_menu import MainMenu
from stats_screen import StatsScreen
from constants import *
import pygame

state_dict = {
    "GAME": Game(),
    "GAME_OVER": GameOver(),
    "MAIN_MENU": MainMenu(),
    "STATS": StatsScreen(),
}

class StateManager:
    def __init__(self):
        self.state = "GAME"
        self.current_state = state_dict[self.state]
        self.running = True

    def start(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("My Pygame Window - Pattern Recognition")
        self.font = pygame.font.Font(None, 36)
        # create a clock and inject common dependencies into the starting state
        self.clock = pygame.time.Clock()

        # inject common objects into the state instance so states don't have to initialize pygame
        self.current_state.screen = self.screen
        self.current_state.font = self.font
        self.current_state.clock = self.clock
        self.current_state.window = (WINDOW_WIDTH, WINDOW_HEIGHT)

        self.start_state()

    def start_state(self):
        # call the state's start method (it should assume screen/font/clock were injected)
        self.current_state.start()
        
    def change_state(self, new_state_name):
        if new_state_name in state_dict.keys():
            self.current_state = state_dict[new_state_name]
            self.start = new_state_name
            # inject shared resources into the newly active state
            if hasattr(self, 'screen'):
                self.current_state.screen = self.screen
            if hasattr(self, 'font'):
                self.current_state.font = self.font
            if hasattr(self, 'clock'):
                self.current_state.clock = self.clock
            if hasattr(self, 'screen'):
                self.current_state.window = (WINDOW_WIDTH, WINDOW_HEIGHT)
            # call start for the new state
            try:
                self.start_state()
            except Exception:
                # ignore start errors for states that don't implement start()
                pass
        else:
            raise ValueError(f"State '{new_state_name}' does not exist.")

    def update(self):
        self.current_state.update()
        # Check for quit request
        if getattr(self.current_state, 'request_quit', False):
            self.running = False
        # Check for state change request
        if hasattr(self.current_state, 'request_state_change'):
            new_state = self.current_state.request_state_change
            print(new_state)
            self.current_state.request_state_change = None
            self.change_state(new_state)

    def draw(self):
        self.current_state.draw()

    def main_game_loop(self):
        while self.running:
            self.update()
            self.draw()

        pygame.quit()