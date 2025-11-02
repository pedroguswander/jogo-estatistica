import pygame
import random


class Enemy:
    
    FALL_SPEED = 120  # pixels per second
    DEFAULT_SIZE = 50
    GRAVITY = 500  # pixels per second squared for defeated enemies
    DEFEATED_COLOR = (128, 0, 128)  # purple color for defeated state

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True
        self.weakness = None  # will be set at spawn time
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

    @classmethod
    def spawn(cls, screen_width):
        """Spawn a new enemy at a random x position at the top of the screen."""
        size = cls.DEFAULT_SIZE
        x = random.randint(0, screen_width - size)
        e = cls(x, -size, size, size)  # start above screen
        # assign a random weakness
        e.weakness = random.choice(["square", "circle", "l", "caret", "horizontal_line", "vertical_line"])
        return e

