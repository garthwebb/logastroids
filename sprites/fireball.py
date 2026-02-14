"""Fireball sprite class - projectile shot by boss."""
import pygame
import math
from constants import WINDOW_WIDTH, WINDOW_HEIGHT


class Fireball(pygame.sprite.Sprite):
    """Animated fireball shot from the boss ship."""

    def __init__(self, x, y, vx, vy, sprite_sheet):
        """Initialize a fireball.
        
        Args:
            x: Initial x position
            y: Initial y position
            vx: Velocity x
            vy: Velocity y
            sprite_sheet: Sprite sheet containing 24 rotation frames
        """
        super().__init__()
        self.sprite_sheet = sprite_sheet or []
        self.rotation_frame = 0  # 0-23, rotation frame
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.life = 180  # Fireballs live for 3 seconds at 60 FPS
        
        # Hitbox: circular collision
        # Base sprite is 48px, radius is about 1/3 of sprite size
        self.radius = 48 / 3.0
        
        # Calculate rotation based on velocity direction
        angle = math.degrees(math.atan2(vy, vx)) + 90  # +90 because sprites face up
        angle = angle % 360
        # Quantize to 15-degree increments (24 frames: 360/24 = 15)
        angle = round(angle / 15.0) * 15.0
        frame_step = 360.0 / 24
        self.rotation_frame = int((angle / frame_step) % 24)
        
        # Set initial image
        self._update_image()
    
    def _update_image(self):
        """Update sprite based on rotation frame."""
        if self.sprite_sheet and self.rotation_frame < len(self.sprite_sheet):
            self.image = self.sprite_sheet[self.rotation_frame].copy()
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        else:
            # Fallback if sprite sheet is missing
            self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 100, 0), (4, 4), 4)
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def update(self):
        """Update fireball position and lifetime."""
        self.x += self.vx
        self.y += self.vy
        
        # Screen wrap
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        elif self.y > WINDOW_HEIGHT:
            self.y = 0
        
        self.rect.center = (int(self.x), int(self.y))
        self._update_image()
        
        self.life -= 1
        if self.life <= 0:
            self.kill()
