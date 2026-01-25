"""UI drawing functions and high score management."""
import pygame
import json
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE


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
