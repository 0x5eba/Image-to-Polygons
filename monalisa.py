from PIL import Image, ImageDraw
import numpy as np
import webbrowser
import threading
import multiprocessing.dummy as mp
import multiprocessing
import os.path
import copy
import sys
import math
import random

POPULATION = 1000
OFFSET = 0
DIMENSION = 30
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
            pdraw.polygon(array_point, fill=(color[0], color[1], color[2], color[3]))
            img2 = Image.alpha_composite(img2, draw)

        return img2

    def random_polygon(self):
        finish = []
        for polygon in self.polygons:
            if polygon.changeable is False:
                finish.append(polygon)
        if(len(finish) == len(self.polygons)):
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
        if rand <= 1:
            idx = random.randrange(0, 3)
            value = random.randrange(0, 256)
            color = list(self.color)
            color[idx] = value
            self.color = tuple(color)
        else:
            idx = random.randrange(0, len(self.points))
            point = tuple(generate_point(size))
            self.points[idx] = point
      

def fitness(img, draw_polygon, color, points):

    a = points[0]
    b = points[1]
    c = points[2]

    maxY = max(a[1], b[1], c[1])
    minY = min(a[1], b[1], c[1])
    minX = min(a[0], b[0], c[0])

    count = 0
    RGB_draw_polygon = np.zeros(3)
    RGB_img = np.zeros(3)
    rgb_draw = draw_polygon.convert('RGBA')
    rgb_img = img.convert('RGBA')


    for y in range(minY, img.size[1]):
        if y is maxY:
            break
        for x in range(minX, img.size[0]):
            if(x < 0 or y < 0):
                continue
            try:
                s = list([x, y])
                alpha = ((b[1] - c[1])*(s[0] - c[0]) + (c[0] - b[0])*(s[1] - c[1])) / ((b[1] - c[1])*(a[0] - c[0]) + (c[0] - b[0])*(a[1] - c[1]))
                beta = ((c[1] - a[1])*(s[0] - c[0]) + (a[0] - c[0])*(s[1] - c[1])) / ((b[1] - c[1])*(a[0] - c[0]) + (c[0] - b[0])*(a[1] - c[1]))
                gamma = 1.0 - alpha - beta
            except(ZeroDivisionError):
                continue
            if alpha>0 and beta>0 and gamma>0:
                RGB_draw_polygon[0] += rgb_draw.getpixel((x, y))[0]
                RGB_draw_polygon[1] += rgb_draw.getpixel((x, y))[1]
                RGB_draw_polygon[2] += rgb_draw.getpixel((x, y))[2]

                RGB_img[0] += rgb_img.getpixel((x, y))[0]
                RGB_img[1] += rgb_img.getpixel((x, y))[1]
                RGB_img[2] += rgb_img.getpixel((x, y))[2]

                count += 1

    if (count <= 0):
        return list([256, 256, 256]), 0

    fitness_draw = list([abs(int(RGB_img[0] / count) - int(RGB_draw_polygon[0] / count)),
                         abs(int(RGB_img[1] / count) - int(RGB_draw_polygon[1] / count)),
                         abs(int(RGB_img[2] / count) - int(RGB_draw_polygon[2] / count))])
    fitness_img = list([int(RGB_img[0]/count), int(RGB_img[1]/count), int(RGB_img[2]/count)])

    return fitness_draw, fitness_img

def generate_point(size_img):
    x = random.randrange(0 - OFFSET, size_img[0] + OFFSET)
    y = random.randrange(0 - OFFSET, size_img[1] + OFFSET)
    return tuple([x, y])


def my_draw(img, color, points):
    size = img.size
    img2 = Image.new('RGBA', size)
    draw = Image.new('RGBA', size)
    pdraw = ImageDraw.Draw(draw)

    array_point = []
    for point in points:
        array_point.append(tuple([point[0], point[1]]))
    pdraw.polygon(array_point, fill=(color[0], color[1], color[2], color[3]))
    img2 = Image.alpha_composite(img2, draw)
    return img2


def generate_dna(img):
    polygons = []
    parent = Image.new('RGBA', img.size)
    for i in range(POPULATION):
        points = []
        side_polygon = random.randint(MIN_SIDE_POLYGONS, MAX_SIDE_POLYGONS)
        randX = random.randrange(0 - OFFSET, img.size[0] + OFFSET)
        randY = random.randrange(0 - OFFSET, img.size[1] + OFFSET)
        for j in range(side_polygon):
            #point = tuple(list((random.randrange(0 - OFFSET, img.size[0] + OFFSET), random.randrange(0 - OFFSET, img.size[1] + OFFSET))))
            point = list((random.randrange(randX, randX + DIMENSION), random.randrange(randY, randY + DIMENSION)))
            while point[0] < 0:
                point[0] = random.randrange(randX, randX + DIMENSION)
            while point[1] < 0:
                point[1] = random.randrange(randX, randX + DIMENSION)
            point = tuple(point)
            points.append(point)

        color = tuple(list([random.randrange(0, 256) for _ in range(4)]))

        draw_polygon = my_draw(img, color, points)
        fitness_polygon, useless = fitness(img, draw_polygon, color, points)
        polygon = Polygons(points, color, fitness_polygon, True)

        parent = Image.alpha_composite(parent, draw_polygon)

        polygons.append(polygon)


    parent.save("pic.png", 'PNG')
    dna = DNA(img.size, polygons)
    return dna, parent


def main():
    url = "file.html"
    webbrowser.open(url)

    img = Image.open("small.jpe")
    dna, parent = generate_dna(img)

    generations = 0
    while True:

        random_poly, index_random_poly = dna.random_polygon() #parent
        fitness_parent = random_poly.fitness

        child = copy.deepcopy(random_poly)
        child.mutate_polygon(img.size)
        draw_child = my_draw(img, child.color, child.points)
        child.fitness, fitness_img = fitness(img, draw_child, child.color, child.points)
        fitness_child = child.fitness

        if(fitness_child[0] < fitness_parent[0] or fitness_child[1] < fitness_parent[1] or fitness_child[2] < fitness_parent[2]):
            dna.polygons[index_random_poly] = child
            parent = dna.draw()
            parent.save("pic.png", 'PNG')

            if(fitness_parent[0] < 5 and fitness_parent[1] < 5 and fitness_parent[2] < 5):
                dna.polygons[index_random_poly].changeable = False

        generations += 1

if __name__ == "__main__":
    main()
