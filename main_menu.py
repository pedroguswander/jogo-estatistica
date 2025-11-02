import pygame

class MainMenu:
    def __init__(self):
        self.screen = None
        self.font = None
        self.clock = None
        self.window = None
        self.title_screen = "Magic Touch: Runner for Hire"

    def start(self):
        if self.screen is None or self.font is None:
            raise RuntimeError("MainMenu.start() requires screen and font to be set by StateManager")
        
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.request_quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.request_state_change = "GAME"

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear screen with black
        text = self.font.render(self.title_screen, True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.window[0] // 2, self.window[1] // 2))
        self.screen.blit(text, text_rect)

        instruction = self.font.render("Press ENTER to start", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.window[0] // 2, self.window[1] // 2 + 50))
        self.screen.blit(instruction, instruction_rect)

        pygame.display.flip()