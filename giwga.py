from PIL import Image, ImageDraw
import matplotlib.path as mplPath
import numpy as np
import webbrowser
import os.path
import copy
import sys
import random
import argparse

POPULATION = 500
DIMENSION = 30

class DNA(object):
    def __init__(self, _img_size, _polygons):
        self.polygons = _polygons
        self.size_img = _img_size

    def draw(self, alpha):
        size = self.size_img
        img2 = Image.new('RGBA', size)
        draw = Image.new('RGBA', size)
        pdraw = ImageDraw.Draw(draw)
        
        for polygon in self.polygons:
            color = polygon.color
            array_point = []
            for point in polygon.points:
                array_point.append(tuple([point[0], point[1]]))
            pdraw.polygon(array_point, fill=(color[0], color[1], color[2], alpha))
            img2 = Image.alpha_composite(img2, draw)

        return img2

    def random_polygon(self):
        finish = []
        for polygon in self.polygons:
            if polygon.changeable is False:
                finish.append(polygon)
        if (len(finish) == len(self.polygons)):
            print("\n\nFinished\n\n")
            sys.exit()

        rand = random.randrange(0, len(self.polygons))
        while self.polygons[rand].changeable is False:
            rand = random.randrange(0, len(self.polygons))
        random_poly = self.polygons[rand]
        
        return random_poly, rand


class Polygons(object):
    def __init__(self, _points, _color, _fitness, _changeable):
        self.points = _points
        self.color = _color
        self.fitness = _fitness
        self.changeable = _changeable

    def mutate_polygon(self, size):
        rand = random.random()
        if rand <= 0.5:
            if (self.fitness[0] > self.fitness[1] and self.fitness[0] > self.fitness[2]):
                idx = 0
            elif (self.fitness[1] > self.fitness[0] and self.fitness[1] > self.fitness[2]):
                idx = 1
            else:
                idx = 2
            value = random.randrange(0, 256)
            color = np.array(self.color)
            color[idx] = value
            self.color = tuple(color)
            return False
        else:
            self.points = generate_point(size)
            return True


def fitness(img, draw_polygon, points):
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
    calculate_color_polygon = False
    RGB_draw_polygon = np.zeros(3)
    rgb_img = img.convert('RGBA')
    rgb_draw = draw_polygon.convert('RGBA')

    for y in range(minY, maxY):
        for x in range(minX, maxX):
            if (bbPath.contains_point((x, y))):
                if (calculate_color_polygon is False):
                    RGB_draw_polygon = list(rgb_draw.getpixel((x, y)))
                    calculate_color_polygon = True

                RGB_img[0] += rgb_img.getpixel((x, y))[0]
                RGB_img[1] += rgb_img.getpixel((x, y))[1]
                RGB_img[2] += rgb_img.getpixel((x, y))[2]

                count += 1

    if (count <= 0):
        return np.array([256, 256, 256])

    fitness_draw = np.array([abs(int(RGB_img[0] / count) - RGB_draw_polygon[0]),
                            abs(int(RGB_img[1] / count) - RGB_draw_polygon[1]),
                            abs(int(RGB_img[2] / count) - RGB_draw_polygon[2])])
    return fitness_draw

def generate_point(size):
    point = np.array([[-1, -1], [-1, -1], [-1, -1]])
    while (point[0][0] < 0 or point[0][1] < 0 or point[1][0] < 0 
            or point[1][1] < 0 or point[2][0] < 0 or point[2][1] < 0):
        point[2] = list([random.randrange(0, size[0]), random.randrange(0, size[1])])
        rand = random.random()
        if (rand <= 0.25):
            point[0] = [point[2][0] - DIMENSION / 2, random.randrange(point[2][1], point[2][1] + DIMENSION)]
            point[1] = [point[2][0] + DIMENSION / 2, random.randrange(point[2][1], point[2][1] + DIMENSION)]
        elif (rand <= 0.50):
            point[0] = [random.randrange(point[2][0], point[2][0] + DIMENSION), point[2][1] - DIMENSION / 2]
            point[1] = [random.randrange(point[2][0], point[2][0] + DIMENSION), point[2][1] + DIMENSION / 2]
        elif (rand <= 0.75):
            point[0] = [point[2][0] - DIMENSION / 2, random.randrange(point[2][1] - DIMENSION, point[2][1])]
            point[1] = [point[2][0] + DIMENSION / 2, random.randrange(point[2][1] - DIMENSION, point[2][1])]
        elif (rand <= 1):
            point[0] = [random.randrange(point[2][0] - DIMENSION, point[2][0]), point[2][1] - DIMENSION / 2]
            point[1] = [random.randrange(point[2][0] - DIMENSION, point[2][0]), point[2][1] + DIMENSION / 2]
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


