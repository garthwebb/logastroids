"""Background image manager for handling level-based backgrounds."""
import pygame
import os
from pathlib import Path


class BackgroundManager:
    """Manages background images with automatic switching based on level progression."""
    
    def __init__(self, window_width, window_height, backgrounds=None, levels_per_background=5):
        """Initialize background manager.
        
        Args:
            window_width: Width of the game window
            window_height: Height of the game window
            backgrounds: List of background image filenames (relative to images/ directory)
            levels_per_background: Number of levels before switching to next background
        """
        self.window_width = window_width
        self.window_height = window_height
        self.levels_per_background = levels_per_background
        
        # Default backgrounds if none provided
        if backgrounds is None:
            backgrounds = ["pixel-starfield.png"]
        
        self.background_files = backgrounds
        self.loaded_backgrounds = {}
        self.current_background = None
        self.current_level = 1
        
        # Load all backgrounds
        script_dir = Path(__file__).parent
        images_dir = script_dir / "images"
        
        for bg_file in self.background_files:
            bg_path = images_dir / bg_file
            try:
                self.loaded_backgrounds[bg_file] = self._load_and_scale_background(bg_path)
            except Exception as e:
                print(f"Warning: failed to load background {bg_file}: {e}")
                self.loaded_backgrounds[bg_file] = None
        
        # Set initial background
        self.update_background_for_level(1)
    
    def _load_and_scale_background(self, bg_path):
        """Load and scale a background image to cover the window with aspect ratio preserved.
        
        Args:
            bg_path: Path to the background image
            
        Returns:
            pygame.Surface: Scaled and cropped background, or None if loading failed
        """
        bg_img = pygame.image.load(bg_path).convert()
        src_w, src_h = bg_img.get_width(), bg_img.get_height()
        
        # Scale factor to cover the window entirely while preserving aspect ratio
        scale = max(self.window_width / src_w, self.window_height / src_h)
        new_w, new_h = int(src_w * scale), int(src_h * scale)
        scaled = pygame.transform.smoothscale(bg_img, (new_w, new_h))
        
        # Create a window-sized surface and blit scaled image centered (cropped)
        background = pygame.Surface((self.window_width, self.window_height))
        offset_x = (self.window_width - new_w) // 2
        offset_y = (self.window_height - new_h) // 2
        background.blit(scaled, (offset_x, offset_y))
        
        return background
    
    def update_background_for_level(self, level):
        """Update the current background based on the level.
        
        Args:
            level: Current game level
        """
        self.current_level = level
        
        # Calculate which background to use based on level
        bg_index = ((level - 1) // self.levels_per_background) % len(self.background_files)
        bg_file = self.background_files[bg_index]
        
        self.current_background = self.loaded_backgrounds.get(bg_file)
    
    def get_current_background(self):
        """Get the current background surface.
        
        Returns:
            pygame.Surface or None: Current background image
        """
        return self.current_background
    
    def draw(self, screen, fallback_color=(0, 0, 0)):
        """Draw the current background to the screen.
        
        Args:
            screen: pygame.Surface to draw on
            fallback_color: Color tuple to use if no background is available
        """
        if self.current_background:
            screen.blit(self.current_background, (0, 0))
        else:
            screen.fill(fallback_color)
