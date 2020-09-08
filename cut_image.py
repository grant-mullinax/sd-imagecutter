import math
import cv2
import numpy as np


def cut_chunk(img, bx, by):
    chunk = np.zeros((255, 255, 3), np.uint8)

    for y in range(255):
        for x in range(255):
            chunk[y][x] = img[y + by][x + bx]

    return chunk


def color_is_black(color):
    r, g, b = color
    return r == 0 and g == 0 and b == 0


def align_cut(img, bx, by):
    height, width, channels = img.shape

    # top
    for x in range(255):
        if by + 254 >= height - 1 or bx + 254 >= width - 1:
            return False
        if not color_is_black(img[by][bx + x]):
            return False

    # bottom
    for x in range(255):
        if by + 254 >= height - 1 or bx + 254 >= width - 1:
            return False
        if not color_is_black(img[by + 254][bx + x]):
            return False

    # left
    for y in range(255):
        if by + 254 >= height - 1 or bx >= width - 1:
            break
        if not color_is_black(img[by + y][bx]):
            return False

    # right
    for y in range(255):
        if by + 254 >= height - 1 or bx + 254 >= width - 1:
            return False
        if not color_is_black(img[by + y][bx + 254]):
            return False

    return True


def cut_image(mask, original):
    height, width, channels = original.shape

    chunk_coords = []
    for x in range(0, width, 50):
        print(x)
        for y in range(0, height, 50):
            if align_cut(mask, x, y):
                chunk_coords.append((x, y))

    print(chunk_coords)
    mask_chunks = [(x, y, cut_chunk(mask, x, y)) for (x, y) in chunk_coords]
    original_chunks = [(x, y, cut_chunk(original, x, y)) for (x, y) in chunk_coords]

    for (x, y, chunk) in mask_chunks:
        cv2.imwrite(f"out/{x}{y}_mask.png", chunk)

    for (x, y, chunk) in original_chunks:
        cv2.imwrite(f"out/{x}{y}_original.png", chunk)
