import pygame
from constants import WINDOW_GAME_WIDTH, WINDOW_GAME_HEIGHT

class MainMenu:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.screen = state_manager.screen
        self.font = state_manager.font
        self.clock = state_manager.clock
        self.window = (WINDOW_GAME_WIDTH, WINDOW_GAME_HEIGHT)
        self.title_screen = "Magic Touch: Runner for Hire"

    def start(self):
        if self.screen is None or self.font is None:
            raise RuntimeError("MainMenu.start() requires screen and font to be set by StateManager")
        
    def run(self, events):
        self.update(events)
        self.draw(events)
        
    def update(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state_manager.set_state("GAME")
                    self.state_manager.reset_state("GAME")

    def draw(self, events):
        self.screen.fill((0, 0, 0))  # Clear screen with black
        text = self.font.render(self.title_screen, True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.window[0] // 2, self.window[1] // 2))
        self.screen.blit(text, text_rect)

        instruction = self.font.render("Press ENTER to start", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.window[0] // 2, self.window[1] // 2 + 50))
        self.screen.blit(instruction, instruction_rect)

        pygame.display.flip()