"""Boss ship sprite class."""
import pygame
import math
import random
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from sprites.fireball import Fireball


class BossShip(pygame.sprite.Sprite):
    """Boss ship that appears at the end of level 3."""
    
    def __init__(self, *groups, x=0, y=0, sprite_sheet=None, fireball_sheet=None):
        """Initialize the boss ship.
        
        Args:
            *groups: Sprite groups to add this sprite to
            x: Initial x position
            y: Initial y position
            sprite_sheet: Sprite sheet containing 24 rotation frames (6x4)
            fireball_sheet: Sprite sheet for fireball projectiles
        """
        super().__init__(*groups)
        self.sprite_sheet = sprite_sheet or []
        self.fireball_sheet = fireball_sheet
        self.current_frame = 0  # 0-23, rotation frame
        self.x = float(x)
        self.y = float(y)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.rotation = 0  # Current rotation in degrees
        
        # Boss stats
        self.max_health = 50  # Boss takes many hits
        self.health = self.max_health
        self.radius = 64  # Collision radius (sprite is 128px)
        
        # Movement behavior
        self.move_timer = 0
        self.move_duration = 120  # Frames to move in one direction
        self.target_vx = 0
        self.target_vy = 0
        
        # Firing behavior
        self.fire_cooldown = 0
        self.fire_rate = 45  # Frames between volleys
        self.volley_count = 0
        self.volley_timer = 0
        
        # Gun positions (in degrees on the first sprite)
        # Guns at 45°, 135°, 225°, 315° compass positions
        self.gun_angles = [45, 135, 225, 315]
        
        # Set initial image
        self._update_image()
        
        # Start with random movement
        self._set_new_movement()
    
    def _update_image(self):
        """Update sprite based on rotation frame."""
        if self.sprite_sheet and self.current_frame < len(self.sprite_sheet):
            self.image = self.sprite_sheet[self.current_frame].copy()
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        else:
            # Fallback if sprite sheet is missing
            self.image = pygame.Surface((128, 128), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 0), (64, 64), 60)
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def _set_new_movement(self):
        """Set a new random movement direction."""
        angle = random.uniform(0, 360)
        speed = random.uniform(1.5, 3.0)
        self.target_vx = math.cos(math.radians(angle)) * speed
        self.target_vy = math.sin(math.radians(angle)) * speed
        self.move_timer = 0
    
    def _calculate_gun_position(self, gun_angle_offset):
        """Calculate world position of a gun based on current rotation.
        
        Args:
            gun_angle_offset: The gun's angle offset on the sprite (45, 135, 225, or 315)
        
        Returns:
            Tuple of (x, y) world position
        """
        # Each sprite frame is 15° rotation (360/24 = 15)
        frame_rotation = self.current_frame * 15
        
        # Total gun angle = sprite rotation + gun offset
        total_angle = frame_rotation + gun_angle_offset
        
        # Convert to radians and calculate position
        # Guns are about 40 pixels from center of 128px sprite
        gun_distance = 40
        rad = math.radians(total_angle - 90)  # -90 because 0° is up
        gun_x = self.x + math.cos(rad) * gun_distance
        gun_y = self.y + math.sin(rad) * gun_distance
        
        return gun_x, gun_y
    
    def fire_volley(self):
        """Fire fireballs from all 4 guns toward the player position.
        
        Returns:
            List of Fireball sprites
        """
        if self.fire_cooldown > 0:
            return []
        
        fireballs = []
        fireball_speed = 4.0
        
        for gun_angle in self.gun_angles:
            gun_x, gun_y = self._calculate_gun_position(gun_angle)
            
            # Fire in the direction the gun is pointing
            # Gun angle is already the total angle (sprite rotation + gun offset)
            frame_rotation = self.current_frame * 15
            total_gun_angle = frame_rotation + gun_angle
            rad = math.radians(total_gun_angle - 90)
            
            vx = math.cos(rad) * fireball_speed
            vy = math.sin(rad) * fireball_speed
            
            fireball = Fireball(gun_x, gun_y, vx, vy, self.fireball_sheet)
            fireballs.append(fireball)
        
        self.fire_cooldown = self.fire_rate
        return fireballs
    
    def take_damage(self):
        """Boss takes damage from a hit."""
        self.health -= 1
        if self.health <= 0:
            return True  # Boss is destroyed
        return False
    
    def update(self):
        """Update boss movement and rotation."""
        # Smooth movement towards target velocity
        self.velocity_x += (self.target_vx - self.velocity_x) * 0.1
        self.velocity_y += (self.target_vy - self.velocity_y) * 0.1
        
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Keep boss on screen (bounce off edges)
        margin = 100
        if self.x < margin:
            self.x = margin
            self.target_vx = abs(self.target_vx)
        elif self.x > WINDOW_WIDTH - margin:
            self.x = WINDOW_WIDTH - margin
            self.target_vx = -abs(self.target_vx)
        
        if self.y < margin:
            self.y = margin
            self.target_vy = abs(self.target_vy)
        elif self.y > WINDOW_HEIGHT - margin:
            self.y = WINDOW_HEIGHT - margin
            self.target_vy = -abs(self.target_vy)
        
        # Change movement direction periodically
        self.move_timer += 1
        if self.move_timer >= self.move_duration:
            self._set_new_movement()
        
        # Slowly rotate
        self.rotation += 0.5
        if self.rotation >= 360:
            self.rotation -= 360
        
        # Update sprite frame based on rotation
        frame_step = 360.0 / 24
        self.current_frame = int((self.rotation / frame_step) % 24)
        
        # Update fire cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        
        self.rect.center = (int(self.x), int(self.y))
        self._update_image()
