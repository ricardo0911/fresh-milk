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

def draw_member(pixels, size, color):
    """Draw a member/community icon"""
    center = size // 2
    # Left person (smaller)
    draw_circle(pixels, center - 10, 14, 6, color)
    for y in range(22, size - 8):
        half_width = min((y - 22) + 4, 8)
        for x in range(center - 10 - half_width, center - 10 + half_width + 1):
            if 0 <= x < size:
                pixels[y][x] = color
    # Right person (smaller)
    draw_circle(pixels, center + 10, 14, 6, color)
    for y in range(22, size - 8):
        half_width = min((y - 22) + 4, 8)
        for x in range(center + 10 - half_width, center + 10 + half_width + 1):
            if 0 <= x < size:
                pixels[y][x] = color

def draw_search(pixels, size, color):
    """Draw a search/magnifying glass icon"""
    # Circle (magnifying glass lens)
    cx, cy, r = size // 2 - 4, size // 2 - 4, 12
    for y in range(len(pixels)):
        for x in range(len(pixels[0])):
            dist_sq = (x - cx) ** 2 + (y - cy) ** 2
            if r - 3 <= (dist_sq ** 0.5) <= r:
                pixels[y][x] = color
    # Handle
    for i in range(10):
        x = cx + r + i - 2
        y = cy + r + i - 2
        if 0 <= x < size and 0 <= y < size:
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if 0 <= x + dx < size and 0 <= y + dy < size:
                        pixels[y + dy][x + dx] = color

def draw_close(pixels, size, color):
    """Draw a close/X icon"""
    margin = 12
    thickness = 3
    for i in range(size - 2 * margin):
        x1 = margin + i
        y1 = margin + i
        x2 = size - margin - 1 - i
        y2 = margin + i
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if 0 <= x1 + dx < size and 0 <= y1 + dy < size:
                    pixels[y1 + dy][x1 + dx] = color
                if 0 <= x2 + dx < size and 0 <= y2 + dy < size:
                    pixels[y2 + dy][x2 + dx] = color

def draw_empty(pixels, size, color):
    """Draw an empty state icon (empty box)"""
    margin = 8
    # Box outline
    for x in range(margin, size - margin):
        for t in range(3):
            pixels[margin + t][x] = color
            pixels[size - margin - 1 - t][x] = color
    for y in range(margin, size - margin):
        for t in range(3):
            pixels[y][margin + t] = color
            pixels[y][size - margin - 1 - t] = color
    # Sad face inside
    center = size // 2
    # Eyes
    draw_circle(pixels, center - 6, center - 4, 2, color)
    draw_circle(pixels, center + 6, center - 4, 2, color)
    # Sad mouth (arc)
    for x in range(center - 6, center + 7):
        y = center + 6 + abs(x - center) // 2
        if 0 <= y < size:
            pixels[y][x] = color
            if y + 1 < size:
                pixels[y + 1][x] = color

# Colors
GRAY = (153, 153, 153, 255)
GREEN = (16, 185, 129, 255)

# Icon configurations
icons = [
    ('home', draw_home),
    ('category', draw_category),
    ('cart', draw_cart),
    ('user', draw_user),
    ('member', draw_member),
    ('search', draw_search),
    ('close', draw_close),
    ('empty', draw_empty),
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
