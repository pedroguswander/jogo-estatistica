import pygame
import random


class Enemy:
    
    FALL_SPEED = 150  # pixels per second
    DEFAULT_SIZE = 50

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True  # flag to mark if enemy should be removed

    def fall(self, delta_time):
        # Move by FALL_SPEED pixels per second, scaled by actual frame time
        self.rect.y += self.FALL_SPEED * delta_time

    def update(self, delta_time):
        self.fall(delta_time)
        # Mark for removal if fallen below screen
        if self.rect.top > 640:  # using default window height
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect)

    @classmethod
    def spawn(cls, screen_width):
        """Spawn a new enemy at a random x position at the top of the screen."""
        size = cls.DEFAULT_SIZE
        x = random.randint(0, screen_width - size)
        return cls(x, -size, size, size)  # start above screen

