import argparse
import cv2


# gets the brightness of a color from 0-1
def get_brightness(color):
    return (float(color[0]) + float(color[1]) + float(color[2])) / (3 * 255)


# this gets the "color" of the pixel, ignoring the shade.
# so dark and light shades of a single color will be considered the same
def get_scaled_color(color):
    brightness = get_brightness(color) + 0.001
    return color[0] / brightness, color[1] / brightness, color[2] / brightness


# gets the difference of the colors piecewise and sums them together
def get_color_diff(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


# weights and sums the brightness and color difference of two pixels and returns if it is within a threshold
def color_threshold(img, pixel, reference):
    x, y = pixel
    height, width, channels = img.shape
    if not (0 <= x < width and 0 <= y < height):
        return False

    color_diff = get_color_diff(get_scaled_color(img[y, x]), get_scaled_color(reference))
    brightness_diff = abs(get_brightness(img[y, x]) - get_brightness(reference))
    # laplacian_brightness = get_brightness(blurred_laplacian[y, x])

    normalized_color_diff = color_diff / 35
    normalized_brightness_diff = brightness_diff / .2
    # normalized_laplacian_brightness = (1 - laplacian_brightness)/.8

    # print(normalized_color_diff, normalized_brightness_diff)

    # sum the normalized values and avg them to allow for leeway if one is especially appropriate
    return (normalized_color_diff + normalized_brightness_diff) < 2


# removes the border pixels on a set of xy coordinates
# recurses size times to remove a border of that width
def remove_border(pixels, size):
    returned_pixels = set()
    for (x, y) in pixels:
        if ((x + 1, y) in pixels) and ((x - 1, y) in pixels) and ((x, y + 1) in pixels) and ((x, y - 1) in pixels):
            returned_pixels.add((x, y))

    if size <= 1:
        return returned_pixels
    else:
        return remove_border(returned_pixels, size - 1)


# for each coordinate in set pixels, creates a 3x3 block of pixels and adds them to the result
# recurses size times for a border of size pixels
def add_border(pixels, size):
    returned_pixels = set()
    for (x, y) in pixels:
        returned_pixels.add((x - 1, y - 1))
        returned_pixels.add((x - 1, y + 1))
        returned_pixels.add((x + 1, y - 1))
        returned_pixels.add((x + 1, y + 1))

    if size <= 1:
        return returned_pixels
    else:
        return add_border(returned_pixels, size - 1)


def get_gravestone_mask(img, coord):
    x, y = coord
    reference_color = img[y, x]
    points = flood_for_threshold_nonrecursive(
        x, y, lambda pixel: color_threshold(img, pixel, reference_color), set()
    )

    remove_width = int(len(points) / 75)
    thin_border = remove_border(points, remove_width)

    expand_width = int(len(points) / 50)
    expanded_border = add_border(thin_border, expand_width)

    return expanded_border


def get_gravestone_masks(img, coords):
    masks = []
    for coord in coords:
        masks.extend(get_gravestone_mask(img, coord))

    return masks


# floods out and gets all pixels that are accepted by predicate threshold
def flood_for_threshold(x, y, threshold, visited):
    print(len(visited))
    if len(visited) > 900:
        return []
    if (x, y) in visited:
        return []
    if threshold((x, y)):
        visited.add((x, y))
        return_list = [(x, y)]
        return_list += flood_for_threshold(x + 1, y, threshold, visited)
        return_list += flood_for_threshold(x - 1, y, threshold, visited)
        return_list += flood_for_threshold(x, y + 1, threshold, visited)
        return_list += flood_for_threshold(x, y - 1, threshold, visited)
        return return_list
    else:
        return []


def flood_for_threshold_nonrecursive(x, y, threshold, visited):
    visited = set()
    points_to_visit = {(x, y)}
    return_list = set()

    visits = 0
    while len(points_to_visit) > 0:
        px, py = points_to_visit.pop()
        if (px, py) in visited:
            continue
        visits += 1
        if visits % 100 == 0:
            print(visits)
        if visits > 2000:
            return return_list
        if threshold((px, py)):
            visited.add((px, py))
            return_list.add((px, py))
            points_to_visit.add((px + 1, py))
            points_to_visit.add((px - 1, py))
            points_to_visit.add((px, py + 1))
            points_to_visit.add((px, py - 1))

    return return_list


# receives a click event and gets all adjacent pixels flooding out of the same shade, ignoring darkness
# then removes 1% of the pixels as a border to remove any noise on the edges to get the main core of the block
# then adds that amount as a border to restore the size
def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points = get_gravestone_mask(main_image, (x, y))
        for (x, y) in points:
            main_image[y][x] = (0, 255, 0)


if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the image")
    args = vars(ap.parse_args())

    # load the image, clone it, and setup the mouse callback function
    main_image = cv2.imread(args["image"])
    edges = cv2.Canny(main_image, 60, 120)

    laplacian = cv2.Laplacian(main_image, cv2.CV_64F)
    blurred_laplacian = cv2.GaussianBlur(laplacian, (5, 5), 0)

    clone = main_image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click)

    # keep looping until the 'c' key is pressed
    while True:
        # cv2.imshow("edge", edges)
        cv2.imshow("image", main_image)
        # cv2.imshow("lap", blurred_laplacian)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c"):
            break

    # close all open windows
    cv2.destroyAllWindows()
