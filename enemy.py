import pygame
import random
import score


class Enemy:
    
    FALL_SPEED = 120  # pixels per second
    DEFAULT_SIZE = 50
    GRAVITY = 500  # pixels per second squared for defeated enemies
    DEFEATED_COLOR = (128, 0, 128)  # purple color for defeated state

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True
        self.weakness = []  # will be set at spawn time
        self.is_defeated = False
        self.velocity = 0  # vertical velocity for defeated state
        self.dead_line_reached = False  # track if enemy has reached dead line

    def fall(self, delta_time):
        if self.is_defeated:
            # Apply gravity
            self.velocity += self.GRAVITY * delta_time
            self.rect.y += self.velocity * delta_time
        else:
            # Normal falling
            self.rect.y += self.FALL_SPEED * delta_time

    def defeat(self):
        """Mark enemy as defeated and initialize falling physics"""
        self.is_defeated = True
        self.velocity = 0  # Start with zero velocity

    def update(self, delta_time):
        if not self.active:
            return
            
        self.fall(delta_time)

    def draw(self, surface):
        if not self.active or self.dead_line_reached:
            return
            
        color = self.DEFEATED_COLOR if self.is_defeated else (255, 0, 0)
        pygame.draw.rect(surface, color, self.rect)

    def draw_enemy_weakness(self, win):
    # small symbol drawn above enemy center
        cx = self.rect.centerx 
        top = self.rect.top - 8
        size = 16
        color = (255, 255, 0)
        w = self.weakness

        if "square" in w:
            rect = pygame.Rect(cx - size//2, top - size, size, size)
            pygame.draw.rect(win, color, rect, 2)
        if "circle" in w:
            pygame.draw.circle(win, color, (cx, top - size//2), size//2, 2)
        if "v" in w:
            # draw a small V
            x1, y1 = cx - size//2, top - size
            x2, y2 = cx, top
            x3, y3 = cx + size//2, top - size
            pygame.draw.line(win, color, (x1, y1), (x2, y2), 2)
            pygame.draw.line(win, color, (x2, y2), (x3, y3), 2)
        if "caret" in w:
            # draw a small caret (^)
            x1, y1 = cx - size//2, top
            x2, y2 = cx, top - size
            x3, y3 = cx + size//2, top
            pygame.draw.line(win, color, (x1, y1), (x2, y2), 2)
            pygame.draw.line(win, color, (x2, y2), (x3, y3), 2)
        if "l" in w:
            x1, y1 = cx - size//2, top - size
            x2, y2 = x1, top
            x3, y3 = cx + size//2, top
            pygame.draw.line(win, color, (x1, y1), (x2, y2), 2)  # linha vertical
            pygame.draw.line(win, color, (x2, y2), (x3, y3), 2)

        if  "horizontal_line" in w:
            # draw a small horizontal line
            x1, y1 = cx - size//2, top - size//2
            x2, y2 = cx + size//2, top - size//2
            pygame.draw.line(win, color, (x1, y1), (x2, y2), 2)
        if "vertical_line" in w:
            # draw a small vertical line
            x1, y1 = cx, top - size//2
            x2, y2 = cx, top + size//2
            pygame.draw.line(win, color, (x1, y1), (x2, y2), 2)

    @classmethod
    def spawn(cls, screen_width):
        """Spawn a new enemy at a random x position at the top of the screen."""
        size = cls.DEFAULT_SIZE
        x = random.randint(0, screen_width - size)
        e = cls(x, -size, size, size)  # start above screen
        # assign a random weakness

        e.weakness.append(random.choice(["square","circle","l","caret","horizontal_line","vertical_line"]))
        
        choice = random.choice(["square","circle","l","caret","horizontal_line","vertical_line"])

        if choice != e.weakness[0] and score.get_score() >= 7:
            e.weakness.append(choice)


        return e

