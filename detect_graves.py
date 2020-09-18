import get_gravestone_masks as masking
import cv2
import argparse
import numpy as np
from pathlib import Path


def get_blobbiness(points):
    return 1 - count_edge_pixels(points) / len(points)


def if_no_set_overlap(s1, s2):
    s = s1 if len(s1) < len(s2) else s2
    so = s2 if len(s1) < len(s2) else s1
    for e in s:
        if e in so:
            return False
    return True


def flood_for_detection(x, y, threshold, visited):
    if (x, y) in visited:
        return {}, False
    points_to_visit = {(x, y)}
    return_list = set()

    visits = 0
    while len(points_to_visit) > 0:
        px, py = points_to_visit.pop()
        if (px, py) in visited:
            continue
        visits += 1
        # if visits % 100 == 0:cqc
        #     print(visits)
        if visits > 2000:
            return return_list, False
        if threshold((px, py)):
            visited.add((px, py))
            return_list.add((px, py))
            points_to_visit.add((px + 1, py))
            points_to_visit.add((px - 1, py))
            points_to_visit.add((px, py + 1))
            points_to_visit.add((px, py - 1))

    return return_list, True


def count_edge_pixels(points):
    edge_point_count = 0
    for (x, y) in points:
        if ((x + 1, y) in points) and ((x - 1, y) in points) and ((x, y + 1) in points) and ((x, y - 1) in points):
            edge_point_count += 1

    return edge_point_count


def detection_threshold(img, pixel, reference, allowed_color_diff, allowed_brightness_diff):
    x, y = pixel
    height, width, channels = img.shape
    if not (0 <= x < width and 0 <= y < height):
        return False

    color_diff = masking.get_color_diff(masking.get_scaled_color(img[y, x]), masking.get_scaled_color(reference))
    brightness_diff = abs(masking.get_brightness(img[y, x]) - masking.get_brightness(reference))

    normalized_color_diff = color_diff / allowed_color_diff
    normalized_brightness_diff = brightness_diff / allowed_brightness_diff
    return (normalized_color_diff + normalized_brightness_diff) < 2


def detect_graves_flood(img, reference_color, reference_area, reference_blobbiness):
    height, width, channels = img.shape
    visited = set()
    mask = []

    for x in range(0, width, 4):
        if x % 100 == 0:
            print(x/width)
        for y in range(0, height, 4):
            points, success = flood_for_detection(
                x, y, lambda pixel: detection_threshold(main_image, pixel, reference_color, 35, .25), visited
            )

            if not (reference_area * 0.6) < len(points) < (reference_area * 1.4):
                continue

            if not (reference_blobbiness * 0.7) < get_blobbiness(points) < (reference_blobbiness * 1.3):
                continue

            if success:
                mask.append(points)

    return mask


def detect_graves_straight(img, reference_color):
    height, width, channels = img.shape
    mask = set()

    for x in range(0, width, 4):
        if x % 100 == 0:
            print(x/width)
        for y in range(0, height, 4):
            if detection_threshold(main_image, (x, y), reference_color):
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if detection_threshold(main_image, (x + dx, y + dy), reference_color):
                            mask.add((x + dx, y + dy))
    return mask


def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        reference_color = main_image[y, x]
        points, success = flood_for_detection(
            x, y, lambda pixel: detection_threshold(main_image, pixel, reference_color, 35, .25), set()
        )
        for (px, py) in points:
            display_image[py][px] = (255, 0, 255)

        # i dont really have to precompute tbh
        reference_values.append((points, len(points), get_blobbiness(points)))


if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the image")
    args = vars(ap.parse_args())

    # load the image, clone it, and setup the mouse callback function
    main_image = cv2.imread(args["image"])
    display_image = cv2.imread(args["image"])
    main_height, main_width, main_channels = main_image.shape

    cv2.namedWindow("image")
    cv2.resizeWindow("image", 1280, 640)
    cv2.setMouseCallback("image", click)

    reference_values = []
    grave_points = set()
    graves = []

    while True:
        cv2.imshow("image", display_image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("z"):
            points, _, _ = reference_values.pop()
            for (x, y) in points:
                display_image[y][x] = main_image[y][x]
        if key == ord("c"):
            break
        if key == ord("q"):
            for reference_value in reference_values:
                reference_color = tuple(np.mean([main_image[y][x] for (x, y) in reference_value[0]], axis=0))
                grave_masks = detect_graves_flood(main_image, reference_color, reference_value[1], reference_value[2])
                total_mask = []
                for grave in grave_masks:
                    if if_no_set_overlap(grave, grave_points):
                        graves.append(grave)
                        total_mask += grave
                        grave_points.update(grave)

                for (x, y) in masking.add_border(total_mask, 2):
                    if not (0 <= x < main_width and 0 <= y < main_height):
                        continue
                    display_image[y][x] = (0, 255, 0)
            reference_values = []

        if key == ord("f"):
            path = Path(args["image"])
            print(f"writing out to {path.parent}/{path.stem}.txt")
            f = open(f"{path.parent}/{path.stem}.txt", "w")
            out_text = ""
            for grave in graves:
                max_x = max(grave, key=lambda t: t[0])[0] + 5
                min_x = min(grave, key=lambda t: t[0])[0] - 5
                max_y = max(grave, key=lambda t: t[1])[1] + 5
                min_y = min(grave, key=lambda t: t[1])[1] - 5

                width = max_x - min_x
                height = max_y - min_y

                x_pos = (max_x + min_x)/2
                y_pos = (max_y + min_y)/2

                out_text += f"0 {x_pos/main_width} {y_pos/main_height} {width/main_width} {height/main_height}\n"

            f.write(out_text)
            f.close()


#            for (x, y) in expanded_border:
#                if not (0 <= x < main_width and 0 <= y < main_height):
#                    continue
#                main_image[y][x] = (0, 255, 0)

    # close all open windows
    cv2.destroyAllWindows()
