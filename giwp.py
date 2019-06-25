from PIL import Image, ImageDraw
import matplotlib.path as mplPath
import numpy as np
import webbrowser
import os.path
import copy
import sys
import random
import argparse

DIMENSION = 30
N = 1000

def fitness(img, points):
    a = points[0]
    b = points[1]
    c = points[2]

    maxY = max(a[1], b[1], c[1])
    maxX = max(a[0], b[0], c[0])
    minY = min(a[1], b[1], c[1])
    minX = min(a[0], b[0], c[0])

    minY = max(minY, 0)
    minX = max(minX, 0)
    maxY = min(maxY, img.size[1])
    maxX = min(maxX, img.size[0])

    bbPath = mplPath.Path(np.array(points))
    count = 0
    RGB_img = np.zeros(3)
    rgb_img = img.convert('RGBA')

    for y in range(minY, maxY):
        for x in range(minX, maxX):
            if (bbPath.contains_point((x, y))):
                rgb_img_tmp = rgb_img.getpixel((x, y))
                RGB_img[0] += rgb_img_tmp[0]
                RGB_img[1] += rgb_img_tmp[1]
                RGB_img[2] += rgb_img_tmp[2]

                count += 1

    if (count <= 0):
        return np.array([256, 256, 256])

    fitness_draw = np.array([int(RGB_img[0] / count),
                             int(RGB_img[1] / count),
                             int(RGB_img[2] / count)])
    return fitness_draw


def generate_point(size):
    point = np.array([[-1, -1], [-1, -1], [-1, -1]])
    
    while (point[0][0] < 0 or point[0][1] < 0 or point[1][0] < 0 or point[1][1] < 0 or point[2][0] < 0 or point[2][1] < 0):
        point[2] = list([random.randrange(0, size[0]), random.randrange(0, size[1])])
        rand = random.random()
        if (rand <= 0.25):
            point[0] = [point[2][0] - DIMENSION / 2,
                        random.randrange(point[2][1], point[2][1] + DIMENSION)]
            point[1] = [point[2][0] + DIMENSION / 2,
                        random.randrange(point[2][1], point[2][1] + DIMENSION)]
        elif (rand <= 0.50):
            point[0] = [random.randrange(
                point[2][0], point[2][0] + DIMENSION), point[2][1] - DIMENSION / 2]
            point[1] = [random.randrange(
                point[2][0], point[2][0] + DIMENSION), point[2][1] + DIMENSION / 2]
        elif (rand <= 0.75):
            point[0] = [point[2][0] - DIMENSION / 2,
                        random.randrange(point[2][1] - DIMENSION, point[2][1])]
            point[1] = [point[2][0] + DIMENSION / 2,
                        random.randrange(point[2][1] - DIMENSION, point[2][1])]
        elif (rand <= 1):
            point[0] = [random.randrange(
                point[2][0] - DIMENSION, point[2][0]), point[2][1] - DIMENSION / 2]
            point[1] = [random.randrange(
                point[2][0] - DIMENSION, point[2][0]), point[2][1] + DIMENSION / 2]
    return point


def my_draw(img, color, points, fitness):
    size = img.size
    img2 = Image.new('RGBA', size)
    draw = Image.new('RGBA', size)
    pdraw = ImageDraw.Draw(draw)

    array_point = []
    for point in points:
        array_point.append(tuple([point[0], point[1]]))
    pdraw.polygon(array_point, fill=(color[0], color[1], color[2], fitness))
    img2 = Image.alpha_composite(img2, draw)
    return img2


def generate_img(img):
    polygons = []
    parent = Image.new('RGBA', img.size)
   
    for i in range(N):
        points = generate_point(img.size)
        color = fitness(img, points)
        polygons.append((color, points))

        # parent = Image.alpha_composite(parent, draw_polygon)
        # parent.save("pic.png", 'PNG')

    for polygon in polygons:
        draw_polygon = my_draw(img, polygon[0], polygon[1], 100)
        parent = Image.alpha_composite(parent, draw_polygon)
    
    parent.save("pic.png", 'PNG')


def main(argv):
    path = os.getcwd()

    if not os.path.exists(path + "/file.html"):
        print("\nPut the \".html\" here: " + path)
        sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('--number-polygons', type=int, default=1000, metavar='N',
                        help='number of polygons to use (default: 1000)')
    parser.add_argument('--img', type=str, default="Image/image.png",
                        help='the image to use for the generation of polygons')
    parser.add_argument('--dimension', type=int, default=30, metavar='N',
                        help='size of a single polygon (default: 30)')
    args = parser.parse_args()
    
    global N, DIMENSION
    N = args.number_polygons
    DIMENSION = args.dimension

    # open image
    img = Image.open(path + "/" + args.img)

    # generate the image with polygons
    generate_img(img)

    # open a web page with the image that refresh every second
    webbrowser.open(path + "/file.html")


if __name__ == "__main__":
    main(sys.argv)
