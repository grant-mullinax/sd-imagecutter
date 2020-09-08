import cv2
import numpy as np


def mask_to_img(coords, width, height, background=None):
    if background is None:
        background = np.zeros((height, width, 3), np.uint8)

    for x, y in coords:
        background[y, x] = (0, 255, 0)

    return background


def display_image(name, img):
    while True:
        cv2.imshow(name, img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            break
