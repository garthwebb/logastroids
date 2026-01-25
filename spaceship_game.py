import pygame
import math
import os
import random
import json

# Initialize Pygame
pygame.init()

# Constants
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

class Spaceship(pygame.sprite.Sprite):
    """Spaceship with asteroid-like movement physics"""
    
    def __init__(self, *groups,
                 sprites_static=None, sprites_thrust=None, damage_sprites=None, shield_sprites=None,
                 fire_thrust_left=None, fire_thrust_right=None, fire_static_left=None, fire_static_right=None,
                 x=None, y=None, spawn_shield=120, sprite_radius=32):
        super().__init__(*groups)
        self.sprites_static = sprites_static or []  # List of rotated sprite frames without thrust
        self.sprites_thrust = sprites_thrust or []  # List of rotated sprite frames with thrust
        # Firing sprite variants
        self.sprites_fire_thrust_left = fire_thrust_left or []
        self.sprites_fire_thrust_right = fire_thrust_right or []
        self.sprites_fire_static_left = fire_static_left or []
        self.sprites_fire_static_right = fire_static_right or []
        self.damage_sprites = damage_sprites or []  # List of damage stage sprite sheets
        self.shield_sprites = shield_sprites or []  # List of shield animation frames
        self.current_frame = 0
        # Provide a safe placeholder if assets are missing
        if self.sprites_static:
            self.image = self.sprites_static[self.current_frame]
        else:
            self.image = pygame.Surface((96, 96), pygame.SRCALPHA)
            self.image.fill((255, 0, 255, 200))
        self.rect = self.image.get_rect(center=(x or 0, y or 0))
        self.radius = sprite_radius  # For circle-based collision
        self.max_health = 3
        self.health = self.max_health
        
        # Physics
        self.x = float(x or 0)
        self.y = float(y or 0)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.rotation = 0  # 0 degrees = pointing up
        self.angular_velocity = 0.0
        
        # Controls
        self.is_rotating_left = False
        self.is_rotating_right = False
        self.is_thrusting = False
        self.fire_cooldown = 0
        # Firing state
        self.fire_side = 'left'  # alternate between 'left' and 'right'
        self.firing_timer = 0
        self.firing_duration = 10  # frames to display firing animation
        
        # Damage state
        self.damage_level = 0  # 0 = healthy, 1+ = damaged stages
        self.is_exploding = False
        self.explosion_tick = 0
        self.explosion_frame = 0
        self.spawn_shield = spawn_shield  # Temporary invulnerability after spawn
        
        # Shield animation
        self.shield_active = False
        self.shield_frame = 0
        self.shield_timer = 0
        self.shield_duration = 30  # frames to show shield animation
        self.hit_invulnerability = 0  # Brief invulnerability after taking damage
        
        # Physics constants
        self.rotation_speed = 6.0  # degrees per frame
        self.acceleration = 0.5  # pixels per frame^2
        self.max_velocity = 10.0
        self.friction = 0.99  # Slight friction in space
        
    def handle_input(self, keys):
        """Handle keyboard input"""
        self.is_rotating_left = keys[pygame.K_LEFT]
        self.is_rotating_right = keys[pygame.K_RIGHT]
        self.is_thrusting = keys[pygame.K_UP]
        # Fire cooldown ticks down while holding space
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
    
    def update(self):
        """Update spaceship position and rotation"""
        # If exploding, skip movement/control updates but handle explosion animation
        if self.is_exploding:
            alive = self.update_explosion()
            if alive:
                self._update_sprite()
            if not alive:
                self.kill()
            if self.rect:
                self.rect.center = (int(self.x), int(self.y))
            return
        
        # Handle rotation
        if self.is_rotating_left:
            self.rotation = (self.rotation - self.rotation_speed) % 360
        if self.is_rotating_right:
            self.rotation = (self.rotation + self.rotation_speed) % 360
        
        # Handle thrust
        if self.is_thrusting:
            # Convert rotation to radians (0 degrees is up, so we use -90 offset)
            rad = math.radians(self.rotation - 90)
            self.velocity_x += self.acceleration * math.cos(rad)
            self.velocity_y += self.acceleration * math.sin(rad)
            
            # Limit velocity
            velocity_magnitude = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            if velocity_magnitude > self.max_velocity:
                scale = self.max_velocity / velocity_magnitude
                self.velocity_x *= scale
                self.velocity_y *= scale
        
        # Apply friction (subtle in space)
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Screen wrapping
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
            
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        elif self.y > WINDOW_HEIGHT:
            self.y = 0
        
        # Update sprite based on rotation
        self._update_sprite()
        
        # Update rect position
        if self.rect:
            self.rect.center = (int(self.x), int(self.y))

        # Decrease firing timer
        if self.firing_timer > 0:
            self.firing_timer -= 1

        # Decrease spawn shield timer
        if self.spawn_shield > 0:
            self.spawn_shield -= 1
        
        # Decrease hit invulnerability timer
        if self.hit_invulnerability > 0:
            self.hit_invulnerability -= 1
        
        # Update shield animation
        if self.shield_active:
            self.shield_timer -= 1
            # Cycle through shield frames (3 frames total)
            if self.shield_timer % 10 == 0:
                self.shield_frame = (self.shield_frame + 1) % len(self.shield_sprites)
            if self.shield_timer <= 0:
                self.shield_active = False
    
    def _update_sprite(self):
        """Update sprite frame based on current rotation, thrust state, and damage"""
        if self.is_exploding:
            # Show damage progression animation
            sheet = self.damage_sprites[self.explosion_frame]
            num_frames = len(sheet)
            frame_index = int((self.rotation / 360.0) * num_frames) % num_frames
            self.image = sheet[frame_index]
        else:
            # Choose sprite set based on firing and thrust state
            if self.firing_timer > 0:
                if self.is_thrusting:
                    active_sprites = self.sprites_fire_thrust_left if self.fire_side == 'left' else self.sprites_fire_thrust_right
                else:
                    active_sprites = self.sprites_fire_static_left if self.fire_side == 'left' else self.sprites_fire_static_right
            else:
                active_sprites = self.sprites_thrust if self.is_thrusting else self.sprites_static

            # Map rotation (0-360) to sprite frame (0-23 for 24 directions)
            num_frames = len(active_sprites)
            frame_index = int((self.rotation / 360.0) * num_frames) % num_frames
            self.current_frame = frame_index
            self.image = active_sprites[self.current_frame]

    def fire(self):
        """Create a bullet traveling in the ship's facing direction."""
        if self.fire_cooldown > 0 or self.is_exploding:
            return None
        # Quantize firing direction to the current sprite frame so bullets align with visible facing
        frame_count = len(self.sprites_static) if self.sprites_static else 0
        if frame_count <= 0:
            frame_count = 24
        frame_step = 360.0 / frame_count
        quantized_rotation = self.current_frame * frame_step
        rad = math.radians(quantized_rotation - 90)
        dir_x = math.cos(rad)
        dir_y = math.sin(rad)
        # Alternate gun origin offset left/right for visual polish
        # Perpendicular vector to forward direction
        perp_x = -dir_y
        perp_y = dir_x
        gun_offset = 20
        side_mult = 1 if self.fire_side == 'left' else -1
        origin_x = self.rect.centerx + dir_x * 20 + perp_x * gun_offset * side_mult
        origin_y = self.rect.centery + dir_y * 20 + perp_y * gun_offset * side_mult
        bullet = Bullet(origin_x, origin_y, dir_x * BULLET_SPEED, dir_y * BULLET_SPEED)
        self.fire_cooldown = 8  # small delay between shots
        # Trigger firing animation and alternate side
        self.firing_timer = self.firing_duration
        self.fire_side = 'right' if self.fire_side == 'left' else 'left'
        return bullet
    
    def take_damage(self, asteroid=None):
        """Spaceship gets hit by an asteroid. Decrement shields; explode when depleted."""
        if self.spawn_shield > 0 or self.is_exploding or self.hit_invulnerability > 0:
            return
        self.health -= 1
        if self.health <= 0:
            # Ship destroyed - no shield animation
            self.is_exploding = True
            self.explosion_tick = 0
            self.explosion_frame = 0
        else:
            # Ship survived - show shield animation and add brief invulnerability
            self.shield_active = True
            self.shield_timer = self.shield_duration
            self.shield_frame = 0
            self.hit_invulnerability = 20  # 20 frames of invulnerability to prevent rapid hits
            
            # Apply elastic collision between ship and asteroid
            if asteroid:
                # Calculate collision normal (from asteroid to ship)
                dx = self.x - asteroid.x
                dy = self.y - asteroid.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance > 0:
                    # Normalize collision normal
                    nx = dx / distance
                    ny = dy / distance
                    
                    # Calculate relative velocity along collision normal
                    dvx = self.velocity_x - asteroid.vx
                    dvy = self.velocity_y - asteroid.vy
                    relative_vel = dvx * nx + dvy * ny
                    
                    # Only apply impulse if objects are moving toward each other
                    if relative_vel < 0:
                        # Elastic collision with equal masses and some energy loss
                        restitution = 0.6  # Coefficient of restitution (0.6 = somewhat elastic)
                        impulse = -(1 + restitution) * relative_vel / 2
                        
                        # Apply impulse to both objects
                        self.velocity_x += impulse * nx
                        self.velocity_y += impulse * ny
                        asteroid.vx -= impulse * nx
                        asteroid.vy -= impulse * ny
    
    def update_explosion(self):
        """Update explosion animation. Returns True if still alive, False if destroyed."""
        self.explosion_tick += 1
        if self.explosion_tick % 3 == 0:  # Frame hold of 3 ticks per damage stage
            self.explosion_frame += 1
            if self.explosion_frame >= len(self.damage_sprites):
                return False  # Fully destroyed
        return True
    
    def draw(self, surface):
        """Draw the spaceship"""
        surface.blit(self.image, self.rect)
        # Draw shield animation if active
        if self.shield_active and self.shield_sprites:
            shield_img = self.shield_sprites[self.shield_frame]
            # Center the shield on the spaceship
            shield_rect = shield_img.get_rect(center=self.rect.center)
            surface.blit(shield_img, shield_rect)


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


