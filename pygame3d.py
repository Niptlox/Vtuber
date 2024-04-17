import math
import time
from typing import NamedTuple, List

import pygame as pg
import numpy as np
from pygame import Surface, Color

DEFAULT_COLOR = "blue"


class Object3(NamedTuple):
    points: list
    joins: list
    color: Color


class Camera:
    def __init__(self):
        self.size = 0, 0
        self.position = np.array((0, 0, -2))
        self.focus = 200

    def draw_objects(self, surface: Surface, objects: List[list | Object3]):
        self.size = surface.get_size()
        for obj in objects:
            if isinstance(obj, Object3):
                points = obj.points
                color = obj.color
            else:
                points = obj
                color = DEFAULT_COLOR
            points2 = [self.point3to2(p3) for p3 in points]
            lp = None
            for p2 in points2:
                if p2:
                    pg.draw.circle(surface, color, p2, radius=2)
                    if lp:
                        pg.draw.line(surface, color, p2, lp)
                lp = p2
                # break

    def point3to2(self, p3):
        x, y, z = p3
        cx, cy, cz = self.position
        dist = z - cz
        k = self.focus / dist
        return x * k + self.size[0] / 2, y * k + self.size[1] / 2


def rotate(points: list, angle: List):
    ax, ay, az = angle
    if ax:
        matrix = ([[1, 0, 0], [0, math.cos(ax), math.sin(ax)], [0, -math.sin(ax), math.cos(ax)]])
        points = np.dot(points, matrix)
    if ay:
        matrix = ([[math.cos(ay), 0, -math.sin(ay)], [0, 1, 0], [math.sin(ay), 0, math.cos(ay)], ])
        points = np.dot(points, matrix)
    if az:
        matrix = ([[math.cos(az), math.sin(az), 0], [-math.sin(az), math.cos(az), 0], [0, 0, 1]])
        points = np.dot(points, matrix)
    return points


def move(points, vec):
    return np.array([p + vec for p in points])


if __name__ == '__main__':
    screen = pg.display.set_mode((780, 420))
    cube = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)])
    cube = move(cube, np.array((-0.5, -0.5, -0.5)))
    cam = Camera()
    running = True
    while running:
        [exit() for event in pg.event.get(pg.QUIT)]
        screen.fill("black")
        cam.draw_objects(screen, [cube])
        cube = rotate(cube, (0.1, 0.1, 0))
        time.sleep(0.1)
        pg.display.flip()
