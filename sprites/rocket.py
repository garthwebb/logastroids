"""Rocket sprite class with animation."""
import pygame
import math
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, BULLET_LIFETIME, ROCKET_SCALE


class Rocket(pygame.sprite.Sprite):
    """Animated rocket shot from the spaceship."""

    def __init__(self, x, y, vx, vy, sprite_sheets):
        """Initialize a rocket.
        
        Args:
            x: Initial x position
            y: Initial y position
            vx: Velocity x
            vy: Velocity y
            sprite_sheets: List of 4 sprite sheets (each containing 24 rotation frames)
        """
        super().__init__()
        self.sprite_sheets = sprite_sheets  # List of 4 sheets for animation
        self.animation_frame = 0  # 0-3, cycles through the 4 sprite sheets
        self.rotation_frame = 0  # 0-23, rotation within current sheet
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.life = BULLET_LIFETIME
        
        # Hitbox: circular collision, proportionally smaller than sprite
        # Base sprite is 48px, so scaled size is 48 * ROCKET_SCALE
        # Radius is 1/3 of sprite size (like spaceship at 96px with radius 32px)
        sprite_size = 48 * ROCKET_SCALE
        self.radius = sprite_size / 3.0
        
        # Calculate rotation based on velocity direction
        angle = math.degrees(math.atan2(vy, vx)) + 90  # +90 because sprites face up
        angle = angle % 360
        # Quantize to 15-degree increments (matching ship's 24-frame rotation: 360/24 = 15)
        angle = round(angle / 15.0) * 15.0
        frame_step = 360.0 / 24  # 24 frames per rotation
        self.rotation_frame = int((angle / frame_step) % 24)
        
        # Set initial image
        self._update_image()
    
    def _update_image(self):
        """Update sprite based on animation and rotation frames."""
        if self.sprite_sheets and self.animation_frame < len(self.sprite_sheets):
            sheet = self.sprite_sheets[self.animation_frame]
            if sheet and self.rotation_frame < len(sheet):
                img = sheet[self.rotation_frame].copy()
                # Scale the rocket sprite
                new_size = int(img.get_width() * ROCKET_SCALE)
                self.image = pygame.transform.smoothscale(img, (new_size, new_size))
                self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            else:
                # Fallback if frame is missing
                self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 100, 0), (2, 2), 2)
                self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        else:
            # Fallback if sprite sheets are missing
            self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 100, 0), (2, 2), 2)
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def update(self):
        """Update rocket position, animation, and lifetime."""
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
        
        # Cycle through animation frames
        # Rockets animate faster than bullets live, so cycle through 4 sprite sheets
        self.animation_frame = (self.life // (BULLET_LIFETIME // 4)) % 4
        
        self.rect.center = (int(self.x), int(self.y))
        self._update_image()
        
        self.life -= 1
        if self.life <= 0:
            self.kill()
