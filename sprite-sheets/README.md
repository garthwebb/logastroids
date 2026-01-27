# Sprite Sheets

This folder contains all the sprite sheet assets used in the Logastroids game. Sprite sheets are organized as grids of animation frames or rotational variations that enable smooth gameplay visuals.

## File Naming Convention

Sprite sheet files follow a consistent naming pattern:

```
<name>-<size>px-<cols>x<rows>.png
```

Where:
- **name**: Descriptive name of the sprite (e.g., `spaceship`, `rocket-1`, `icy-asteroid`)
- **size**: Frame size in pixels (e.g., `96px`, `48px`)
- **cols**: Number of columns in the sprite sheet grid (e.g., `6`)
- **rows**: Number of rows in the sprite sheet grid (e.g., `4`)

### Grid Layout

Most sprite sheets use a **6×4 grid** (24 frames total) with **96px frames**. This layout represents:
- 24 rotational positions (15° increments) for a complete 360° rotation
- Each frame shows the sprite at a different angle, enabling smooth rotation in-game

Special cases:
- **Power-ups**: 4×1 grid with 48px frames (4 different power-up types)
- **Shield**: 3×1 grid with 96px frames (3 animation frames)

## Sprite Sheet Categories

### Spaceship Sprites

**Core Ship States:**
- `spaceship-static_spritesheet-96px-6x4.png` - Spaceship at rest (no thrust)
- `spaceship-96px-6x4.png` - Spaceship with main thrust engaged

**Firing Variants:**
- `spaceship-fire-left_spritesheet-96px-6x4.png` - Firing left weapon with thrust
- `spaceship-fire-right_spritesheet-96px-6x4.png` - Firing right weapon with thrust
- `spaceship-static-fire-left_spritesheet-96px-6x4.png` - Firing left weapon, no thrust
- `spaceship-static-fire-right_spritesheet-96px-6x4.png` - Firing right weapon, no thrust

**Damage Progression (12 stages):**
- `spaceship-damaged-1_spritesheet-96px-6x4.png` through `spaceship-damaged-12_spritesheet-96px-6x4.png`
- Shows increasing damage levels as the ship takes hits
- Higher numbers indicate more severe damage

### Asteroid Sprites

**Main Asteroid Stages (4 types):**
- `icy-asteroid-96px-6x4.png` - Stage 1: Icy asteroid
- `green-asteroid-96px-6x4.png` - Stage 2: Green asteroid
- `rocky-asteroid-96px-6x4.png` - Stage 3: Rocky asteroid
- `molten-asteroid-96px-6x4.png` - Stage 4: Molten asteroid

**Broken Asteroid Debris (4 variants):**
- `broken-asteroid-1_spritesheet-96px-6x4.png`
- `broken-asteroid-2_spritesheet-96px-6x4.png`
- `broken-asteroid-3_spritesheet-96px-6x4.png`
- `broken-asteroid-4_spritesheet-96px-6x4.png`
- These represent fragments created when asteroids are destroyed

### Rocket Projectiles

**Rocket Animation Frames (4 frames):**
- `rocket-1_spritesheet-96px-6x4.png` - Frame 1
- `rocket-2_spritesheet-96px-6x4.png` - Frame 2
- `rocket-3_spritesheet-96px-6x4.png` - Frame 3
- `rocket-4_spritesheet-96px-6x4.png` - Frame 4
- Each sheet contains 24 rotational positions for a single animation frame
- Cycling through frames 1-4 creates the rocket engine animation

### Power-ups

`power-ups-48px-4x1.png` - Contains 4 power-up types in a single row:
1. Health restore
2. Invulnerability
3. Rocket ammunition
4. Shield activation

### Shields

`shield-96px-3x1.png` - Shield animation with 3 frames showing the protective bubble effect

## Technical Details

All rotational sprite sheets (6×4 layouts) are generated using the `scripts/create-sprite-rotations.py` tool, which:
- Takes a source PNG image (facing upward at 0°)
- Rotates it in 15° increments (24 total rotations)
- Arranges the rotations in a 6×4 grid
- Outputs a standardized sprite sheet for use in the game

These assets are loaded by the game engine through the `utils/assets.py` module, which defines specifications for each sprite sheet and handles the parsing of grid layouts.
