"""Main game module for Logastroids."""
import pygame
import math
import os
import random

# Import from modules
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, BLACK,
    BULLET_SPEED, ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED, ASTEROID_ROTATION_RANGE,
    LEVEL_1_INITIAL_ASTEROIDS, LEVEL_1_MAX_ON_SCREEN, LEVEL_1_TOTAL_ASTEROIDS,
    LEVEL_1_SPAWN_INTERVAL, LEVEL_PROGRESSION_INITIAL, LEVEL_PROGRESSION_MAX,
    LEVEL_PROGRESSION_TOTAL, LEVEL_PROGRESSION_SPAWN_REDUCTION
)
from sprites import Spaceship, Bullet, Asteroid, Explosion
from utils import load_spritesheet
from ui import (
    draw_health, draw_score, draw_level, draw_game_over, draw_start_screen,
    load_high_scores, save_high_scores, is_high_score, add_high_score
)

# Initialize Pygame
pygame.init()


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

    # Asteroid stages and explosion frames
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
        spawn_margin = 100
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
        explosion = Explosion(broken_sheets, x, y, rotation_angle, rotation_speed, vx, vy)
        explosions.add(explosion)
        all_sprites.add(explosion)

    # Level system
    current_level = 1
    asteroids_spawned_this_level = 0
    asteroids_destroyed_this_level = 0
    
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
    respawn_timer = 0
    RESPAWN_DELAY = 180
    spaceship_destroyed_pos = None
    score = 0
    game_over = False
    game_started = False
    high_scores = load_high_scores()
    entering_name = False
    player_name = ""
    running = True
    
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if entering_name:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip():
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
                        game_started = True
                    elif game_over and not entering_name:
                        game_over = False
                        current_level = 1
                        asteroids_spawned_this_level = 0
                        asteroids_destroyed_this_level = 0
                        score = 0
                        entering_name = False
                        player_name = ""
                        
                        all_sprites.empty()
                        bullets.empty()
                        asteroids.empty()
                        explosions.empty()
                        
                        initial_asteroids, max_asteroids, total_asteroids, spawn_interval_seconds = get_level_params(current_level)
                        spawn_interval_frames = int(spawn_interval_seconds * FPS)
                        
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
            score += 1
            if not alive:
                score += 10
                asteroids_destroyed_this_level += 1
                create_explosion(asteroid.x, asteroid.y, asteroid.rotation, asteroid.rotation_speed, asteroid.vx, asteroid.vy)
                
                # Spawn child asteroids if this is a parent asteroid and level >= 3
                if asteroid.spawn_children and asteroid.scale == 1.0 and current_level >= 3:
                    child_scale = 0.5
                    for i in range(3):
                        angle = (i * 120) * math.pi / 180
                        child_speed = 2.0
                        child_vx = asteroid.vx + math.cos(angle) * child_speed
                        child_vy = asteroid.vy + math.sin(angle) * child_speed
                        
                        offset_dist = 30
                        child_x = asteroid.x + math.cos(angle) * offset_dist
                        child_y = asteroid.y + math.sin(angle) * offset_dist
                        
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
                    spawn_timer = 0
        
        # Check for level completion
        if (asteroids_destroyed_this_level >= total_asteroids and 
            len(asteroids) == 0 and 
            len(explosions) == 0):
            current_level += 1
            asteroids_spawned_this_level = 0
            asteroids_destroyed_this_level = 0
            
            initial_asteroids, max_asteroids, total_asteroids, spawn_interval_seconds = get_level_params(current_level)
            spawn_interval_frames = int(spawn_interval_seconds * FPS)
            
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
            game_over = True
            if is_high_score(score, high_scores):
                entering_name = True
                player_name = ""
        
        # Draw
        screen.fill(BLACK)
        bullets.draw(screen)
        asteroids.draw(screen)
        explosions.draw(screen)
        if spaceship in all_sprites:
            spaceship.draw(screen)
        draw_health(screen, spaceship.health if spaceship in all_sprites else 0, max_segments=3)
        draw_score(screen, score)
        draw_level(screen, current_level)

        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
