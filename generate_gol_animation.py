#!/usr/bin/env python3
"""
Generate a Conway's Game of Life animation as a GIF.
This matches the Game of Life displayed in the README.
"""

import numpy as np
from PIL import Image, ImageDraw
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

def create_image(cells, cell_size=8):
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
    
    return img

def generate_animation(output_file='gol_animation.gif', num_frames=400, grid_width=100, grid_height=60, cell_size=8):
    """Generate Game of Life animation and save as GIF"""
    
    print(f"Generating Game of Life animation ({grid_width}x{grid_height})...")
    print(f"Generating {num_frames} frames...")
    
    gol = GameOfLife(grid_width, grid_height)
    frames = []
    
    for frame_num in range(num_frames):
        if frame_num % 20 == 0:
            print(f"  Frame {frame_num}/{num_frames}")
        
        img = create_image(gol.cells, cell_size)
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
