import pygame
from recognizer import recognize_pattern


class InputHandler:
    """Handles mouse input for continuous drawing with left mouse button.

    - While left button held: append points.
    - On release: return the finished stroke (list of points) and clear internal buffer.
    """

    def __init__(self):
        self.points = []
        self.is_drawing = False

    def handle_event(self, event):
        # Returns finished stroke (list of points) when left button released, otherwise None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_drawing = True
            self.points = [event.pos]
        elif event.type == pygame.MOUSEMOTION and self.is_drawing:
            self.points.append(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_drawing = False
            finished = self.points[:]
            self.points = []
            return finished
        return None

    def draw(self, surface):
        if len(self.points) > 1:
            pygame.draw.lines(surface, (0, 255, 0), False, self.points, 3)


class Game:

    def __init__(self, window=(800, 600)):
        self.window = window
        self.screen = None
        self.font = None
        self.clock = None
        self.input = InputHandler()
        self.score = 0
        self.running = False

    def start(self):
        """Initializes pygame and starts the game loop. Calls update every frame."""
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(self.window)
        pygame.display.set_caption("My Pygame Window - Pattern Recognition")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # let input handler process event; if it returns a finished stroke, check pattern
                finished = self.input.handle_event(event)
                if finished is not None:
                    if recognize_pattern(finished):
                        self._on_pattern_recognized()

            self.update()
            self.clock.tick(60)

        pygame.quit()

    def update(self):
        # Draw everything: background, current stroke and counter
        self.screen.fill((0, 0, 0))

        # draw current stroke (while player holds left mouse)
        self.input.draw(self.screen)

        # draw score / counter
        text = self.font.render(f"Squares: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        pygame.display.flip()

    def _on_pattern_recognized(self):
        """Increment counter and (implicitly) draw via update. This is the hook when a pattern is recognized."""
        self.score += 1
        # Additional visual feedback could be implemented here (flash, small animation).