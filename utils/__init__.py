"""Sprite sheet loading utilities and specs."""
import pygame
from .assets import (
    ASSET_ROOT,
    BROKEN_ASTEROID_SPECS,
    DAMAGE_SPECS,
    FIRE_SPECS,
    ROCKET_SPECS,
    SHIELD_SPEC,
    SHIP_SPECS,
    ASTEROID_STAGE_SPECS,
    BOSS_SPEC,
    FIREBALL_SPEC,
    SpriteSheetSpec,
    load_sheet,
    load_specs_dict,
    load_specs_list,
    load_powerup_sprites,
)


def load_spritesheet(filepath, cols, rows, sprite_width, sprite_height):
    """Load and split a spritesheet into individual frames."""
    try:
        spritesheet = pygame.image.load(filepath).convert_alpha()
        sprites = []
        for row in range(rows):
            for col in range(cols):
                x = col * sprite_width
                y = row * sprite_height
                sprite = spritesheet.subsurface((x, y, sprite_width, sprite_height))
                sprites.append(sprite.convert_alpha())
        return sprites
    except Exception as e:
        # Fallback placeholder to avoid blank screen if asset missing/failed load
        placeholder = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
        placeholder.fill((255, 0, 255, 200))  # magenta debug color
        print(f"Warning: failed to load {filepath}: {e}. Using placeholder.")
        return [placeholder.copy() for _ in range(cols * rows)]

