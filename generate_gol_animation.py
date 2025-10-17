#!/usr/bin/env python3
"""
Generate a Conway's Game of Life animation as a GIF.
This matches the Game of Life displayed in the README.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

class GameOfLife:
    def __init__(self, width, height, seed=42):
        self.width = width
        self.height = height
        self.cells = np.random.RandomState(seed).random((height, width)) > 0.7
        
        # Create dead zone from 2/5 down to 7/8 down
        dead_zone_start = int(height * 2 / 5)
        dead_zone_end = int(height * 7 / 8)
        self.cells[dead_zone_start:dead_zone_end, :] = False
    
    def count_neighbors(self, x, y):
        """Count live neighbors using toroidal wrapping"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                if self.cells[ny, nx]:
                    count += 1
        return count
    
    def step(self):
        """Advance one generation"""
        new_cells = np.zeros_like(self.cells)
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                if self.cells[y, x]:  # Cell is alive
                    new_cells[y, x] = neighbors in [2, 3]
                else:  # Cell is dead
                    new_cells[y, x] = neighbors == 3
        self.cells = new_cells

def create_image(cells, cell_size=8, add_text=False, text_x_center=None):
    """Create a PIL Image from the cell state"""
    height, width = cells.shape
    img_width = width * cell_size
    img_height = height * cell_size
    
    # Create image with dark background
    img = Image.new('RGB', (img_width, img_height), color=(13, 17, 23))
    pixels = img.load()
    
    # Draw alive cells in blue (#58a6ff)
    alive_color = (88, 166, 255)
    for y in range(height):
        for x in range(width):
            if cells[y, x]:
                # Draw cell (cell_size-1 to create grid effect)
                for py in range(cell_size - 1):
                    for px in range(cell_size - 1):
                        pixels[x * cell_size + px, y * cell_size + py] = alive_color
    
    # Add text overlay
    if add_text:
        draw = ImageDraw.Draw(img)
        
        # Try to load a monospace font, fall back to default if not available
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 40)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
        except (IOError, OSError):
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", 40)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", 22)
            except (IOError, OSError):
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # Green color for text (#3fb950)
        text_color = (63, 185, 80)
        shadow_color = (0, 0, 0)
        
        # Draw text at the dead zone area
        text1 = "hi there ! i'm andrew"
        text2 = "(here are my side quests)"
        
        # Use provided text_x_center or default to image center
        if text_x_center is None:
            text_x_center = img_width // 2
        
        text_y_center = int(img_height * (2/5 + 7/8) / 2)
        
        # Draw thin black outline for definition without losing sharpness
        outline_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for offset_x, offset_y in outline_offsets:
            draw.text((text_x_center + offset_x, text_y_center - 20 + offset_y), text1, 
                     fill=shadow_color, anchor="mm", font=font_large)
            draw.text((text_x_center + offset_x, text_y_center + 15 + offset_y), text2, 
                     fill=shadow_color, anchor="mm", font=font_small)
        
        # Main text pass - sharp and vibrant
        draw.text((text_x_center, text_y_center - 20), text1, 
                 fill=text_color, anchor="mm", font=font_large)
        draw.text((text_x_center, text_y_center + 15), text2, 
                 fill=text_color, anchor="mm", font=font_small)
    
    return img

def generate_animation(output_file='gol_animation.gif', num_frames=120, grid_width=100, grid_height=60, cell_size=8, text_x_center=6/10*800):
    """Generate Game of Life animation and save as GIF"""
    
    print(f"Generating Game of Life animation ({grid_width}x{grid_height})...")
    print(f"Generating {num_frames} frames with text overlay...")
    
    gol = GameOfLife(grid_width, grid_height)
    frames = []
    
    for frame_num in range(num_frames):
        if frame_num % 20 == 0:
            print(f"  Frame {frame_num}/{num_frames}")
        
        img = create_image(gol.cells, cell_size, add_text=True, text_x_center=text_x_center)
        frames.append(img)
        gol.step()
    
    print(f"Saving animation to {output_file}...")
    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=125,  # 125ms per frame = ~8 fps
        loop=0,
        optimize=False
    )
    
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✓ Animation saved! File size: {file_size_mb:.2f} MB")
    print(f"  Location: {os.path.abspath(output_file)}")

if __name__ == '__main__':
    generate_animation()
