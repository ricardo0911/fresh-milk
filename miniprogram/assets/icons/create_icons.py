#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate tabBar icons for the mini-program"""

import struct
import zlib
import os

def create_png(width, height, pixels):
    """Create a PNG file from pixel data"""
    def png_chunk(chunk_type, data):
        chunk_len = struct.pack('>I', len(data))
        chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
        return chunk_len + chunk_type + data + chunk_crc
    
    signature = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    
    raw_data = b''
    for row in pixels:
        raw_data += b'\x00'
        for r, g, b, a in row:
            raw_data += struct.pack('BBBB', r, g, b, a)
    
    compressed = zlib.compress(raw_data, 9)
    
    return (signature + 
            png_chunk(b'IHDR', ihdr) + 
            png_chunk(b'IDAT', compressed) + 
            png_chunk(b'IEND', b''))

def draw_icon(size, draw_func, color):
    """Create an icon with the given drawing function"""
    pixels = [[(255, 255, 255, 0) for _ in range(size)] for _ in range(size)]
    draw_func(pixels, size, color)
    return pixels

def draw_circle(pixels, cx, cy, r, color):
    """Draw a filled circle"""
    for y in range(len(pixels)):
        for x in range(len(pixels[0])):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                pixels[y][x] = color

def draw_rect(pixels, x1, y1, x2, y2, color):
    """Draw a filled rectangle"""
    for y in range(max(0, y1), min(len(pixels), y2)):
        for x in range(max(0, x1), min(len(pixels[0]), x2)):
            pixels[y][x] = color

def draw_home(pixels, size, color):
    """Draw a home icon"""
    # Roof (triangle)
    center = size // 2
    for y in range(6, size // 2):
        half_width = (y - 6) * 2
        for x in range(center - half_width, center + half_width + 1):
            if 0 <= x < size:
                pixels[y][x] = color
    # House body
    draw_rect(pixels, size//4, size//2, 3*size//4, size - 6, color)
    # Door
    door_color = (255, 255, 255, 255) if color[3] == 255 else (255, 255, 255, 0)
    draw_rect(pixels, size//2 - 4, size//2 + 6, size//2 + 4, size - 6, door_color)

def draw_category(pixels, size, color):
    """Draw a category/grid icon"""
    gap = 4
    box_size = (size - gap * 3) // 2
    # Top left
    draw_rect(pixels, gap, gap, gap + box_size, gap + box_size, color)
    # Top right
    draw_rect(pixels, gap * 2 + box_size, gap, size - gap, gap + box_size, color)
    # Bottom left
    draw_rect(pixels, gap, gap * 2 + box_size, gap + box_size, size - gap, color)
    # Bottom right
    draw_rect(pixels, gap * 2 + box_size, gap * 2 + box_size, size - gap, size - gap, color)

def draw_cart(pixels, size, color):
    """Draw a cart icon"""
    # Cart body
    draw_rect(pixels, 8, 12, size - 6, size - 12, color)
    # Handle
    for x in range(4, 10):
        for y in range(8, 14):
            pixels[y][x] = color
    # Wheels
    draw_circle(pixels, 14, size - 8, 4, color)
    draw_circle(pixels, size - 12, size - 8, 4, color)

def draw_user(pixels, size, color):
    """Draw a user icon"""
    center = size // 2
    # Head
    draw_circle(pixels, center, 12, 8, color)
    # Body
    for y in range(22, size - 4):
        half_width = min((y - 22) + 6, size // 2 - 4)
        for x in range(center - half_width, center + half_width + 1):
            if 0 <= x < size:
                pixels[y][x] = color

# Colors
GRAY = (153, 153, 153, 255)
GREEN = (16, 185, 129, 255)

# Icon configurations
icons = [
    ('home', draw_home),
    ('category', draw_category),
    ('cart', draw_cart),
    ('user', draw_user),
]

size = 48
script_dir = os.path.dirname(os.path.abspath(__file__))

for name, draw_func in icons:
    # Normal icon (gray)
    pixels = draw_icon(size, draw_func, GRAY)
    png_data = create_png(size, size, pixels)
    with open(os.path.join(script_dir, f'{name}.png'), 'wb') as f:
        f.write(png_data)
    
    # Active icon (green)
    pixels = draw_icon(size, draw_func, GREEN)
    png_data = create_png(size, size, pixels)
    with open(os.path.join(script_dir, f'{name}-active.png'), 'wb') as f:
        f.write(png_data)

print('Icons created successfully!')
