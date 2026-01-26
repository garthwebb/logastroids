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
    LEVEL_PROGRESSION_TOTAL, LEVEL_PROGRESSION_SPAWN_REDUCTION,
    MAX_SHIELDS, INVULNERABILITY_DURATION, NUM_ROCKETS_PER_PICKUP,
    POWERUP_SPAWN_CHANCE, HEALTH_POWERUP_WEIGHT, INVULNERABILITY_POWERUP_WEIGHT,
    ROCKETS_POWERUP_WEIGHT, SHIELDS_POWERUP_WEIGHT
)
from sprites import Spaceship, Bullet, Rocket, Asteroid, Explosion, PowerUp
from utils import (
    load_sheet,
    load_specs_dict,
    load_specs_list,
    load_powerup_sprites,
    SHIP_SPECS,
    FIRE_SPECS,
    SHIELD_SPEC,
    DAMAGE_SPECS,
    ASTEROID_STAGE_SPECS,
    BROKEN_ASTEROID_SPECS,
    ROCKET_SPECS,
)
from ui import (
    draw_health, draw_score, draw_level, draw_game_over, draw_start_screen,
    load_high_scores, save_high_scores, is_high_score, add_high_score,
    draw_rockets, draw_invulnerability
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
    # Load background image, scale preserving aspect ratio to cover window, then crop
    background = None
    try:
        bg_path = os.path.join(script_dir, "images", "pixel-starfield.png")
        bg_img = pygame.image.load(bg_path).convert()
        src_w, src_h = bg_img.get_width(), bg_img.get_height()
        # Scale factor to cover the window entirely while preserving aspect ratio
        scale = max(WINDOW_WIDTH / src_w, WINDOW_HEIGHT / src_h)
        new_w, new_h = int(src_w * scale), int(src_h * scale)
        scaled = pygame.transform.smoothscale(bg_img, (new_w, new_h))
        # Create a window-sized surface and blit scaled image centered (cropped)
        background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        offset_x = (WINDOW_WIDTH - new_w) // 2
        offset_y = (WINDOW_HEIGHT - new_h) // 2
        background.blit(scaled, (offset_x, offset_y))
    except Exception as e:
        print(f"Warning: failed to load background image: {e}. Using solid fill.")
    # Load sprite sheets using declarative specs
    ship_sheets = load_specs_dict(SHIP_SPECS)
    fire_sheets = load_specs_dict(FIRE_SPECS)
    shield_sprites = load_sheet(SHIELD_SPEC)
    damage_sprites = load_specs_list(DAMAGE_SPECS)
    asteroid_stage_sheets = load_specs_list(ASTEROID_STAGE_SPECS)
    broken_sheets = load_specs_list(BROKEN_ASTEROID_SPECS)
    rocket_sheets = load_specs_list(ROCKET_SPECS)

    # Create spaceship
    spaceship = Spaceship(
        sprites_static=ship_sheets.get("static", []),
        sprites_thrust=ship_sheets.get("thrust", []),
        damage_sprites=damage_sprites,
        shield_sprites=shield_sprites,
        fire_thrust_left=fire_sheets.get("fire_thrust_left", []),
        fire_thrust_right=fire_sheets.get("fire_thrust_right", []),
        fire_static_left=fire_sheets.get("fire_static_left", []),
        fire_static_right=fire_sheets.get("fire_static_right", []),
        rocket_sheets=rocket_sheets,
        x=WINDOW_WIDTH // 2,
        y=WINDOW_HEIGHT // 2,
    )

    # Load power-up sprites
    powerup_sprites = load_powerup_sprites()
    
    # Sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    rockets = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

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
                            high_scores = add_high_score(player_name.strip(), score, current_level, high_scores)
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
                elif event.key == pygame.K_b and not game_over and game_started:
                    rocket = spaceship.fire_rocket()
                    if rocket:
                        rockets.add(rocket)
                        all_sprites.add(rocket)
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
                        rockets.empty()
                        asteroids.empty()
                        explosions.empty()
                        powerups.empty()
                        
                        initial_asteroids, max_asteroids, total_asteroids, spawn_interval_seconds = get_level_params(current_level)
                        spawn_interval_frames = int(spawn_interval_seconds * FPS)
                        
                        spaceship = Spaceship(
                            sprites_static=ship_sheets.get("static", []),
                            sprites_thrust=ship_sheets.get("thrust", []),
                            damage_sprites=damage_sprites,
                            shield_sprites=shield_sprites,
                            fire_thrust_left=fire_sheets.get("fire_thrust_left", []),
                            fire_thrust_right=fire_sheets.get("fire_thrust_right", []),
                            fire_static_left=fire_sheets.get("fire_static_left", []),
                            fire_static_right=fire_sheets.get("fire_static_right", []),
                            rocket_sheets=rocket_sheets,
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
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill(BLACK)
            draw_start_screen(screen)
            pygame.display.flip()
            continue
        
        # Skip updates if game over
        if game_over:
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill(BLACK)
            draw_game_over(screen, score, high_scores, entering_name, player_name)
            pygame.display.flip()
            continue
        
        # Update
        spaceship.handle_input(keys)
        all_sprites.update()

        # Bullet vs asteroid collisions
        for asteroid in pygame.sprite.groupcollide(asteroids, bullets, False, True):
            alive = asteroid.take_damage(1)
            score += 1
            if not alive:
                score += 10
                asteroids_destroyed_this_level += 1
                create_explosion(asteroid.x, asteroid.y, asteroid.rotation, asteroid.rotation_speed, asteroid.vx, asteroid.vy)
                
                # Randomly spawn a power-up when asteroid is destroyed
                if random.random() < POWERUP_SPAWN_CHANCE:
                    roll = random.random()
                    if roll < HEALTH_POWERUP_WEIGHT:
                        powerup_type = PowerUp.HEALTH
                    elif roll < HEALTH_POWERUP_WEIGHT + INVULNERABILITY_POWERUP_WEIGHT:
                        powerup_type = PowerUp.INVULNERABILITY
                    elif roll < HEALTH_POWERUP_WEIGHT + INVULNERABILITY_POWERUP_WEIGHT + ROCKETS_POWERUP_WEIGHT:
                        powerup_type = PowerUp.ROCKETS
                    else:
                        powerup_type = PowerUp.SHIELDS  # Remaining weight
                    
                    powerup_sprite = powerup_sprites[powerup_type]
                    powerup = PowerUp(asteroid.x, asteroid.y, powerup_type, powerup_sprite)
                    powerups.add(powerup)
                    all_sprites.add(powerup)
                
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
        
        # Rocket vs asteroid collisions (using circle-based collision for smaller hitbox)
        for rocket in list(rockets):
            if rocket not in all_sprites:
                continue
            for asteroid in asteroids:
                # Circle-based collision between rocket and asteroid
                dx = rocket.x - asteroid.x
                dy = rocket.y - asteroid.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < (rocket.radius + asteroid.radius):
                    # Collision! Rocket does 4 damage (destroys in one hit)
                    alive = asteroid.take_damage(4)
                    score += 1
                    rocket.kill()
                    if not alive:
                        score += 10
                        asteroids_destroyed_this_level += 1
                        create_explosion(asteroid.x, asteroid.y, asteroid.rotation, asteroid.rotation_speed, asteroid.vx, asteroid.vy)
                        
                        # Randomly spawn a power-up when asteroid is destroyed
                        if random.random() < POWERUP_SPAWN_CHANCE:
                            roll = random.random()
                            if roll < HEALTH_POWERUP_WEIGHT:
                                powerup_type = PowerUp.HEALTH
                            elif roll < HEALTH_POWERUP_WEIGHT + INVULNERABILITY_POWERUP_WEIGHT:
                                powerup_type = PowerUp.INVULNERABILITY
                            elif roll < HEALTH_POWERUP_WEIGHT + INVULNERABILITY_POWERUP_WEIGHT + ROCKETS_POWERUP_WEIGHT:
                                powerup_type = PowerUp.ROCKETS
                            else:
                                powerup_type = PowerUp.SHIELDS  # Remaining weight
                            
                            powerup_sprite = powerup_sprites[powerup_type]
                            powerup = PowerUp(asteroid.x, asteroid.y, powerup_type, powerup_sprite)
                            powerups.add(powerup)
                            all_sprites.add(powerup)
                        
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
                    break
        
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
        
        # Power-up vs spaceship collisions
        for powerup in pygame.sprite.spritecollide(spaceship, powerups, True):
            if powerup.power_type == PowerUp.HEALTH:
                # Increase max health (up to 6) and refill health
                spaceship.max_health = min(spaceship.max_health + 1, 6)
                spaceship.health = spaceship.max_health
            elif powerup.power_type == PowerUp.SHIELDS:
                # Refill health to max (only if not already at max)
                if spaceship.health < spaceship.max_health:
                    spaceship.health = spaceship.max_health
            elif powerup.power_type == PowerUp.INVULNERABILITY:
                # Grant invulnerability
                spaceship.invulnerability_time = int(INVULNERABILITY_DURATION * FPS)
            elif powerup.power_type == PowerUp.ROCKETS:
                # Add rockets
                spaceship.rockets += NUM_ROCKETS_PER_PICKUP

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
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)
        bullets.draw(screen)
        rockets.draw(screen)
        asteroids.draw(screen)
        explosions.draw(screen)
        powerups.draw(screen)
        if spaceship in all_sprites:
            spaceship.draw(screen)
        draw_health(screen, spaceship.health if spaceship in all_sprites else 0, max_segments=spaceship.max_health if spaceship in all_sprites else 3)
        if spaceship in all_sprites and spaceship.rockets > 0:
            draw_rockets(screen, spaceship.rockets)
        if spaceship in all_sprites and spaceship.invulnerability_time > 0:
            draw_invulnerability(screen, spaceship.invulnerability_time, fps=FPS)
        draw_score(screen, score)
        draw_level(screen, current_level)

        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
