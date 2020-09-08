import cv2

from read_labels import read_labels
from get_gravestone_masks import get_gravestone_masks
from mask_to_img import mask_to_img
from mask_to_img import display_image
from cut_image import cut_image

if __name__ == '__main__':
    labels = read_labels("graves_labels.txt")

    image = cv2.imread("graves.png")
    height, width, channels = image.shape

    center_points = [(int(px * width), int(py * height)) for ((px, py), (w, h)) in labels]

    print(center_points)

    mask = get_gravestone_masks(image, center_points)
    mask_img = mask_to_img(mask, width, height, cv2.imread("graves.png"))

    # print(mask)
    # display_image("mask", mask_img)

    cut_image(mask_img)


