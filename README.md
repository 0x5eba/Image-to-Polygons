# Genetic algorithm - Monalisa

From an image you can create the same image but formed of polygons.

You can do it in 2 ways, one with genetic algorithm, the other directly.

## Guide step-by-step

### Setup

To install the requirements:

`sudo pip install -r requirements.txt`

### Genetic algorithm

Use the file `giwga.py` like this:

`python giwga.py --population 1000 --dimension 30 --img="Image/monalisa.jpg"`

For more info run `python giwga.py`

**In Runtime** 

It will create an image, called pic.png, that is the representation in polygons of the original image

Also it will be open in the browser, that automatically refresh the image.

With Genetic algorithm it will take a lot of time to make and image similar to the original so **Use very small image**

### Image to Polygons

Use the file `giwga.py` like this:

`python giwp.py --number-polygons 1000 --dimension 30 --img="Image/monalisa.jpg"`

For more info run `python giwp.py`


## Results

Original image

<img src="https://github.com/0x5eba/Genetic_algorithm-Monalisa/blob/master/Image/monalisa.jpg" width="200" height="300">

Generated image with 50000 polygons of dimension 30

<img src="https://github.com/0x5eba/Genetic_algorithm-Monalisa/blob/master/Image/monalisa_30_50000.png" width="300" height="400">

Generated image with 10000 polygons of dimension 70

<img src="https://github.com/0x5eba/Genetic_algorithm-Monalisa/blob/master/Image/monalisa_70_10000.png" width="300" height="400">

