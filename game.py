import pygame
from recognizer import recognize_pattern
from enemy import Enemy

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

    def __init__(self, window=(360, 640)):
        self.window = window
        self.screen = None
        self.font = None
        self.clock = None
        self.input = InputHandler()
        self.score = 0
        # targets cycle through these patterns
        self.targets = ["square", "z", "triangle", "circle"]
        self.target_index = 0
        self.running = False
        self.fps = 60
        # enemy spawning and management
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 2.0  # spawn every 2 seconds
        # dead line: choose near the end of the screen
        self.dead_line = pygame.Vector2(self.window[0] - 15, self.window[1] - 15)

    def start(self):
        """Initializes pygame and starts the game loop. Calls update every frame."""
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(self.window)
        pygame.display.set_caption("My Pygame Window - Pattern Recognition")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

        # spawn first enemy
        self.enemies.append(Enemy.spawn(self.window[0]))
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # let input handler process event; if it returns a finished stroke, check pattern
                finished = self.input.handle_event(event)
                if finished is not None:
                    # check against current target
                    current = self.current_target()
                    recognized = recognize_pattern(finished, pattern=current)
                    if recognized:
                        self._on_pattern_recognized()
                    # switch to next target on every attempt
                    self._next_target(recognized)

            self.delta_time = self.clock.tick(self.fps) / 1000.0  # convert to seconds
            self.update()
            self.draw()

        pygame.quit()

    def update(self):
        # Draw everything: background, current stroke and counter
        self.screen.fill((0, 0, 0))

        # Update spawn timer and spawn new enemies
        self.spawn_timer += self.delta_time
        if self.spawn_timer >= self.spawn_interval:
            self.enemies.append(Enemy.spawn(self.window[0]))
            self.spawn_timer = 0

        self.check_game_over()

        # Update and draw enemies, remove inactive ones

    def draw(self):
        # draw current stroke (while player holds left mouse)
        self.input.draw(self.screen)
        
        # draw the target symbol
        self.draw_target()

        # draw score / counter
        text = self.font.render(f"Acertos: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        # draw instruction about current target
        instr = self.font.render(f"Desenhe: {self.current_target().upper()}", True, (200, 200, 0))
        self.screen.blit(instr, (10, 40))

        self.enemies = [enemy for enemy in self.enemies if enemy.active]
        for enemy in self.enemies:
            enemy.update(self.delta_time)
            enemy.draw(self.screen)

        pygame.draw.line(self.screen, (255, 0, 0), (0, self.dead_line.y), (self.window[0], self.dead_line.y), 2)

        pygame.display.flip()

    def check_game_over(self):
        # Game over if any enemy reaches bottom of screen
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.dead_line.y:
                print("Game Over!")
                self.running = False

    def _on_pattern_recognized(self):
        """Increment counter and (implicitly) draw via update. This is the hook when a pattern is recognized."""
        self.score += 1
        # Additional visual feedback could be implemented here (flash, small animation).

    def current_target(self):
        return self.targets[self.target_index]

    def _next_target(self, recognized):
        if recognized:
            self.target_index = (self.target_index + 1) % len(self.targets)

    def draw_target(self):
        """Draw a small guide symbol on the screen to indicate the current pattern the player should draw."""
        # position and size for the guide
        size = 80
        x = self.window[0] - size - 20
        y = 20
        color = (100, 200, 255)
        pattern = self.current_target()
        if pattern == "square":
            rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.screen, color, rect, 3)
        elif pattern == "triangle":
            p1 = (x + size // 2, y)
            p2 = (x, y + size)
            p3 = (x + size, y + size)
            pygame.draw.polygon(self.screen, color, [p1, p2, p3], 3)
        elif pattern == "circle":
            pygame.draw.circle(self.screen, color, (x + size // 2, y + size // 2), size // 2, 3)