class Bullet(pygame.sprite.Sprite):
    """Simple bullet shot from the spaceship."""

    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (2, 2), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.life = BULLET_LIFETIME

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Screen wrap for bullets to keep gameplay consistent
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
        self.life -= 1
        if self.life <= 0:
            self.kill()


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


class Explosion(pygame.sprite.Sprite):
    """Explosion that keeps drifting and spinning with the destroyed asteroid."""

    def __init__(self, broken_sheets, x, y, rotation_angle, rotation_speed, vx, vy, frame_hold=4):
        super().__init__()
        self.broken_sheets = broken_sheets  # list of directional sheets
        self.frame_hold = frame_hold
        self.tick = 0
        self.frame_index = 0
        self.rotation = rotation_angle
        self.rotation_speed = rotation_speed
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.image = None
        self.rect = None
        self._set_image()

    def _set_image(self):
        sheet = self.broken_sheets[self.frame_index]
        num_frames = len(sheet)
        dir_index = int((self.rotation / 360.0) * num_frames) % num_frames
        self.image = sheet[dir_index]
        if self.rect:
            center = self.rect.center
            self.rect = self.image.get_rect(center=center)
        else:
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        # Drift forward with preserved velocity
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

        # Keep spinning to animate directional shards
        self.rotation = (self.rotation + self.rotation_speed) % 360

        self.tick += 1
        if self.tick % self.frame_hold == 0:
            self.frame_index += 1
            if self.frame_index >= len(self.broken_sheets):
                self.kill()
                return
            self._set_image()
        else:
            # Update frame for current rotation even within the same explosion stage
            self._set_image()


