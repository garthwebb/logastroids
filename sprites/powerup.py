"""Power-up sprite class."""
import pygame
import random
from constants import WINDOW_HEIGHT, POWERUP_SPEED


class PowerUp(pygame.sprite.Sprite):
    """Power-up sprite that floats down the screen."""
    
    # Power-up types
    HEALTH = 'health'
    INVULNERABILITY = 'invulnerability'
    ROCKETS = 'rockets'
    SHIELDS = 'shields'
    
    def __init__(self, x, y, power_type, sprite_image):
        """Initialize a power-up.
        
        Args:
            x: Initial x position
            y: Initial y position
            power_type: Type of power-up (HEALTH, INVULNERABILITY, ROCKETS, SHIELDS)
            sprite_image: pygame.Surface containing the power-up sprite
        """
        super().__init__()
        self.power_type = power_type
        self.image = sprite_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity_y = POWERUP_SPEED
        self.lifetime = 300  # frames (5 seconds at 60 FPS)
        self.age = 0
    
    def update(self):
        """Update power-up position and check if it's off-screen."""
        self.rect.y += self.velocity_y
        self.age += 1
        
        # Remove if off-screen or too old
        if self.rect.top > WINDOW_HEIGHT or self.age > self.lifetime:
            self.kill()
    
    def get_description(self):
        """Return a human-readable description of the power-up."""
        descriptions = {
            self.HEALTH: "Health",
            self.INVULNERABILITY: "Invulnerability",
            self.ROCKETS: "Rockets",
            self.SHIELDS: "Shields"
        }
        return descriptions.get(self.power_type, "Unknown")
