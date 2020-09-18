import cv2
import argparse

from read_labels import read_labels
import os
import cut_image
from pathlib import Path


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

    return chunks, chunk_coords


def read_and_print_for_cut_image(img_path, label_path, scale):
    labels = read_labels(label_path)

    unscaled_image = cv2.imread(img_path)
    unscaled_height, unscaled_width, _ = unscaled_image.shape

    main_image = cv2.resize(unscaled_image,
                            (int(unscaled_width * float(scale)), int(unscaled_height * float(scale))))
    main_height, main_width, _ = main_image.shape

    bounding_boxes = [(px * main_width, py * main_height, w, h) for ((px, py), (w, h)) in labels]

    chunks, chunk_coords = cut_image_yolo(bounding_boxes, main_image)

    if not os.path.exists("out"):
        os.makedirs("out")

    img_name = Path(img_path).stem

    if not os.path.exists(f"out/{img_name}"):
        os.makedirs(f"out/{img_name}")

    for (x, y, chunk) in chunks:
        cv2.imwrite(f"out/{img_name}/{x}{y}_image.png", chunk)

    for (x, y) in chunk_coords:
        f = open(f"out/{img_name}/{x}{y}_image.txt", "w")
        out_text = ""
        for (px, py, w, h) in bounding_boxes:
            if x < px < x + 256 and y < py < y + 256:
                out_text += f"15 {(px - x) / 256} {(py - y) / 256} {w * main_width / 256} {h * main_height / 256}\n"

        f.write(out_text)
        f.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False, help="Path to the image")
    ap.add_argument("-f", "--folder", required=False, help="Path to the folder containing the images")
    ap.add_argument("-l", "--label", required=False, help="Path to the labels for the given image")
    ap.add_argument("-s", "--scale", required=False, help="Amount to scale output images", default=1)
    args = vars(ap.parse_args())

    if args["folder"] is not None:
        for filename in os.listdir(args["folder"]):
            path = Path(args["folder"] + "/" + filename)
            if path.suffix == ".png":
                read_and_print_for_cut_image(str(path), str(Path(args["folder"] + "/" + path.stem + ".txt")), args["scale"])

    if not (args["image"] is None or args["label"] is None):
        read_and_print_for_cut_image(args["image"], args["label"], args["scale"])

    print("please supply either folder or image argument")
    exit()
