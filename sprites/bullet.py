"""Bullet sprite class."""
import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, BULLET_SPEED, BULLET_LIFETIME


class Bullet(pygame.sprite.Sprite):
    """Simple bullet shot from the spaceship."""

    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (2, 2), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.life = BULLET_LIFETIME

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Screen wrap for bullets to keep gameplay consistent
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        elif self.y > WINDOW_HEIGHT:
            self.y = 0
        self.rect.center = (int(self.x), int(self.y))
        self.life -= 1
        if self.life <= 0:
            self.kill()
