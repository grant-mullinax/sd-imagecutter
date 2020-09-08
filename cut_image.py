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
            break
        if not color_is_black(img[by][bx + x]):
            return align_cut(img, bx, by + 1)

    # bottom
    for x in range(255):
        if by + 254 >= height - 1 or bx + 254 >= width - 1:
            break
        if not color_is_black(img[by + 254][bx + x]):
            return align_cut(img, bx, by - 1)

    # left
    for y in range(255):
        if by + 254 >= height - 1 or bx >= width - 1:
            break
        if not color_is_black(img[by + y][bx]):
            return align_cut(img, bx + 1, by)

    # right
    for y in range(255):
        if by + 254 >= height - 1 or bx + 254 >= width - 1:
            break
        if not color_is_black(img[by + y][bx + 254]):
            return align_cut(img, bx - 1, by)

    return bx, by


def cut_image(img):
    height, width, channels = img.shape
    h_cuts = math.floor(width / 255)
    v_cuts = math.floor(height / 255)

    chunk_coords = [align_cut(img, x * 255, y * 255) for x in range(h_cuts) for y in range(v_cuts)]

    print(chunk_coords)
    chunks = [(x, y, cut_chunk(img, x, y)) for (x, y) in chunk_coords]

    for (x, y, chunk) in chunks:
        cv2.imwrite(f"out/{x}{y}.png", chunk)
