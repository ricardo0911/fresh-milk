#!/usr/bin/env node
/**
 * Generate missing icons for the mini-program
 * Creates simple PNG icons using pure Node.js (no dependencies)
 */

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

function createPNG(width, height, pixels) {
    // PNG signature
    const signature = Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);

    // IHDR chunk
    const ihdrData = Buffer.alloc(13);
    ihdrData.writeUInt32BE(width, 0);
    ihdrData.writeUInt32BE(height, 4);
    ihdrData.writeUInt8(8, 8);  // bit depth
    ihdrData.writeUInt8(6, 9);  // color type (RGBA)
    ihdrData.writeUInt8(0, 10); // compression
    ihdrData.writeUInt8(0, 11); // filter
    ihdrData.writeUInt8(0, 12); // interlace
    const ihdr = createChunk('IHDR', ihdrData);

    // IDAT chunk (image data)
    const rawData = [];
    for (let y = 0; y < height; y++) {
        rawData.push(0); // filter byte
        for (let x = 0; x < width; x++) {
            const pixel = pixels[y * width + x];
            rawData.push(pixel[0], pixel[1], pixel[2], pixel[3]);
        }
    }
    const compressed = zlib.deflateSync(Buffer.from(rawData), { level: 9 });
    const idat = createChunk('IDAT', compressed);

    // IEND chunk
    const iend = createChunk('IEND', Buffer.alloc(0));

    return Buffer.concat([signature, ihdr, idat, iend]);
}

function createChunk(type, data) {
    const length = Buffer.alloc(4);
    length.writeUInt32BE(data.length, 0);

    const typeBuffer = Buffer.from(type);
    const crcData = Buffer.concat([typeBuffer, data]);
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(crcData), 0);

    return Buffer.concat([length, typeBuffer, data, crc]);
}

function crc32(data) {
    let crc = 0xFFFFFFFF;
    const table = [];
    for (let i = 0; i < 256; i++) {
        let c = i;
        for (let j = 0; j < 8; j++) {
            c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
        }
        table[i] = c;
    }
    for (let i = 0; i < data.length; i++) {
        crc = table[(crc ^ data[i]) & 0xFF] ^ (crc >>> 8);
    }
    return (crc ^ 0xFFFFFFFF) >>> 0;
}

function createIcon(size, drawFunc, color) {
    const pixels = [];
    for (let i = 0; i < size * size; i++) {
        pixels.push([255, 255, 255, 0]); // transparent
    }
    drawFunc(pixels, size, color);
    return createPNG(size, size, pixels);
}

function setPixel(pixels, size, x, y, color) {
    if (x >= 0 && x < size && y >= 0 && y < size) {
        pixels[y * size + x] = color;
    }
}

function drawCircle(pixels, size, cx, cy, r, color) {
    for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
            if ((x - cx) ** 2 + (y - cy) ** 2 <= r ** 2) {
                setPixel(pixels, size, x, y, color);
            }
        }
    }
}

function drawRect(pixels, size, x1, y1, x2, y2, color) {
    for (let y = Math.max(0, y1); y < Math.min(size, y2); y++) {
        for (let x = Math.max(0, x1); x < Math.min(size, x2); x++) {
            setPixel(pixels, size, x, y, color);
        }
    }
}

// Draw search icon (magnifying glass)
function drawSearch(pixels, size, color) {
    const cx = size / 2 - 4;
    const cy = size / 2 - 4;
    const r = 12;

    // Draw circle outline
    for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
            const dist = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2);
            if (dist >= r - 3 && dist <= r) {
                setPixel(pixels, size, x, y, color);
            }
        }
    }

    // Draw handle
    for (let i = 0; i < 12; i++) {
        const x = Math.floor(cx + r + i - 2);
        const y = Math.floor(cy + r + i - 2);
        for (let dx = -2; dx <= 2; dx++) {
            for (let dy = -2; dy <= 2; dy++) {
                setPixel(pixels, size, x + dx, y + dy, color);
            }
        }
    }
}

// Draw close icon (X)
function drawClose(pixels, size, color) {
    const margin = 12;
    const thickness = 2;

    for (let i = 0; i < size - 2 * margin; i++) {
        const x1 = margin + i;
        const y1 = margin + i;
        const x2 = size - margin - 1 - i;
        const y2 = margin + i;

        for (let dx = -thickness; dx <= thickness; dx++) {
            for (let dy = -thickness; dy <= thickness; dy++) {
                setPixel(pixels, size, x1 + dx, y1 + dy, color);
                setPixel(pixels, size, x2 + dx, y2 + dy, color);
            }
        }
    }
}

// Draw empty state icon (empty box with sad face)
function drawEmpty(pixels, size, color) {
    const margin = 8;

    // Box outline
    for (let x = margin; x < size - margin; x++) {
        for (let t = 0; t < 3; t++) {
            setPixel(pixels, size, x, margin + t, color);
            setPixel(pixels, size, x, size - margin - 1 - t, color);
        }
    }
    for (let y = margin; y < size - margin; y++) {
        for (let t = 0; t < 3; t++) {
            setPixel(pixels, size, margin + t, y, color);
            setPixel(pixels, size, size - margin - 1 - t, y, color);
        }
    }

    // Eyes
    const center = Math.floor(size / 2);
    drawCircle(pixels, size, center - 6, center - 4, 2, color);
    drawCircle(pixels, size, center + 6, center - 4, 2, color);

    // Sad mouth
    for (let x = center - 6; x <= center + 6; x++) {
        const y = center + 6 + Math.floor(Math.abs(x - center) / 2);
        setPixel(pixels, size, x, y, color);
        setPixel(pixels, size, x, y + 1, color);
    }
}

// Colors
const GRAY = [153, 153, 153, 255];

// Generate icons
const size = 48;
const scriptDir = __dirname;

const icons = [
    ['search', drawSearch],
    ['close', drawClose],
    ['empty', drawEmpty],
];

for (const [name, drawFunc] of icons) {
    const pngData = createIcon(size, drawFunc, GRAY);
    const filePath = path.join(scriptDir, `${name}.png`);
    fs.writeFileSync(filePath, pngData);
    console.log(`Created: ${name}.png`);
}

console.log('Missing icons created successfully!');
