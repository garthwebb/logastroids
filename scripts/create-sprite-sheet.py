#!/usr/bin/env python3
"""
Create a sprite sheet from a list of images.

Usage:
    python create-sprite-sheet.py <output_base_name> <sprite_size> <image1> <image2> ...

Example:
    python create-sprite-sheet.py my-sprite 96 img1.png img2.png img3.png
    
This will create: my-sprite-96px-3x1.png (3 columns, 1 row)
"""

import sys
import os
import math
from pathlib import Path
from PIL import Image


def create_sprite_sheet(image_paths, output_base, sprite_size, max_cols=10):
    """
    Create a sprite sheet from a list of images.
    
    Args:
        image_paths: List of paths to input images
        output_base: Base name for output file (without extension)
        sprite_size: Target size for each sprite (width and height in pixels)
        max_cols: Maximum number of columns before starting a new row (default: 10)
    
    Returns:
        Path to the created sprite sheet
    """
    if not image_paths:
        raise ValueError("No images provided")
    
    # Load and resize all images
    sprites = []
    for img_path in image_paths:
        try:
            img = Image.open(img_path).convert("RGBA")
            # Resize to target sprite size
            if img.size != (sprite_size, sprite_size):
                img = img.resize((sprite_size, sprite_size), Image.Resampling.LANCZOS)
            sprites.append(img)
        except Exception as e:
            print(f"Warning: Could not load {img_path}: {e}")
            continue
    
    if not sprites:
        raise ValueError("No valid images could be loaded")
    
    # Calculate grid dimensions
    num_sprites = len(sprites)
    cols = min(num_sprites, max_cols)
    rows = math.ceil(num_sprites / max_cols)
    
    # Create the sprite sheet
    sheet_width = cols * sprite_size
    sheet_height = rows * sprite_size
    sprite_sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))
    
    # Paste sprites into the sheet
    for i, sprite in enumerate(sprites):
        col = i % cols
        row = i // cols
        x = col * sprite_size
        y = row * sprite_size
        sprite_sheet.paste(sprite, (x, y))
    
    # Generate output filename with format: BASE-PIXELSpx-COLxROW.png
    output_filename = f"{output_base}-{sprite_size}px-{cols}x{rows}.png"
    sprite_sheet.save(output_filename)
    
    print(f"✓ Created sprite sheet: {output_filename}")
    print(f"  - Grid: {cols} columns × {rows} rows")
    print(f"  - Sprites: {num_sprites}")
    print(f"  - Size: {sheet_width}×{sheet_height} pixels")
    
    return output_filename


def main():
    if len(sys.argv) < 4:
        print("Usage: python create-sprite-sheet.py <output_base> <sprite_size> <image1> [image2] ...")
        print("\nExample:")
        print("  python create-sprite-sheet.py my-sprite 96 frame1.png frame2.png frame3.png")
        print("\nThis creates: my-sprite-96px-COLxROW.png")
        print("  where COL and ROW are calculated based on the number of images (max 10 columns)")
        sys.exit(1)
    
    output_base = sys.argv[1]
    
    try:
        sprite_size = int(sys.argv[2])
        if sprite_size <= 0:
            raise ValueError("Sprite size must be positive")
    except ValueError as e:
        print(f"Error: Invalid sprite size '{sys.argv[2]}': {e}")
        sys.exit(1)
    
    image_paths = sys.argv[3:]
    
    # Verify all image files exist
    missing_files = [path for path in image_paths if not os.path.exists(path)]
    if missing_files:
        print("Error: The following files do not exist:")
        for f in missing_files:
            print(f"  - {f}")
        sys.exit(1)
    
    try:
        create_sprite_sheet(image_paths, output_base, sprite_size)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
