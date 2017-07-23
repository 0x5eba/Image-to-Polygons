from PIL import Image, ImageDraw
import numpy as np
import webbrowser
import os.path
import copy
import sys
import random


POPULATION = 0
DIMENSION = 0
MIN_SIDE_POLYGONS = 3
MAX_SIDE_POLYGONS = 3


class DNA(object):
    def __init__(self, _img_size, _polygons):
        self.polygons = _polygons
        self.size_img = _img_size

    def draw(self):
        size = self.size_img
        img2 = Image.new('RGBA', size)
        draw = Image.new('RGBA', size)
        pdraw = ImageDraw.Draw(draw)
        for polygon in self.polygons:
            color = polygon.color
            array_point = []
            for point in polygon.points:
                array_point.append(tuple([point[0], point[1]]))
            pdraw.polygon(array_point, fill=(color[0], color[1], color[2]))
            # img2.paste(draw, mask=draw)
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
            # idx = random.randrange(0, 3)
            value = random.randrange(0, 256)
            color = np.array(self.color)
            color[idx] = value
            self.color = tuple(color)
            return False
        else:
            self.points = generate_point(size)
            return True


def fitness(img, draw_polygon, color, points):
    a = points[0]
    b = points[1]
    c = points[2]

    '''
    problema con l'OFFSET perchè va anche in negativo
    probabilmente una soluzione è mettere a 0 se è negativo ma non funziona molto 
    '''
    maxY = max(a[1], b[1], c[1])
    minY = min(a[1], b[1], c[1])
    minX = min(a[0], b[0], c[0])

    count = 0
    calculate_color_polygon = False
    RGB_draw_polygon = np.zeros(3)
    RGB_img = np.zeros(3)
    rgb_draw = draw_polygon.convert('RGBA')
    rgb_img = img.convert('RGBA')

    for y in range(minY, img.size[1]):
        if y is maxY:
            break
        for x in range(minX, img.size[0]):
            if (x < 0 or y < 0):
                continue
            try:
                s = np.array([x, y])
                alpha = ((b[1] - c[1]) * (s[0] - c[0]) + (c[0] - b[0]) * (s[1] - c[1])) / (
                    (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1]))
                beta = ((c[1] - a[1]) * (s[0] - c[0]) + (a[0] - c[0]) * (s[1] - c[1])) / (
                    (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1]))
                gamma = 1.0 - alpha - beta
            except(ZeroDivisionError):
                continue
            if alpha > 0 and beta > 0 and gamma > 0:
                if (calculate_color_polygon is False):
                    RGB_draw_polygon[0] = rgb_draw.getpixel((x, y))[0]
                    RGB_draw_polygon[1] = rgb_draw.getpixel((x, y))[1]
                    RGB_draw_polygon[2] = rgb_draw.getpixel((x, y))[2]
                    calculate_color_polygon = True

                RGB_img[0] += rgb_img.getpixel((x, y))[0]
                RGB_img[1] += rgb_img.getpixel((x, y))[1]
                RGB_img[2] += rgb_img.getpixel((x, y))[2]

                count += 1

    if (count <= 0):
        return np.array([256, 256, 256])

    # fitness_return = np.array([int(RGB_img[0]/count), int(RGB_img[1]/count), int(RGB_img[2]/count)])

    fitness_draw = np.array([abs(int(RGB_img[0] / count) - RGB_draw_polygon[0]),
                             abs(int(RGB_img[1] / count) - RGB_draw_polygon[1]),
                             abs(int(RGB_img[2] / count) - RGB_draw_polygon[2])])

    # fitness_draw = np.array([int(RGB_img[0] / count), int(RGB_img[1] / count), int(RGB_img[2] / count)])

    return fitness_draw


def generate_point(size):
    point = np.array([[-1, -1], [-1, -1], [-1, -1]])
    while (point[0][0] < 0 or point[0][1] < 0 or point[1][0] < 0 or point[1][1] < 0 or point[2][0] < 0 or point[2][
        1] < 0):
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


