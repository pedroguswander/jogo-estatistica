import pygame
from recognizer import recognize_pattern, identify_pattern
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
        self.targets = ["square", "z", "triangle", "circle", "v"]
        self.target_index = 0
        self.running = False
        self.fps = 60
        # enemy spawning and management
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 2.0  # spawn every 2 seconds
        # dead line: choose near the end of the screen
        self.dead_line = pygame.Vector2(self.window[0] - 15, self.window[1] - 15)
        self.recognized = False

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
                    # identify which pattern (if any) the player drew
                    matched, pattern = identify_pattern(finished)
                    self.recognized = matched
                    if matched:
                        print(f"Pattern recognized: {pattern}")
                        # try to destroy enemies under the stroke that have this weakness
                        destroyed = self.handle_recognized_pattern(pattern)
                        if destroyed > 0:
                            # increment score by number destroyed
                            self.score += destroyed
                    # advance target only when recognized (keeps current behavior)
                    self._next_target()

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
        
        # draw score / counter
        text = self.font.render(f"Acertos: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        self.enemies = [enemy for enemy in self.enemies if enemy.active]
        for enemy in self.enemies:
            enemy.update(self.delta_time)
            enemy.draw(self.screen)
            # draw enemy weakness symbol above the enemy
            self.draw_enemy_weakness(enemy)

        pygame.draw.line(self.screen, (255, 0, 0), (0, self.dead_line.y), (self.window[0], self.dead_line.y), 2)

        pygame.display.flip()

    def check_balloon_destroyed(self):
        # deprecated: handling is done in handle_recognized_pattern
        return

    def check_game_over(self):
        # Game over if any enemy reaches bottom of screen
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.dead_line.y:
                pass


    def _on_pattern_recognized(self):
        """Increment counter and (implicitly) draw via update. This is the hook when a pattern is recognized."""
        # legacy hook - keep for visual feedback only
        # Additional visual feedback could be implemented here (flash, small animation).

    def current_target(self):
        return self.targets[self.target_index]

    def _next_target(self):
        if self.recognized:
            self.target_index = (self.target_index + 1) % len(self.targets)

    def handle_recognized_pattern(self, pattern):
        if not pattern:
            return 0

        destroyed = 0
        for enemy in self.enemies:
            if not enemy.active:
                continue
            if enemy.weakness == pattern:
                enemy.active = False
                destroyed += 1
        return destroyed

    def draw_enemy_weakness(self, enemy):
        # small symbol drawn above enemy center
        cx = enemy.rect.centerx
        top = enemy.rect.top - 8
        size = 16
        color = (255, 255, 0)
        w = enemy.weakness
        if w == "square":
            rect = pygame.Rect(cx - size//2, top - size, size, size)
            pygame.draw.rect(self.screen, color, rect, 2)
        elif w == "triangle":
            p1 = (cx, top - size)
            p2 = (cx - size//2, top)
            p3 = (cx + size//2, top)
            pygame.draw.polygon(self.screen, color, [p1, p2, p3], 2)
        elif w == "circle":
            pygame.draw.circle(self.screen, color, (cx, top - size//2), size//2, 2)
        elif w == "z":
            # draw a small Z
            x1, y1 = cx - size//2, top - size
            x2, y2 = cx + size//2, top - size
            x3, y3 = cx - size//2, top
            x4, y4 = cx + size//2, top
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)
            pygame.draw.line(self.screen, color, (x2, y2), (x3, y3), 2)
            pygame.draw.line(self.screen, color, (x3, y3), (x4, y4), 2)
        elif w == "v":
            # draw a small V
            x1, y1 = cx - size//2, top - size
            x2, y2 = cx, top
            x3, y3 = cx + size//2, top - size
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)
            pygame.draw.line(self.screen, color, (x2, y2), (x3, y3), 2)
        elif w == "horizontal_line":
            # draw a small horizontal line
            x1, y1 = cx - size//2, top - size//2
            x2, y2 = cx + size//2, top - size//2
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)
        elif w == "vertical_line":
            # draw a small vertical line
            x1, y1 = cx, top - size//2
            x2, y2 = cx, top + size//2
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)