def generate_dna(img):
    polygons = []
    parent = Image.new('RGBA', img.size)
    for i in range(POPULATION):
        points = generate_point(img.size)
        color = tuple(np.array([random.randrange(0, 256) for _ in range(4)]))

        draw_polygon = my_draw(img, color, points, 50)
        fitness_polygon = fitness(img, draw_polygon, points)
        polygon = Polygons(points, color, fitness_polygon, True)

        parent = Image.alpha_composite(parent, draw_polygon)

        polygons.append(polygon)

        parent.save("pic.png", 'PNG')
    dna = DNA(img.size, polygons)
    return dna, parent


def crossover(fitness_child, fitness_parent, dna, parent, child, index_random_poly, generations):
    if (fitness_child[0] <= fitness_parent[0] and fitness_child[1] <= fitness_parent[1] 
            and fitness_child[2] <= fitness_parent[2]):

        # change color alpha of the polygon
        if(fitness_child.sum() > 200):
            alpha = 30
        else:
            alpha = int(150*(1-fitness_child.sum()/200))

        dna.polygons[index_random_poly] = child
        parent = dna.draw(alpha)
        parent.save("pic.png", 'PNG')

        # if its fitness is enough good will block the polygon to not change anymore
        if (fitness_child[0] < 2 and fitness_child[1] < 2 and fitness_child[2] < 2):
            dna.polygons[index_random_poly].changeable = False
            
        print(f"generation: {generations}\n")


def main(argv):
    path = os.getcwd()

    if not os.path.exists(path + "/file.html"):
        print("\nPut the \".html\" here: " + path)
        sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('--population', type=int, default=500, metavar='N',
                        help='number of population to use (default: 500)')
    parser.add_argument('--img', type=str, default="Image/image.png",
                        help='the image to use for the generation of polygons')
    parser.add_argument('--dimension', type=int, default=30, metavar='N',
                        help='size of a single polygon (default: 30)')
    args = parser.parse_args()

    global POPULATION, DIMENSION
    POPULATION = args.population
    DIMENSION = args.dimension

    # open image
    img = Image.open(path + "/" + args.img)

    # generate the image with polygons
    generate_dna(img)

    # open a web page with the image that refresh every second
    webbrowser.open(path + "/file.html")

    # create the dna with N polygon, where N is POPULATION
    dna, parent = generate_dna(img)

    generations = 0
    while True:
        # choose a random polygon
        random_poly, index_random_poly = dna.random_polygon()

        # make a copy of the parent, that will use if it decide to change the dimension
        # parent_copy = copy.deepcopy(random_poly)
        fitness_parent = random_poly.fitness

        # make a copy of parent that will modify
        child = copy.deepcopy(random_poly)
        # mutate or colors or points
        child.mutate_polygon(img.size)
        draw_child = my_draw(img, child.color, child.points, 0)

        # calculate the fitness for the child that has been mutate
        child.fitness = fitness(img, draw_child, child.points)
        fitness_child = child.fitness

        # compare the new one created ( child ) with the older one ( parent )
        # if the child is better ( in terms of fitness ) will change the parent with the child
        crossover(fitness_child, fitness_parent, dna, parent, child, index_random_poly, generations)
        generations += 1


if __name__ == "__main__":
    main(sys.argv)
