"""Game constants."""

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
FPS = 60
BULLET_SPEED = 12
BULLET_LIFETIME = 90  # frames
SHIP_DRIFT_DECAY = 0.99  # Ship drift slowdown when not thrusting (closer to 1.0 = longer drift, closer to 0.0 = stops quickly)
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

# Power-up Constants
MAX_SHIELDS = 6  # Maximum shield bars the spaceship can have
INVULNERABILITY_DURATION = 5  # Seconds of invulnerability
NUM_ROCKETS_PER_PICKUP = 3  # Rockets given per power-up pickup
POWERUP_SPEED = 2.0  # Speed at which power-ups float down
UNLIMITED_ROCKETS = False  # If True, rockets can be fired infinitely; if False, requires power-up pickup
ROCKET_SCALE = 0.75  # Scale factor for rocket sprite size (1.0 = original 48px, 1.5 = 72px)
ROCKET_SPEED_MULTIPLIER = 1.0  # Speed multiplier relative to BULLET_SPEED (was 1.5)

# Power-up Spawn Chances (when asteroid is destroyed)
# First roll: chance that any power-up drops
POWERUP_SPAWN_CHANCE = 0.20  # 20% chance a destroyed asteroid drops a power-up
# Second roll (weights must sum to 1.0) to pick which power-up drops
HEALTH_POWERUP_WEIGHT = 0.10
INVULNERABILITY_POWERUP_WEIGHT = 0.20
ROCKETS_POWERUP_WEIGHT = 0.20
SHIELDS_POWERUP_WEIGHT = 0.50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
