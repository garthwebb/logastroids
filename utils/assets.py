"""Sprite sheet specifications and loaders."""
from dataclasses import dataclass
from pathlib import Path
import pygame

ASSET_ROOT = Path(__file__).resolve().parent.parent / "sprite-sheets"


@dataclass(frozen=True)
class SpriteSheetSpec:
    """Declarative description of a sprite sheet grid."""
    key: str
    filename: str
    cols: int
    rows: int
    frame_size: int
    scale: float = 1.0


def _placeholder_frames(spec: SpriteSheetSpec):
    """Return magenta placeholders matching the spec layout/scale."""
    size = int(spec.frame_size * spec.scale)
    placeholder = pygame.Surface((size, size), pygame.SRCALPHA)
    placeholder.fill((255, 0, 255, 200))
    return [placeholder.copy() for _ in range(spec.cols * spec.rows)]


def load_sheet(spec: SpriteSheetSpec, root: Path = ASSET_ROOT):
    """Load and split a sprite sheet based on the provided spec."""
    try:
        sheet = pygame.image.load(root / spec.filename).convert_alpha()
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"Warning: failed to load {root / spec.filename}: {exc}. Using placeholder.")
        return _placeholder_frames(spec)

    frames = []
    for row in range(spec.rows):
        for col in range(spec.cols):
            x = col * spec.frame_size
            y = row * spec.frame_size
            frame = sheet.subsurface((x, y, spec.frame_size, spec.frame_size))
            if spec.scale != 1.0:
                size = int(spec.frame_size * spec.scale)
                frame = pygame.transform.smoothscale(frame, (size, size))
            frames.append(frame.convert_alpha())
    return frames


def load_specs_dict(specs, root: Path = ASSET_ROOT):
    """Load multiple specs into a dict keyed by spec.key."""
    return {spec.key: load_sheet(spec, root) for spec in specs}


def load_specs_list(specs, root: Path = ASSET_ROOT):
    """Load multiple specs into a list preserving the given order."""
    return [load_sheet(spec, root) for spec in specs]


# Power-ups
POWERUP_SPEC = SpriteSheetSpec("powerups", "power-ups-48px-4x1.png", cols=4, rows=1, frame_size=48)


def load_powerup_sprites(root: Path = ASSET_ROOT):
    frames = load_sheet(POWERUP_SPEC, root)
    return {
        "health": frames[0],
        "invulnerability": frames[1],
        "rockets": frames[2],
        "shields": frames[3],
    }


# Ship core sheets
SHIP_SPECS = [
    SpriteSheetSpec("static", "spaceship-static_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("thrust", "spaceship_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
]

# Ship firing variants
FIRE_SPECS = [
    SpriteSheetSpec("fire_thrust_left", "spaceship-fire-left_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("fire_thrust_right", "spaceship-fire-right_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("fire_static_left", "spaceship-static-fire-left_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("fire_static_right", "spaceship-static-fire-right_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
]

# Shield animation
SHIELD_SPEC = SpriteSheetSpec("shield", "shield-96px-3x1.png", cols=3, rows=1, frame_size=96)

# Ship damage progression
DAMAGE_SPECS = [
    SpriteSheetSpec("damage_1", "spaceship-damaged-1_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_2", "spaceship-damaged-2_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_3", "spaceship-damaged-3_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_4", "spaceship-damaged-4_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_5", "spaceship-damaged-5_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_6", "spaceship-damaged-6_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_7", "spaceship-damaged-7_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_8", "spaceship-damaged-8_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_9", "spaceship-damaged-9_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_10", "spaceship-damaged-10_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_11", "spaceship-damaged-11_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("damage_12", "spaceship-damaged-12_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
]

# Asteroid stages and broken debris
ASTEROID_STAGE_SPECS = [
    SpriteSheetSpec("asteroid_stage_1", "icy-asteriod_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("asteroid_stage_2", "green-asteriod_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("asteroid_stage_3", "rocky-asteriod_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("asteroid_stage_4", "motlen-asteriod_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
]

BROKEN_ASTEROID_SPECS = [
    SpriteSheetSpec("broken_1", "broken-asteroid-1_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("broken_2", "broken-asteroid-2_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("broken_3", "broken-asteroid-3_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("broken_4", "broken-asteroid-4_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
]

# Rocket sheets (animation frames, each with 24 rotations)
ROCKET_SPECS = [
    SpriteSheetSpec("rocket_1", "rocket-1_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("rocket_2", "rocket-2_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("rocket_3", "rocket-3_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
    SpriteSheetSpec("rocket_4", "rocket-4_spritesheet-96px-6x4.png", cols=6, rows=4, frame_size=96),
]
