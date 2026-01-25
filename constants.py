"""Game constants."""

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
FPS = 60
BULLET_SPEED = 12
BULLET_LIFETIME = 90  # frames
ASTEROID_MIN_SPEED = 1.0
ASTEROID_MAX_SPEED = 3.0
ASTEROID_ROTATION_RANGE = (-3.0, 3.0)

# Level System Constants
LEVEL_1_INITIAL_ASTEROIDS = 5  # Number of asteroids spawned at level start
LEVEL_1_MAX_ON_SCREEN = 5  # Max asteroids on screen at once
LEVEL_1_TOTAL_ASTEROIDS = 10  # Total asteroids to spawn in level
LEVEL_1_SPAWN_INTERVAL = 5.0  # Seconds between spawns
LEVEL_PROGRESSION_INITIAL = 1  # Added to initial asteroids per level
LEVEL_PROGRESSION_MAX = 1  # Added to max on screen per level
LEVEL_PROGRESSION_TOTAL = 1  # Added to total asteroids per level
LEVEL_PROGRESSION_SPAWN_REDUCTION = 0.2  # Seconds reduced from spawn interval per level

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
