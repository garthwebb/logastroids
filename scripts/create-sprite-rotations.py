import sys
from pathlib import Path
from PIL import Image


def create_rotational_spritesheet(source_path, output_path, sprite_size, angle_increment):
    try:
        # Load the source image (Expects a transparent PNG)
        # Ensure the source is facing UP (0 degrees) for correct rotation logic
        src_img = Image.open(source_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Could not find '{source_path}'. Please ensure the file exists.")
        return

    # resize source if it isn't already the correct size
    if src_img.size != (sprite_size, sprite_size):
        src_img = src_img.resize((sprite_size, sprite_size), Image.Resampling.LANCZOS)

    # Calculate Grid Dimensions
    total_frames = int(360 / angle_increment) # 24 frames
    
    # Let's organize it into a readable grid (e.g., 6 columns x 4 rows)
    columns = 6
    rows = 4
    
    sheet_width = columns * sprite_size
    sheet_height = rows * sprite_size
    
    # Create the blank sheet
    sprite_sheet = Image.new("RGBA", (sheet_width, sheet_height))

    print(f"Generating {total_frames} frames...")

    for i in range(total_frames):
        # Calculate angle (Negative because PIL rotates counter-clockwise)
        angle = i * angle_increment
        
        # Rotate the image
        # 'expand=False' keeps the size 96x96, clipping corners if the ship is too wide.
        # Ensure your ship has some empty padding in the source image to avoid clipping!
        rotated_frame = src_img.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=False)
        
        # Calculate position on the grid
        col_idx = i % columns
        row_idx = i // columns
        
        x = col_idx * sprite_size
        y = row_idx * sprite_size
        
        # Paste into the sheet
        sprite_sheet.paste(rotated_frame, (x, y))

    # Save the result
    sprite_sheet.save(output_path)
    print(f"Success! Saved sprite sheet to: {output_path}")

# --- Configuration ---
def main():
    if len(sys.argv) < 2:
        print("Usage: python create-sprite-rotations.py <image_filename> [sprite_size] [angle_increment] [output_filename]")
        print("\nArguments:")
        print("  image_filename    - Source PNG image to rotate")
        print("  sprite_size       - Size in pixels (default: 96)")
        print("  angle_increment   - Degrees between frames (default: 15)")
        print("  output_filename   - Custom output path (optional)")
        print("\nExamples:")
        print("  python create-sprite-rotations.py spaceship.png")
        print("  python create-sprite-rotations.py rocket.png 48 15")
        print("  python create-sprite-rotations.py ship.png 64 10 my_output.png")
        sys.exit(1)
    
    source_filename = sys.argv[1]
    
    # Set defaults
    sprite_size = 96
    angle_increment = 15
    output_filename = None
    
    # Override with command-line arguments if provided
    if len(sys.argv) > 2:
        sprite_size = int(sys.argv[2])
    if len(sys.argv) > 3:
        angle_increment = int(sys.argv[3])
    if len(sys.argv) > 4:
        output_filename = sys.argv[4]
    
    # Generate default output filename with actual sprite_size
    if output_filename is None:
        output_filename = f"{Path(source_filename).stem}-{sprite_size}px-6x4.png"
    
    create_rotational_spritesheet(
        source_path=source_filename,
        output_path=output_filename,
        sprite_size=sprite_size,
        angle_increment=angle_increment
    )

if __name__ == "__main__":
    main()