def draw_health(surface, health, max_segments=3, position=(10, 10), size=(30, 10), gap=6):
    """Draw a segmented health (shield) bar."""
    x, y = position
    w, h = size
    for i in range(max_segments):
        color = (0, 220, 120) if i < health else (70, 70, 70)
        pygame.draw.rect(surface, color, (x + i * (w + gap), y, w, h), border_radius=3)
        pygame.draw.rect(surface, (20, 20, 20), (x + i * (w + gap), y, w, h), width=1, border_radius=3)


def draw_score(surface, score, position=None):
    """Draw the score counter in the upper right."""
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    if position is None:
        # Default to upper right with padding
        position = (WINDOW_WIDTH - text.get_width() - 10, 10)
    surface.blit(text, position)


def draw_level(surface, level, position=None):
    """Draw the level counter."""
    font = pygame.font.Font(None, 36)
    text = font.render(f"Level: {level}", True, WHITE)
    if position is None:
        # Default to upper center
        position = (WINDOW_WIDTH // 2 - text.get_width() // 2, 10)
    surface.blit(text, position)


def draw_game_over(surface, score, high_scores, entering_name=False, current_name=""):
    """Draw game over screen with score and restart prompt."""
    # Game Over title
    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("GAME OVER", True, WHITE)
    title_pos = (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 50)
    surface.blit(title_text, title_pos)
    
    # Score display
    score_font = pygame.font.Font(None, 48)
    score_text = score_font.render(f"Final Score: {score}", True, WHITE)
    score_pos = (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 120)
    surface.blit(score_text, score_pos)
    
    if entering_name:
        # Show name entry
        draw_name_entry(surface, current_name, 200)
    else:
        # Show high scores
        draw_high_scores(surface, high_scores, 200)
        
        # Restart prompt
        prompt_font = pygame.font.Font(None, 36)
        prompt_text = prompt_font.render("Press 'P' to play again", True, WHITE)
        prompt_pos = (WINDOW_WIDTH // 2 - prompt_text.get_width() // 2, WINDOW_HEIGHT - 100)
        surface.blit(prompt_text, prompt_pos)


def draw_start_screen(surface):
    """Draw start screen with game title and start prompt."""
    # Game title
    title_font = pygame.font.Font(None, 96)
    title_text = title_font.render("Logastroids", True, WHITE)
    title_pos = (WINDOW_WIDTH // 2 - title_text.get_width() // 2, WINDOW_HEIGHT // 3)
    surface.blit(title_text, title_pos)
    
    # Start prompt
    prompt_font = pygame.font.Font(None, 36)
    prompt_text = prompt_font.render("Press 'P' to start", True, WHITE)
    prompt_pos = (WINDOW_WIDTH // 2 - prompt_text.get_width() // 2, WINDOW_HEIGHT // 2 + 100)
    surface.blit(prompt_text, prompt_pos)


def load_high_scores(filename="high_scores.json"):
    """Load high scores from file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_high_scores(scores, filename="high_scores.json"):
    """Save high scores to file."""
    with open(filename, 'w') as f:
        json.dump(scores, f)


def is_high_score(score, high_scores, max_entries=10):
    """Check if score qualifies for the high score list."""
    if len(high_scores) < max_entries:
        return True
    return score > min(s['score'] for s in high_scores)


def add_high_score(name, score, high_scores, max_entries=10):
    """Add a new high score and return updated list."""
    high_scores.append({'name': name, 'score': score})
    high_scores.sort(key=lambda x: x['score'], reverse=True)
    return high_scores[:max_entries]


def draw_high_scores(surface, high_scores, y_start=250):
    """Draw the high scores table with formatted layout."""
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("HIGH SCORES", True, WHITE)
    title_pos = (WINDOW_WIDTH // 2 - title_text.get_width() // 2, y_start)
    surface.blit(title_text, title_pos)
    
    # Calculate padding (30% of screen width on each side)
    padding = int(WINDOW_WIDTH * 0.3)
    usable_width = WINDOW_WIDTH - (2 * padding)
    
    score_font = pygame.font.Font(None, 32)
    y_offset = y_start + 50
    
    for i, entry in enumerate(high_scores[:10]):
        rank = f"{i + 1}."
        name = entry['name'][:12]  # Ensure max 12 characters
        score_val = str(entry['score'])
        
        # Draw rank and name on left
        left_text = f"{rank} {name}"
        left_surface = score_font.render(left_text, True, WHITE)
        left_x = padding
        
        # Draw score on right
        right_surface = score_font.render(score_val, True, WHITE)
        right_x = WINDOW_WIDTH - padding - right_surface.get_width()
        
        # Calculate dots width
        dots_start_x = left_x + left_surface.get_width() + 10
        dots_end_x = right_x - 10
        dots_width = dots_end_x - dots_start_x
        
        # Create dots string to fill the space
        dot_char = "."
        dot_width = score_font.size(dot_char)[0]
        num_dots = max(0, int(dots_width / dot_width))
        dots = dot_char * num_dots
        
        y_pos = y_offset + i * 35
        
        # Draw all parts
        surface.blit(left_surface, (left_x, y_pos))
        if num_dots > 0:
            dots_surface = score_font.render(dots, True, (100, 100, 100))  # Gray dots
            surface.blit(dots_surface, (dots_start_x, y_pos))
        surface.blit(right_surface, (right_x, y_pos))


def draw_name_entry(surface, current_name, y_pos=400):
    """Draw name entry prompt in a centered floating box."""
    # Create semi-transparent background box
    box_width = 600
    box_height = 200
    box_x = (WINDOW_WIDTH - box_width) // 2
    box_y = (WINDOW_HEIGHT - box_height) // 2
    
    # Draw background with border
    background = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    background.fill((0, 0, 0, 220))  # Semi-transparent black
    surface.blit(background, (box_x, box_y))
    pygame.draw.rect(surface, WHITE, (box_x, box_y, box_width, box_height), 3, border_radius=10)
    
    # Draw prompt text
    prompt_font = pygame.font.Font(None, 36)
    prompt_text = prompt_font.render("NEW HIGH SCORE!", True, WHITE)
    prompt_pos = (WINDOW_WIDTH // 2 - prompt_text.get_width() // 2, box_y + 30)
    surface.blit(prompt_text, prompt_pos)
    
    # Draw input box
    input_font = pygame.font.Font(None, 48)
    input_text = input_font.render(current_name + "_", True, WHITE)
    input_pos = (WINDOW_WIDTH // 2 - input_text.get_width() // 2, box_y + 80)
    surface.blit(input_text, input_pos)
    
    # Draw instruction
    inst_font = pygame.font.Font(None, 24)
    inst_text = inst_font.render("Enter your name and press ENTER (12 chars max)", True, (200, 200, 200))
    inst_pos = (WINDOW_WIDTH // 2 - inst_text.get_width() // 2, box_y + 140)
    surface.blit(inst_text, inst_pos)


def main():
    """Main game loop"""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Asteroid-Style Spaceship Game")
    clock = pygame.time.Clock()
    
    # Load spritesheets
    script_dir = os.path.dirname(__file__)
    cols, rows = 6, 4
    sprite_width, sprite_height = 96, 96
    sprite_static_path = os.path.join(script_dir, "sprite-sheets", "spaceship-static_spritesheet-96px-6x4.png")
    sprite_thrust_path = os.path.join(script_dir, "sprite-sheets", "spaceship_spritesheet-96px-6x4.png")
    sprites_static = load_spritesheet(sprite_static_path, cols, rows, sprite_width, sprite_height)
    sprites_thrust = load_spritesheet(sprite_thrust_path, cols, rows, sprite_width, sprite_height)
    if not sprites_static or not sprites_thrust:
        print("Warning: spaceship sprites failed to load; using placeholders.")

    # Load firing sprite variants (left/right for thrusting and static)
    fire_thrust_left_path = os.path.join(script_dir, "sprite-sheets", "spaceship-fire-left_spritesheet-96px-6x4.png")
    fire_thrust_right_path = os.path.join(script_dir, "sprite-sheets", "spaceship-fire-right_spritesheet-96px-6x4.png")
    fire_static_left_path = os.path.join(script_dir, "sprite-sheets", "spaceship-static-fire-left_spritesheet-96px-6x4.png")
    fire_static_right_path = os.path.join(script_dir, "sprite-sheets", "spaceship-static-fire-right_spritesheet-96px-6x4.png")
    sprites_fire_thrust_left = load_spritesheet(fire_thrust_left_path, cols, rows, sprite_width, sprite_height)
    sprites_fire_thrust_right = load_spritesheet(fire_thrust_right_path, cols, rows, sprite_width, sprite_height)
    sprites_fire_static_left = load_spritesheet(fire_static_left_path, cols, rows, sprite_width, sprite_height)
    sprites_fire_static_right = load_spritesheet(fire_static_right_path, cols, rows, sprite_width, sprite_height)
    
    # Load shield animation
    shield_path = os.path.join(script_dir, "sprite-sheets", "shield-96px-3x1.png")
    shield_sprites = load_spritesheet(shield_path, 3, 1, sprite_width, sprite_height)
    if not shield_sprites:
        print("Warning: shield sprites failed to load; using placeholder.")
        placeholder = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
        placeholder.fill((100, 200, 255, 150))
        shield_sprites = [placeholder.copy() for _ in range(3)]

    # Load spaceship damage progression sprites
    damage_sheet_names = [
        "spaceship-damaged-1_spritesheet-96px-6x4.png",
        "spaceship-damaged-2_spritesheet-96px-6x4.png",
        "spaceship-damaged-3_spritesheet-96px-6x4.png",
        "spaceship-damaged-4_spritesheet-96px-6x4.png",
        "spaceship-damaged-5_spritesheet-96px-6x4.png",
        "spaceship-damaged-6_spritesheet-96px-6x4.png",
        "spaceship-damaged-7_spritesheet-96px-6x4.png",
        "spaceship-damaged-8_spritesheet-96px-6x4.png",
        "spaceship-damaged-9_spritesheet-96px-6x4.png",
        "spaceship-damaged-10_spritesheet-96px-6x4.png",
        "spaceship-damaged-11_spritesheet-96px-6x4.png",
        "spaceship-damaged-12_spritesheet-96px-6x4.png",
    ]
    damage_sprites = []
    for name in damage_sheet_names:
        damage_sprites.append(load_spritesheet(os.path.join(script_dir, "sprite-sheets", name), cols, rows, sprite_width, sprite_height))
    if not damage_sprites:
        # Ensure we always have something to animate
        placeholder = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
        placeholder.fill((255, 128, 0, 220))
        damage_sprites = [[placeholder.copy() for _ in range(cols * rows)]]

    # Asteroid stages and explosion frames (using actual filenames present)
    asteroid_stage_names = [
        "icy-asteriod_spritesheet-96px-6x4.png",
        "green-asteriod_spritesheet-96px-6x4.png",
        "rocky-asteriod_spritesheet-96px-6x4.png",
        "motlen-asteriod_spritesheet-96px-6x4.png",
    ]
    asteroid_stage_sheets = [
        load_spritesheet(os.path.join(script_dir, "sprite-sheets", name), cols, rows, sprite_width, sprite_height)
        for name in asteroid_stage_names
    ]
    broken_sheet_names = [
        "broken-asteroid-1_spritesheet-96px-6x4.png",
        "broken-asteroid-2_spritesheet-96px-6x4.png",
        "broken-asteroid-3_spritesheet-96px-6x4.png",
        "broken-asteroid-4_spritesheet-96px-6x4.png",
    ]
    broken_sheets = [
        load_spritesheet(os.path.join(script_dir, "sprite-sheets", name), cols, rows, sprite_width, sprite_height)
        for name in broken_sheet_names
    ]

    # Create spaceship
    spaceship = Spaceship(
        sprites_static=sprites_static,
        sprites_thrust=sprites_thrust,
        damage_sprites=damage_sprites,
        shield_sprites=shield_sprites,
        fire_thrust_left=sprites_fire_thrust_left,
        fire_thrust_right=sprites_fire_thrust_right,
        fire_static_left=sprites_fire_static_left,
        fire_static_right=sprites_fire_static_right,
        x=WINDOW_WIDTH // 2,
        y=WINDOW_HEIGHT // 2,
    )

    # Sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    explosions = pygame.sprite.Group()

    all_sprites.add(spaceship)

    def spawn_asteroid():
        # Spawn asteroids off-screen and have them float in
        spawn_margin = 100  # Distance off-screen to spawn
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        
        if edge == 'top':
            x = random.uniform(0, WINDOW_WIDTH)
            y = -spawn_margin
        elif edge == 'bottom':
            x = random.uniform(0, WINDOW_WIDTH)
            y = WINDOW_HEIGHT + spawn_margin
        elif edge == 'left':
            x = -spawn_margin
            y = random.uniform(0, WINDOW_HEIGHT)
        else:  # right
            x = WINDOW_WIDTH + spawn_margin
            y = random.uniform(0, WINDOW_HEIGHT)
        
        # Give velocity directed generally toward the screen center
        center_x = WINDOW_WIDTH / 2
        center_y = WINDOW_HEIGHT / 2
        dx = center_x - x
        dy = center_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            # Normalize direction toward center
            dir_x = dx / dist
            dir_y = dy / dist
        else:
            dir_x, dir_y = 0, 0
        
        # Random speed with inward component
        speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        vx = dir_x * speed
        vy = dir_y * speed
        
        rotation = random.uniform(0, 360)
        rotation_speed = random.uniform(*ASTEROID_ROTATION_RANGE)
        # Ensure some spin
        if abs(rotation_speed) < 0.3:
            rotation_speed = 0.3 if rotation_speed >= 0 else -0.3
        asteroid = Asteroid(asteroid_stage_sheets, 0, x, y, vx, vy, rotation, rotation_speed)
        asteroids.add(asteroid)
        all_sprites.add(asteroid)

    def create_explosion(x, y, rotation_angle, rotation_speed, vx, vy):
        # Use directional sheets so shards keep rotating and drifting
        explosion = Explosion(broken_sheets, x, y, rotation_angle, rotation_speed, vx, vy)
        explosions.add(explosion)
        all_sprites.add(explosion)

    # Level system
    current_level = 1
    asteroids_spawned_this_level = 0
    asteroids_destroyed_this_level = 0
    
    # Calculate level-based values
    def get_level_params(level):
        initial = LEVEL_1_INITIAL_ASTEROIDS + (level - 1) * LEVEL_PROGRESSION_INITIAL
        max_on_screen = LEVEL_1_MAX_ON_SCREEN + (level - 1) * LEVEL_PROGRESSION_MAX
        total = LEVEL_1_TOTAL_ASTEROIDS + (level - 1) * LEVEL_PROGRESSION_TOTAL
        spawn_interval = max(1.0, LEVEL_1_SPAWN_INTERVAL - (level - 1) * LEVEL_PROGRESSION_SPAWN_REDUCTION)
        return initial, max_on_screen, total, spawn_interval
    
    initial_asteroids, max_asteroids, total_asteroids, spawn_interval_seconds = get_level_params(current_level)
    spawn_interval_frames = int(spawn_interval_seconds * FPS)
    
    # Seed initial asteroids for level 1
    for _ in range(initial_asteroids):
        spawn_asteroid()
        asteroids_spawned_this_level += 1
    
    spawn_timer = 0
    respawn_timer = 0  # Timer for respawning after destruction
    RESPAWN_DELAY = 180  # 3 seconds at 60 FPS
    spaceship_destroyed_pos = None  # Store position when destroyed
    score = 0  # Track player score
    game_over = False  # Game over state
    game_started = False  # Game started state
    high_scores = load_high_scores()  # Load high scores
    entering_name = False  # Name entry state
    player_name = ""  # Current name being entered
    running = True
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if entering_name:
                    # Handle name entry
                    if event.key == pygame.K_RETURN:
                        # Save high score
                        if player_name.strip():  # Only save if name is not empty
                            high_scores = add_high_score(player_name.strip(), score, high_scores)
                            save_high_scores(high_scores)
                        entering_name = False
                        player_name = ""
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif len(player_name) < 12 and event.unicode.isprintable():
                        player_name += event.unicode
                elif event.key == pygame.K_SPACE and not game_over and game_started:
                    bullet = spaceship.fire()
                    if bullet:
                        bullets.add(bullet)
                        all_sprites.add(bullet)
                elif event.key == pygame.K_p:
                    if not game_started:
                        # Start the game
                        game_started = True
                    elif game_over and not entering_name:
                        # Restart the game (only if not entering name)
                        game_over = False
                        current_level = 1
                        asteroids_spawned_this_level = 0
                        asteroids_destroyed_this_level = 0
                        score = 0
                        entering_name = False
                        player_name = ""
                        
                        # Clear all sprites
                        all_sprites.empty()
                        bullets.empty()
                        asteroids.empty()
                        explosions.empty()
                        
                        # Reset level parameters
                        initial_asteroids, max_asteroids, total_asteroids, spawn_interval_seconds = get_level_params(current_level)
                        spawn_interval_frames = int(spawn_interval_seconds * FPS)
                        
                        # Create new spaceship
                        spaceship = Spaceship(
                            sprites_static=sprites_static,
                            sprites_thrust=sprites_thrust,
                            damage_sprites=damage_sprites,
                            shield_sprites=shield_sprites,
                            fire_thrust_left=sprites_fire_thrust_left,
                            fire_thrust_right=sprites_fire_thrust_right,
                            fire_static_left=sprites_fire_static_left,
                            fire_static_right=sprites_fire_static_right,
                            x=WINDOW_WIDTH // 2,
                            y=WINDOW_HEIGHT // 2,
                        )
                        all_sprites.add(spaceship)
                        
                        # Spawn initial asteroids
                        for _ in range(initial_asteroids):
                            spawn_asteroid()
                            asteroids_spawned_this_level += 1
                        spawn_timer = 0
                        respawn_timer = 0
        
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Check for ESC to quit
        if keys[pygame.K_ESCAPE]:
            running = False
        
        # Show start screen if game hasn't started
        if not game_started:
            screen.fill(BLACK)
            draw_start_screen(screen)
            pygame.display.flip()
            continue
        
        # Skip updates if game over
        if game_over:
            screen.fill(BLACK)
            draw_game_over(screen, score, high_scores, entering_name, player_name)
            pygame.display.flip()
            continue
        
        # Update
        spaceship.handle_input(keys)
        all_sprites.update()

        # Bullet vs asteroid collisions
        for asteroid in pygame.sprite.groupcollide(asteroids, bullets, False, True):
            alive = asteroid.advance_stage()
            score += 1  # 1 point per asteroid hit
            if not alive:
                score += 10  # 10 bonus points for destroying asteroid
                asteroids_destroyed_this_level += 1
                create_explosion(asteroid.x, asteroid.y, asteroid.rotation, asteroid.rotation_speed, asteroid.vx, asteroid.vy)
                
                # Spawn child asteroids if this is a parent asteroid and level >= 3
                if asteroid.spawn_children and asteroid.scale == 1.0 and current_level >= 3:
                    # Spawn 3 smaller asteroids at the rocky stage (index 2)
                    child_scale = 0.5  # 1/2 size
                    for i in range(3):
                        # Spread them out in different directions
                        angle = (i * 120) * math.pi / 180  # 0°, 120°, 240°
                        child_speed = 2.0
                        child_vx = asteroid.vx + math.cos(angle) * child_speed
                        child_vy = asteroid.vy + math.sin(angle) * child_speed
                        
                        # Slight offset from parent position to avoid overlap
                        offset_dist = 30
                        child_x = asteroid.x + math.cos(angle) * offset_dist
                        child_y = asteroid.y + math.sin(angle) * offset_dist
                        
                        # Create child asteroid at rocky stage (stage 2), scaled down, no further children
                        child_asteroid = Asteroid(asteroid_stage_sheets, 2, child_x, child_y, child_vx, child_vy, 
                                                 random.uniform(0, 360), random.uniform(*ASTEROID_ROTATION_RANGE),
                                                 scale=child_scale, spawn_children=False)
                        asteroids.add(child_asteroid)
                        all_sprites.add(child_asteroid)
                
                asteroid.kill()
                
                # Spawn a new asteroid immediately when one is destroyed (if limits allow)
                if (len(asteroids) < max_asteroids and 
                    asteroids_spawned_this_level < total_asteroids):
                    spawn_asteroid()
                    asteroids_spawned_this_level += 1
                    spawn_timer = 0  # Reset timer after spawning
        
        # Check for level completion
        if (asteroids_destroyed_this_level >= total_asteroids and 
            len(asteroids) == 0 and 
            len(explosions) == 0):
            # Level complete! Advance to next level
            current_level += 1
            asteroids_spawned_this_level = 0
            asteroids_destroyed_this_level = 0
            
            # Get new level parameters
            initial_asteroids, max_asteroids, total_asteroids, spawn_interval_seconds = get_level_params(current_level)
            spawn_interval_frames = int(spawn_interval_seconds * FPS)
            
            # Spawn initial asteroids for new level
            for _ in range(initial_asteroids):
                spawn_asteroid()
                asteroids_spawned_this_level += 1
            spawn_timer = 0
        
        # Asteroid vs spaceship collisions
        if not spaceship.is_exploding and spaceship.spawn_shield <= 0:
            for asteroid in pygame.sprite.spritecollide(spaceship, asteroids, False, pygame.sprite.collide_circle):
                spaceship.take_damage(asteroid)

        # Maintain asteroid population based on level
        spawn_timer += 1
        if (spawn_timer >= spawn_interval_frames and 
            len(asteroids) < max_asteroids and 
            asteroids_spawned_this_level < total_asteroids):
            spawn_asteroid()
            asteroids_spawned_this_level += 1
            spawn_timer = 0
        
        # Handle spaceship destruction and game over
        if spaceship not in all_sprites and respawn_timer == 0:
            # Ship just destroyed - game over
            game_over = True
            # Check if player got a high score
            if is_high_score(score, high_scores):
                entering_name = True
                player_name = ""
        # Draw
        screen.fill(BLACK)
        # Draw bullets, asteroids, and explosions
        bullets.draw(screen)
        asteroids.draw(screen)
        explosions.draw(screen)
        # Draw spaceship with custom draw method (for shield animation)
        if spaceship in all_sprites:
            spaceship.draw(screen)
        # HUD: health segments
        draw_health(screen, spaceship.health if spaceship in all_sprites else 0, max_segments=3)
        # HUD: score counter
        draw_score(screen, score)
        # HUD: level counter
        draw_level(screen, current_level)

        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