def my_draw(img, color, points):
    size = img.size
    img2 = Image.new('RGBA', size)
    draw = Image.new('RGBA', size)
    pdraw = ImageDraw.Draw(draw)

    array_point = []
    for point in points:
        array_point.append(tuple([point[0], point[1]]))
    pdraw.polygon(array_point, fill=(color[0], color[1], color[2]))
    # img2.paste(draw, mask=draw)
    img2 = Image.alpha_composite(img2, draw)
    return img2


def generate_dna(img):
    polygons = []
    parent = Image.new('RGBA', img.size)
    for i in range(POPULATION):
        # side_polygon = random.randrange(MIN_SIDE_POLYGONS, MAX_SIDE_POLYGONS)
        # randX = random.randrange(0 - OFFSET, img.size[0] + OFFSET)
        # randY = random.randrange(0 - OFFSET, img.size[1] + OFFSET)
        # for j in range(side_polygon):
        #     point = generate_point(img.size, randX, randY)
        #     points.append(point)

        points = generate_point(img.size)
        color = tuple(np.array([random.randrange(0, 256) for _ in range(4)]))

        draw_polygon = my_draw(img, color, points)
        fitness_polygon = fitness(img, draw_polygon, color, points)
        polygon = Polygons(points, color, fitness_polygon, True)

        parent = Image.alpha_composite(parent, draw_polygon)
        # parent.paste(draw_polygon, mask=draw_polygon)

        polygons.append(polygon)

        parent.save("pic.png", 'PNG')
    dna = DNA(img.size, polygons)
    return dna, parent


def fitness_calculation(dna):
    tot_fitness = 0
    for polygon in dna.polygons:
        tot_fitness += (polygon.fitness[0] + polygon.fitness[1] + polygon.fitness[2])

    print("Fitness: ", "{0:.2f}".format((100 * POPULATION / tot_fitness) * 100))
    # print("Fitness: ", tot_fitness)


def main():
    # open a web page with the image that refresh every second
    url = "file.html"
    webbrowser.open(url)

    # open image
    img = Image.open("monalisaFace.jpg")

    # find the best population based on the given image
    # 300 : 25600 = x : img.size[0]*img.size[1]
    global POPULATION
    POPULATION = int((img.size[0] * img.size[1]) * 300 / 25600)
    global DIMENSION
    DIMENSION = int(POPULATION / 10) / 2

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
        point_modify = child.mutate_polygon(img.size)
        draw_child = my_draw(img, child.color, child.points)
        # # if want to modify a point of a polygon
        # if (point_modify):
        #     parent_copy = copy.deepcopy(child)
        #     parent_copy.fitness = fitness(img, draw_child, parent_copy.color, parent_copy.points)
        #     fitness_parent = parent_copy.fitness
        # # if want to modify a color of a polygon
        # else:
        #     child.fitness = fitness(img, draw_child, child.color, child.points)
        child.fitness = fitness(img, draw_child, child.color, child.points)
        fitness_child = child.fitness

        # compare the new one created ( child ) with the older one ( parent )
        # if the child is better ( in terms of fitness ) will change the parent with the child
        if (fitness_child[0] <= fitness_parent[0] and fitness_child[1] <= fitness_parent[1] and fitness_child[2] <=
            fitness_parent[2]):
            # if (point_modify):
            #     dna.polygons[index_random_poly] = parent_copy
            # else:
            #     dna.polygons[index_random_poly] = child
            dna.polygons[index_random_poly] = child
            parent = dna.draw()
            parent.save("pic.png", 'PNG')

            # if its fitness is enough good will block the polygon to not change anymore
            if (fitness_child[0] < 2 and fitness_child[1] < 2 and fitness_child[2] < 2):
                dna.polygons[index_random_poly].changeable = False

            # print the percentage of the total fitness
            fitness_calculation(dna)
            print(f"generation: {generations}")
        generations += 1


if __name__ == "__main__":
    # main(sys.argv)
    main()
