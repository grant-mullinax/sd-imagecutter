import cv2
import argparse

from read_labels import read_labels
import os
import cut_image


def cut_image_yolo(boxes, img):
    height, width, channels = img.shape

    chunk_coords = []
    for x in range(0, width - 256, 256):
        for y in range(0, height - 256, 256):
            # for chunk aligning
            chunk_coords.append((x, y))

    chunks = [(x, y, cut_image.cut_chunk(img, x, y)) for (x, y) in chunk_coords]

    if not os.path.exists("out"):
        os.makedirs("out")

    for (x, y) in chunk_coords:
        f = open(f"out/{x}{y}_image.txt", "w")
        out_text = ""
        for (px, py, w, h) in boxes:
            if x < px < x + 256 and y < py < y + 256:
                out_text += f"15 {(px - x) / 256} {(py - y) / 256} {w * width / 256} {h * width / 256}\n"

        f.write(out_text)
        f.close()

    for (x, y, chunk) in chunks:
        cv2.imwrite(f"out/{x}{y}_image.png", chunk)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the image")
    ap.add_argument("-l", "--label", required=True, help="Path to the labels for the given image")
    ap.add_argument("-s", "--scale", required=False, help="Amount to scale output images", default=1)
    args = vars(ap.parse_args())

    labels = read_labels(args["label"])

    unscaled_image = cv2.imread(args["image"])
    unscaled_height, unscaled_width, _ = unscaled_image.shape

    main_image = cv2.resize(unscaled_image,
                            (int(unscaled_width * float(args["scale"])), int(unscaled_height * float(args["scale"]))))
    main_height, main_width, _ = main_image.shape

    bounding_boxes = [(px * main_width, py * main_height, w, h) for ((px, py), (w, h)) in labels]

    # print(mask)
    # display_image("mask", mask_img)

    cut_image_yolo(bounding_boxes, main_image)
