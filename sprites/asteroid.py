"""Asteroid sprite class."""
import pygame
import math
import random
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, ASTEROID_ROTATION_RANGE


class Asteroid(pygame.sprite.Sprite):
    """Asteroid that can progress through visual stages when shot."""

    def __init__(self, sprites_by_stage, stage_index, x, y, vx, vy, rotation, rotation_speed, scale=1.0, spawn_children=True):
        super().__init__()
        self.sprites_by_stage = sprites_by_stage
        self.stage_index = stage_index
        self.sprites = self.sprites_by_stage[self.stage_index]
        self.rotation = rotation
        self.rotation_speed = rotation_speed
        self.current_frame = 0
        self.scale = scale  # Scale factor for this asteroid (1.0 = normal size)
        self.spawn_children = spawn_children  # Whether to spawn child asteroids when destroyed
        self.hit_points = 4  # Each asteroid has 4 health (one per stage)
        
        # Load and scale the image
        original_image = self.sprites[self.current_frame]
        if scale != 1.0:
            new_size = (int(original_image.get_width() * scale), int(original_image.get_height() * scale))
            self.image = pygame.transform.scale(original_image, new_size)
        else:
            self.image = original_image
        
        self.rect = self.image.get_rect(center=(x, y))
        # Circle hitbox at ~80% of sprite diameter (radius = 0.4 * width)
        self.radius = int(self.rect.width * 0.4)
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy

    def update(self):
        # Spin
        self.rotation = (self.rotation + self.rotation_speed) % 360
        num_frames = len(self.sprites)
        frame_index = int((self.rotation / 360.0) * num_frames) % num_frames
        if frame_index != self.current_frame:
            self.current_frame = frame_index
            original_image = self.sprites[self.current_frame]
            # Apply scaling if needed
            if self.scale != 1.0:
                new_size = (int(original_image.get_width() * self.scale), int(original_image.get_height() * self.scale))
                self.image = pygame.transform.scale(original_image, new_size)
            else:
                self.image = original_image

        # Move
        self.x += self.vx
        self.y += self.vy
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        elif self.y > WINDOW_HEIGHT:
            self.y = 0
        if self.rect:
            self.rect.center = (int(self.x), int(self.y))

    def advance_stage(self):
        """Advance to the next visual stage. Returns True if still alive, False if finished."""
        next_index = self.stage_index + 1
        if next_index >= len(self.sprites_by_stage):
            return False
        self.stage_index = next_index
        self.sprites = self.sprites_by_stage[self.stage_index]
        # Preserve rotation mapping to keep frame continuity
        num_frames = len(self.sprites)
        frame_index = int((self.rotation / 360.0) * num_frames) % num_frames
        self.current_frame = frame_index
        original_image = self.sprites[self.current_frame]
        # Apply scaling if needed
        if self.scale != 1.0:
            new_size = (int(original_image.get_width() * self.scale), int(original_image.get_height() * self.scale))
            self.image = pygame.transform.scale(original_image, new_size)
        else:
            self.image = original_image
        return True

    def take_damage(self, damage):
        """Apply damage to the asteroid. Returns True if still alive, False if destroyed."""
        self.hit_points -= damage
        if self.hit_points <= 0:
            return False
        # Apply stage advancement for each hit point lost
        # Damage of 1 = one stage, damage of 4 = destroy immediately
        for _ in range(damage):
            if not self.advance_stage():
                return False
        return True
