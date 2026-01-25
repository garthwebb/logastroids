"""Sprite sheet loading utility."""
import pygame


def load_spritesheet(filepath, cols, rows, sprite_width, sprite_height):
    """Load and split a spritesheet into individual frames"""
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


def load_powerup_sprites():
    """Load power-up sprites from sprite sheet.
    
    Returns:
        dict: Dictionary with keys 'health', 'invulnerability', 'rockets', 'shields'
    """
    sprites = load_spritesheet("sprite-sheets/power-ups-48px-4x1.png", 4, 1, 48, 48)
    
    return {
        'health': sprites[0],
        'invulnerability': sprites[1],
        'rockets': sprites[2],
        'shields': sprites[3],
    }

