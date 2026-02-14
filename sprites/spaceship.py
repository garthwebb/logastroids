"""Spaceship sprite class."""
import pygame
import math
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, BULLET_SPEED, SHIP_DRIFT_DECAY, MAX_SHIELDS, UNLIMITED_ROCKETS, ROCKET_SPEED_MULTIPLIER
from sprites.bullet import Bullet
from sprites.rocket import Rocket


class Spaceship(pygame.sprite.Sprite):
    """Spaceship with asteroid-like movement physics"""
    
    def __init__(self, *groups,
                 sprites_static=None, sprites_thrust=None, damage_sprites=None, shield_sprites=None,
                 fire_thrust_left=None, fire_thrust_right=None, fire_static_left=None, fire_static_right=None,
                 rocket_sheets=None, shield_hit_sound=None, ship_destroyed_sound=None, rocket_sound=None,
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
        self.rocket_sheets = rocket_sheets or []  # List of 4 rocket animation sheets
        self.shield_hit_sound = shield_hit_sound  # Sound to play when shields get hit
        self.ship_destroyed_sound = ship_destroyed_sound  # Sound to play when ship is destroyed
        self.rocket_sound = rocket_sound  # Sound to play when launching rockets
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
        
        # Power-up system
        self.invulnerability_time = 0  # frames remaining of invulnerability
        self.rockets = 0  # Number of rockets available
        
        # Physics constants
        self.rotation_speed = 6.0  # degrees per frame
        self.acceleration = 0.5  # pixels per frame^2
        self.max_velocity = 10.0
        self.drift_decay = SHIP_DRIFT_DECAY
        
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
            # Continue drifting with current velocity during explosion
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
        else:
            # Apply drift decay only when not thrusting
            self.velocity_x *= self.drift_decay
            self.velocity_y *= self.drift_decay
        
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
        
        # Decrease invulnerability timer (from power-ups)
        if self.invulnerability_time > 0:
            self.invulnerability_time -= 1
        
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
    
    def fire_rocket(self):
        """Create a rocket traveling in the ship's facing direction. Consumes a rocket (unless UNLIMITED_ROCKETS)."""
        # Check if we can fire: need rockets or unlimited mode enabled
        if not UNLIMITED_ROCKETS and self.rockets <= 0:
            return None
        if self.fire_cooldown > 0 or self.is_exploding:
            return None
        
        # Play rocket launch sound
        if self.rocket_sound:
            self.rocket_sound.play()
        
        # Consume a rocket if not in unlimited mode
        if not UNLIMITED_ROCKETS:
            self.rockets -= 1
        
        frame_count = len(self.sprites_static) if self.sprites_static else 0
        if frame_count <= 0:
            frame_count = 24
        frame_step = 360.0 / frame_count
        quantized_rotation = self.current_frame * frame_step
        rad = math.radians(quantized_rotation - 90)
        dir_x = math.cos(rad)
        dir_y = math.sin(rad)
        # Perpendicular vector to forward direction
        perp_x = -dir_y
        perp_y = dir_x
        gun_offset = 20
        side_mult = 1 if self.fire_side == 'left' else -1
        origin_x = self.rect.centerx + dir_x * 20 + perp_x * gun_offset * side_mult
        origin_y = self.rect.centery + dir_y * 20 + perp_y * gun_offset * side_mult
        # Rockets use configurable speed multiplier
        rocket = Rocket(origin_x, origin_y, dir_x * BULLET_SPEED * ROCKET_SPEED_MULTIPLIER, dir_y * BULLET_SPEED * ROCKET_SPEED_MULTIPLIER, self.rocket_sheets)
        self.fire_cooldown = 8
        self.firing_timer = self.firing_duration
        self.fire_side = 'right' if self.fire_side == 'left' else 'left'
        return rocket
    
    def take_damage(self, asteroid=None):
        """Spaceship gets hit by an asteroid. Decrement health; explode when depleted."""
        # Skip damage if spawn shield, already exploding, recently hit, or currently invulnerable
        if self.spawn_shield > 0 or self.is_exploding or self.hit_invulnerability > 0 or self.invulnerability_time > 0:
            return
        
        self.health -= 1
        if self.health <= 0:
            # Ship destroyed
            self.is_exploding = True
            self.explosion_tick = 0
            self.explosion_frame = 0
            
            # Play ship destroyed sound
            if self.ship_destroyed_sound:
                self.ship_destroyed_sound.play()
        else:
            # Ship survived - show shield animation and add brief invulnerability
            self.shield_active = True
            self.shield_timer = self.shield_duration
            self.shield_frame = 0
            self.hit_invulnerability = 20  # 20 frames of invulnerability to prevent rapid hits
            
            # Play shield hit sound
            if self.shield_hit_sound:
                self.shield_hit_sound.play()
            
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
